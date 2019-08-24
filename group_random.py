import numpy as np

from GroupSearch import GroupSearch

group_search = GroupSearch(3, 6, np.array([0, 0, 1, 1, 0, 0], np.int32))
print(group_search.find_best_allocation())
