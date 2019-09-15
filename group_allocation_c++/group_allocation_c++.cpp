#include <iostream>
#include <vector>
#include <valarray>
#include "Matrix.h"
#include "GroupEvaluation.h"
#include "GroupSearch.h"
#include "args.hxx"
#include <regex>

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

			if (n_users != static_cast<int>(foreigners.size()))
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
