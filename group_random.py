import numpy as np

from group_allocation_python.GroupEvaluation import GroupEvaluation
from group_allocation_python.GroupSearch import GroupSearch


if __name__ == '__main__':
    n_users = 4
    n_groups = 3

    group_search = GroupSearch(n_groups, n_users)
    alloc = group_search.find_best_allocation()

    gval = GroupEvaluation(np.unique(alloc), alloc.shape[1])
    error = sum(gval.error_components(alloc))

    meets = [len(others) for others in gval.others]
    days = [np.unique(day, return_counts=True)[1] for day in alloc]

    print(meets)
    print(days)
    print(error)


# if __name__ == '__main__':
#     df = pd.read_csv('example_data.csv')
#     foreigners = df['Foreigner'].to_numpy().astype(np.int32)
#     alphas = [0.17, 0.77, 0.06]
#     n_groups = 3
#
#     group_search = GroupSearch(n_groups, len(df), foreigners, alphas)
#     alloc = group_search.find_best_allocation()
#
#     gval = group_search.gval
#     print(gval.error_components(alloc))
#     print(gval.error_total(alloc))
#
#     meets = [len(others) for others in gval.others]
#     days = [np.unique(day, return_counts=True)[1] for day in alloc]
#
#     print(meets)
#     print(days)

# TODO: error messages code duplication --> maybe file with all common strings
# TODO: test both implementations are the same
