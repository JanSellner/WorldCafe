#include <iostream>
#include <utility>
#include <vector>
#include <valarray>
#include <chrono>
#include "Matrix.h"
#include "GroupEvaluation.h"

int n_groups = 5;
int n_users = 10;


// TODO: mean, std function


int main()
{
	Matrix<int> alloc_start(std::valarray<int>({
		1, 2, 4, 2, 3, 0, 3, 0, 3, 4,
		4, 0, 0, 3, 2, 4, 2, 4, 1, 1,
		0, 4, 3, 1, 0, 2, 0, 2, 0, 2,
		3, 3, 2, 0, 1, 1, 1, 3, 4, 3,
		2, 1, 1, 4, 4, 3, 4, 1, 2, 0
		}), n_users);
	std::vector<int> foreigners = { 0, 0, 1, 1, 0, 1, 1, 1, 0, 1 };

	GroupEvaluation gval(n_groups, n_users, foreigners);
	gval.error_total(alloc_start);

	size_t n_runs = 10;
	std::vector<double> times(n_runs);
	for (size_t i = 0; i < times.size(); ++i)
	{
		auto begin = std::chrono::high_resolution_clock::now();

		for (int j = 0; j < 1000000; ++j)
		{
			// error_group_sizes(alloc_start);
			// error_meetings(alloc_start);
			gval.error_foreigners(alloc_start);
		}

		auto end = std::chrono::high_resolution_clock::now();
		times[i] = static_cast<double>(std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count());
		std::cout << times[i] << " ms" << std::endl;
	}

	double mean = std::accumulate(times.begin(), times.end(), 0.0) / times.size();
	auto size = times.size();
	double std = std::sqrt(std::accumulate(times.begin(), times.end(), 0.0, [&mean, size](const double accumulator, const double val)
	{
		return accumulator + (val - mean) * (val - mean) / (size - 1);
	}));

	std::cout << mean << " ms (std = " << std << ")" << std::endl;
}
