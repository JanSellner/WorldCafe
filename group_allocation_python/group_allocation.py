import argparse
import json
import sys
import numpy as np

from GroupSearch import GroupSearch

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Finds a good group allocation.')
    parser.add_argument('--n_groups', type=int, help='Number of groups/days.', required=True)
    parser.add_argument('--n_users', type=int, help='Number of users.', required=True)
    parser.add_argument('--foreigners', type=str, help='Information about the foreigner state of each user passed as JSON array with either 0 (non-foreigner) or 1 (foreigner) values.')
    parser.add_argument('--alphas', type=str, help='Weights for the individual components of the error function passed as JSON array.')

    args = parser.parse_args()

    if args.n_groups < 2:
        sys.exit('There must be at least two groups.')

    if args.n_users < args.n_groups:
        sys.exit('There are not enough users available to fill the groups.')

    foreigners = None
    if args.foreigners is not None:
        try:
            foreigners = json.loads(args.foreigners)
        except json.JSONDecodeError:
            sys.exit('Could not parse the foreigners list. Please provide a valid JSON array.')

        if args.n_users != len(foreigners):
            sys.exit(f'A foreigner state must be given for each user ({args.n_users} users and {len(foreigners)} foreigner values given).')

        if not all([state in [0, 1] for state in foreigners]):
            sys.exit('Please use only 0 or 1 to specify the foreigner state.')

    alphas = None
    if args.alphas is not None:
        try:
            alphas = json.loads(args.alphas)
        except json.JSONDecodeError:
            sys.exit('Could not parse the alpha weights. Please provide a valid JSON array.')

        if not np.isclose(sum(alphas), 1):
            sys.exit('The alpha weights need to sum up to 1.')

        if foreigners is None and len(alphas) != 2:
            sys.exit('Each error component must have a corresponding alpha weight. Note that there should be 2 weights since no information about the foreigners is available.')
        elif foreigners is not None and len(alphas) != 3:
            sys.exit('Each error component must have a corresponding alpha weight. Note that there should be 3 weights since information about the foreigners is available.')

    group_search = GroupSearch(args.n_groups, args.n_users, foreigners, alphas)
    alloc = group_search.find_best_allocation()
    print(json.dumps(alloc.tolist()))
