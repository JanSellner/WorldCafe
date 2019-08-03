import numpy as np
from group_common import GroupEvaluation

n_students = 12
groups = [1, 2, 3]
foreigners = np.array([0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1], np.int32)


def test():
    combs = np.stack([np.random.choice(groups, size=2, replace=False) for i in range(n_students)]).transpose()
    # combs = [
    #     [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3],
    #     [2, 2, 2, 2, 3, 3, 3, 3, 1, 1, 1, 1]
    # ]
    gval = GroupEvaluation(foreigners, groups)

    error = gval.error_total(combs)
    print('beginning', error)
    last_improvement = -1

    for i in range(200):
        idx_student = np.random.randint(0, n_students)
        new_slots = np.random.choice(groups, 2, replace=False)

        # Temporarily assign the student to new groups (for all days)
        combs_copy = combs.copy()
        combs_copy[:, idx_student] = new_slots

        error_new = gval.error_total(combs_copy)
        if sum(error_new) < sum(error):
            error = error_new
            combs = combs_copy
            last_improvement = i

    print(error, sum(error))
    print(combs)
    print(last_improvement)


for _ in range(20):
    test()
