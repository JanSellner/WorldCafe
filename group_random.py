import numpy as np
from group_common import GroupEvaluation
import copy

n_students = 12
labels = [1, 2, 3]
foreigners = np.array([0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1], np.int32)


def test():
    combs = np.stack([np.random.choice([1, 2, 3], size=2, replace=False) for i in range(12)]).transpose().tolist()
    # combs = [
    #     [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3],
    #     [2, 2, 2, 2, 3, 3, 3, 3, 1, 1, 1, 1]
    # ]
    gval = GroupEvaluation(foreigners)

    error = gval.error_total(combs)
    print('beginning', error)

    for _ in range(100):
        idx_student = np.random.randint(0, n_students)
        new_slots = np.random.choice(labels, 2, replace=False)

        combs_copy = copy.deepcopy(combs)
        for level in range(2):
            combs_copy[level][idx_student] = new_slots[level]

        error_new = gval.error_total(combs_copy)
        if sum(error_new) < sum(error):
            error = error_new
            combs = combs_copy

    print(error, sum(error))
    print(combs)


for _ in range(10):
    test()
