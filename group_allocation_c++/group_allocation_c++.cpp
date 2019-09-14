#include <iostream>
#include <utility>
#include <vector>
#include <valarray>
#include <chrono>
#include <algorithm>
#include "Matrix.h"
#include "GroupEvaluation.h"
#include "GroupSearch.h"
#include "args.hxx"
#include <regex>

int n_groups = 5;
int n_users = 10;

// TODO: mean, std function
// TODO: const std::valarray<int> day = days.row(row); produces a copy (http://www.cplusplus.com/reference/valarray/slice_array/)

void gval_performance()
{
	Matrix<int> alloc_start(std::valarray<int>({
		1, 2, 4, 2, 3, 0, 3, 0, 3, 4,
		4, 0, 0, 3, 2, 4, 2, 4, 1, 1,
		0, 4, 3, 1, 0, 2, 0, 2, 0, 2,
		3, 3, 2, 0, 1, 1, 1, 3, 4, 3,
		2, 1, 1, 4, 4, 3, 4, 1, 2, 0
		}), n_users);
	std::vector<int> foreigners = { 0, 0, 1, 1, 0, 1, 1, 1, 0, 1 };

	// GroupEvaluation gval(n_groups, n_users, foreigners);
	GroupSearch group_search(n_groups, n_users, foreigners);
	
	size_t n_runs = 10;
	std::vector<double> times(n_runs);
	for (size_t i = 0; i < times.size(); ++i)
	{
		auto begin = std::chrono::high_resolution_clock::now();

		for (int j = 0; j < 1; ++j)
		{
			// gval.error_total(alloc_start);
			// error_group_sizes(alloc_start);
			// error_meetings(alloc_start);
			// gval.error_foreigners(alloc_start);
			group_search.find_best_allocation();
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

template<typename T>
std::vector<T> parse_json(std::string argument, const std::string& error_message)
{
	if (!std::regex_match(argument, std::regex(R"(\[[\d,.\s]+\])")))
	{
		throw args::ValidationError(error_message);
	}
	
	argument = std::regex_replace(argument, std::regex(R"([\[\]])"), "");
	argument = std::regex_replace(argument, std::regex(R"(,\s*)"), " ");

	// https://stackoverflow.com/a/20659156
	std::stringstream iss(argument);

	T number;
	std::vector<T> numbers;
	while (iss >> number) {
		numbers.push_back(number);
	}

	return numbers;
}

int main(int argc, char** argv)
{
	args::ArgumentParser parser("Finds a good group allocation.");
	args::HelpFlag help(parser, "help", "Display the help menu.", { 'h', "help" });
	args::ValueFlag<int> args_n_groups(parser, "n_groups", "Number of groups/days.", { "n_groups" }, args::Options::Required | args::Options::Single);
	args::ValueFlag<int> args_n_users(parser, "n_users", "Number of users.", { "n_users" }, args::Options::Required | args::Options::Single);
	args::ValueFlag<std::string> args_foreigners(parser, "foreigners", "Information about the foreigner state of each user passed as JSON array with either 0 (non-foreigner) or 1 (foreigner) values.", { "foreigners" }, args::Options::Single);
	args::ValueFlag<std::string> args_alphas(parser, "alphas", "Weights for the individual components of the error function passed as JSON array.", { "alphas" }, args::Options::Single);
	
	try
	{
		parser.ParseCLI(argc, argv);

		const int n_groups = args::get(args_n_groups);
		if (n_groups < 2)
		{
			throw args::ValidationError("There must be at least two groups.");
		}

		const int n_users = args::get(args_n_users);
		if (n_users < n_groups)
		{
			throw args::ValidationError("There are not enough users available to fill the groups.");
		}

		std::vector<int> foreigners = {};
		if (args_foreigners)
		{
			foreigners = parse_json<int>(args::get(args_foreigners), "Could not parse the foreigners list. Please provide a valid JSON array.");

			if (n_users != foreigners.size())
			{
				throw args::ValidationError("A foreigner state must be given for each user (" + std::to_string(n_users) + " users and " + std::to_string(foreigners.size()) + " foreigner values given).");
			}

			for (auto foreigner : foreigners)
			{
				if (foreigner != 0 && foreigner != 1)
				{
					throw args::ValidationError("Please use only 0 or 1 to specify the foreigner state.");
				}
			}
		}

		std::vector<double> alphas = {};
		if (args_alphas)
		{
			alphas = parse_json<double>(args::get(args_alphas), "Could not parse the alpha weights. Please provide a valid JSON array.");

			const double sum = std::accumulate(alphas.begin(), alphas.end(), 0.0);
			if (std::abs(sum - 1.0) > 0.001)
			{
				throw args::ValidationError("The alpha weights need to sum up to 1.");
			}

			if (!args_foreigners && alphas.size() != 2)
			{
				throw args::ValidationError("Each error component must have a corresponding alpha weight. Note that there should be 2 weights since no information about the foreigners is available.");
			}
			else if (args_foreigners && alphas.size() != 3)
			{
				throw args::ValidationError("Each error component must have a corresponding alpha weight. Note that there should be 3 weights since information about the foreigners is available.");
			}
		}

		GroupSearch group_search(n_groups, n_users, foreigners, alphas);

		Matrix<int> alloc = group_search.find_best_allocation();
		std::cout << alloc.to_json() << std::endl;
	}
	catch (const args::Help&)
	{
		std::cout << parser;
		return 0;
	}
	catch (const args::ParseError& e)
	{
		std::cerr << e.what() << std::endl;
		std::cerr << parser;
		return 1;
	}
	catch (const args::ValidationError& e)
	{
		std::cerr << e.what() << std::endl;
		std::cerr << parser;
		return 1;
	}

	return 0;
}
