#pragma once
#include <utility>
#include <vector>
#include <algorithm>
#include <random>
#include <iostream>
#include "Matrix.h"
#include "GroupEvaluation.h"
#include "ParallelExecution.h"

class GroupSearch
{
public:
	GroupSearch(int n_groups, int n_users, std::vector<int> foreigners = {}, std::vector<double> alphas = {})
		: gval(n_groups, n_users, std::move(foreigners), std::move(alphas)),
	      groups(n_groups),
	      days_init(n_groups, n_users)
	{
		for (int i = 0; i < this->groups.size(); ++i)
		{
			this->groups[i] = i;
		}

		this->n_seeds = 24;
		this->n_iterations = n_users * 2;

		// First "equal" allocation is used as starting point
		std::valarray<int> first_day(n_users);
		for (size_t i = 0; i < first_day.size(); ++i)
		{
			first_day[i] = i % n_groups;
		}
		std::sort(std::begin(first_day), std::end(first_day));

		days_init.row(0) = first_day;
		for (size_t row = 1; row < days_init.rows; ++row)
		{
			std::valarray<int> prev_day = days_init.row(row - 1);
			const std::valarray<int> next_day = (prev_day + 1) % n_groups;
			days_init.row(row) = next_day;
		}
	}

	Matrix<int> find_best_allocation()
	{
		struct Result
		{
			Matrix<int> allocation;
			double error;

			Result() = default;
			Result(Matrix<int> allocation, const double error)
				: allocation(std::move(allocation)),
				  error(error)
			{}
		};
		std::vector<Result> results(n_seeds);

#ifndef PRINT_NO_PROGRESS
		int total = n_iterations * n_seeds;// TODO: int or double?
		int counter = 0;
#endif

		ParallelExecution pe(6);
		pe.parallel_for(0, n_seeds - 1, [&](const size_t seed)
		{
			std::mt19937_64 generator(seed);
			const std::uniform_int_distribution<> user_generator(0, days_init.columns - 1);

			Matrix<int> days(days_init);
			if (seed > 0)
			{
				random_shuffle(days, seed);
			}

			double error = gval.error_total(days);
			std::valarray<int> current_groups = groups;

			for (int t = 0; t < n_iterations; ++t)
			{
				const size_t idx_user = user_generator(generator);
				do {
					const std::valarray<int> column_copy = days.column(idx_user);
					days.column(idx_user) = current_groups;

					const double error_new = gval.error_total(days);
					if (error_new < error)
					{
						error = error_new;
					}
					else
					{
						days.column(idx_user) = column_copy;
					}
				} while (std::next_permutation(std::begin(current_groups), std::end(current_groups)));

#ifndef PRINT_NO_PROGRESS
				pe.setResult([&]()
				{
					counter++;
					std::cout << static_cast<double>(counter) / total << std::endl;
				});
#endif
			}

			results[seed] = Result(days, error);
		});

		return std::min_element(results.begin(), results.end(), [](const Result& r1, const Result& r2)
		{
			return r1.error < r2.error;
		})->allocation;
	}

private:
	void random_shuffle(Matrix<int>& days, int seed) const
	{
		std::mt19937_64 generator(seed);
		const std::uniform_int_distribution<> row_generator(0, days.rows - 1);

		for (size_t i = 0; i < days.data.size(); ++i)
		{
			const size_t row = row_generator(generator);
			const size_t column = i % days.columns;
			std::swap(days.data[i], days(row, column));
		}
	}
	
private:
	GroupEvaluation gval;
	std::valarray<int> groups;
	Matrix<int> days_init;
	int n_seeds;
	int n_iterations;
};
