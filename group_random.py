import numpy as np

from MeasureTime import MeasureTime
from GroupEvaluation import GroupEvaluation

n_students = 6
groups = [1, 2, 3]
foreigners = np.array([0, 0, 1, 1, 0, 0], np.int32)#, 0, 1, 1, 1, 0, 1, 1
assert len(foreigners) == n_students


def test():
    combs = np.stack([np.random.choice(groups, size=2, replace=False) for _ in range(n_students)]).transpose()
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

    return error, last_improvement, combs


errors = []
last_improvements = []

with MeasureTime():
    for _ in range(20):
        error, last_improvement, combs = test()
        errors.append(error)
        last_improvements.append(last_improvement)

best_error = min([sum(e) for e in errors])
print(f'best error = {best_error}')
