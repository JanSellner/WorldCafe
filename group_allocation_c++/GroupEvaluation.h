#pragma once
#include <vector>
#include <valarray>
#include <numeric>
#include <unordered_set>
#include "Matrix.h"

using uchar = unsigned char;

class GroupEvaluation
{
public:
	GroupEvaluation(const int n_groups, const int n_users, std::vector<int> foreigners = {}, std::vector<double> alphas = {})
		: n_groups(n_groups),
	      n_days(n_groups),
	      n_users(n_users),
	      foreigners(std::move(foreigners)),
	      alphas(std::move(alphas))
	{
		if (this->alphas.empty())
		{
			const int n_alphas = this->foreigners.empty() ? 2 : 3;
			this->alphas = std::vector<double>(n_alphas, 1.0 / n_alphas);
		}
	}

	double error_group_sizes(const Matrix<int>& days) const
	{
		Matrix<int> counts(n_days, n_groups);
		for (size_t day = 0; day < days.rows; ++day)
		{
			for (size_t user = 0; user < days.columns; ++user)
			{
				const int group = days(day, user);
				counts(day, group)++;
			}
		}
		
		std::valarray<double> normalized_counts(counts.data.size());
		double mean = 0.0;
		double mean_abs = 0.0;

		// We can calculate both means in the same loop
		for (size_t i = 0; i < counts.data.size(); ++i)
		{
			const double normalized = counts.data[i] / (static_cast<double>(n_users) / n_groups);
			normalized_counts[i] = normalized;	// Required for the variance calculation later

			mean += normalized;
			mean_abs += std::abs(normalized - 1);
		}

		const size_t size = normalized_counts.size();
		mean /= size;
		mean_abs /= size;

		const double std = std::sqrt(std::accumulate(std::begin(normalized_counts), std::end(normalized_counts), 0.0, [&mean, size](const double accumulator, const double val)
		{
			return accumulator + (val - mean) * (val - mean) / (size - 1);
		}));

		return mean_abs + std;
	}

	double error_meetings(const Matrix<int>& days) const
	{
		std::valarray<double> meetings(0.0, n_users);

		for (size_t current_user = 0; current_user < meetings.size(); ++current_user)
		{
			std::unordered_set<size_t> indices;

			for (size_t day = 0; day < days.rows; ++day)
			{
				for (size_t other_user = 0; other_user < days.columns; ++other_user)
				{
					if (days(day, current_user) == days(day, other_user))
					{
						indices.insert(other_user);
					}
				}
			}

			// Normalize meetings directly
			meetings[current_user] = indices.size() / static_cast<double>(n_users);
		}

		const double mean = std::accumulate(std::begin(meetings), std::end(meetings), 0.0) / meetings.size();

		const size_t size = meetings.size();
		const double std = std::sqrt(std::accumulate(std::begin(meetings), std::end(meetings), 0.0, [mean, size](const double accumulator, const double val)
		{
			return accumulator + (val - mean) * (val - mean) / (size - 1);
		}));

		return 1 - mean + std;
	}

	double error_foreigners(const Matrix<int>& days)
	{
		Matrix<double> entropies(n_days, n_groups);
		for (size_t day = 0; day < days.rows; ++day)
		{
			for (int group = 0; group < n_groups; ++group)
			{
				std::valarray<uchar> counts(static_cast<uchar>(0), 2);
				for (size_t user = 0; user < days.columns; ++user)
				{
					if (days(day, user) == group)
					{
						counts[foreigners[user]]++;
					}
				}

				if (counts[0] == 0 || counts[1] == 0)
				{
					entropies(day, group) = 1;
					continue;
				}

				const double total = counts.sum();
				std::valarray<double> probabilities = { counts[0] / total, counts[1] / total };

				const double entropy = -probabilities[0] * std::log2(probabilities[0]) - probabilities[1] * std::log2(probabilities[1]);
				entropies(day, group) = 1 - entropy;
			}
		}

		const std::valarray<double>& values = entropies.data;
		const double mean = std::accumulate(std::begin(values), std::end(values), 0.0) / values.size();

		const size_t size = values.size();
		const double std = std::sqrt(std::accumulate(std::begin(values), std::end(values), 0.0, [mean, size](const double accumulator, const double val)
		{
			return accumulator + (val - mean) * (val - mean) / (size - 1);
		}));

		return mean + std;
	}

	double error_total(const Matrix<int>& days)
	{
		double error = error_group_sizes(days) * alphas[0] + error_meetings(days) * alphas[1];
		if (!foreigners.empty())
		{
			error += error_foreigners(days) * alphas[2];
		}

		return error;
	}

private:
	int n_groups;
	int n_days;
	int n_users;
	std::vector<int> foreigners;
	std::vector<double> alphas;
};
