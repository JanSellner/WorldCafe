import itertools

import numpy as np
from group_common import GroupEvaluation

n_students = 12
groups = [1, 2, 3]

init_mapping = np.zeros(n_students, np.int32)
init_mapping[:4] = 1
init_mapping[4:8] = 2
init_mapping[8:12] = 3

foreigners = np.array([0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1], np.int32)
assert len(init_mapping) == len(foreigners)

labels = [1, 2, 3]
n_group_opt = n_students / len(labels)

# First, find all possible group assignments
combs = []
for c in itertools.product(labels, repeat=n_students):
    if not any(c == init_mapping):
        combs.append(c)

gval = GroupEvaluation(foreigners, groups)

errors = []
for c in combs:
    errors.append(gval.error_total(np.vstack([init_mapping, c])))

# print(errors)
print(min(errors))

