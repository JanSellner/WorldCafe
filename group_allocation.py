import argparse
import json
import sys

from GroupSearch import GroupSearch
from JSONNumpyEncoder import JSONNumpyEncoder

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Finds a good group allocation.')
    parser.add_argument('n_groups', type=int, help='Number of groups/days')
    parser.add_argument('n_users', type=int, help='Number of users')
    parser.add_argument('--foreigners', type=str, help='Information about the foreigner state of each user passed as JSON array with either 0 (non-foreigner) or 1 (foreigner) values.')

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

    group_search = GroupSearch(args.n_groups, args.n_users, foreigners)
    alloc = group_search.find_best_allocation()
    print(json.dumps(alloc, cls=JSONNumpyEncoder))
