import numpy as np

from misc.MeasureTime import MeasureTime
from group_allocation_python.GroupEvaluation import GroupEvaluation

# if __name__ == '__main__':
#     with MeasureTime():
#         group_search = GroupSearch(5, 10, np.array([0, 0, 1, 1, 0, 1, 1, 1, 0, 1]))
#         alloc = group_search.find_best_allocation()
#         print(alloc)

alloc = np.array([
 [1, 2, 4, 2, 3, 0, 3, 0, 3, 4],
 [4, 0, 0, 3, 2, 4, 2, 4, 1, 1],
 [0, 4, 3, 1, 0, 2, 0, 2, 0, 2],
 [3, 3, 2, 0, 1, 1, 1, 3, 4, 3],
 [2, 1, 1, 4, 4, 3, 4, 1, 2, 0]])

# Opt
# alloc = np.array([
#  [2, 0, 4, 1, 2, 1, 4, 3, 0, 3],
#  [4, 1, 3, 4, 3, 0, 1, 2, 2, 0],
#  [1, 2, 0, 3, 4, 2, 0, 4, 3, 1],
#  [3, 3, 1, 0, 0, 4, 2, 1, 4, 2],
#  [0, 4, 2, 2, 1, 3, 3, 0, 1, 4]])

foreigners = np.array([0, 0, 1, 1, 0, 1, 1, 1, 0, 1])

gval = GroupEvaluation(np.unique(alloc), alloc.shape[1], foreigners)

with MeasureTime():
    for _ in range(200000):
        # gval.error_foreigners(alloc)
        # gval.error_meetings(alloc)
        gval.error_group_sizes(alloc)
