import numpy as np

from group_allocation_python.GroupEvaluation import GroupEvaluation

alloc = np.array([[2, 2, 0, 2, 2, 1],
                  [1, 0, 2, 0, 1, 0],
                  [0, 1, 1, 1, 0, 2]])

gval = GroupEvaluation(np.unique(alloc), alloc.shape[1], np.array([1, 1, 1, 0, 0, 0]))
print(gval.error_group_sizes(alloc))
print(gval.error_meetings(alloc))
print(gval.error_foreigners(alloc))
