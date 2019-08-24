import itertools

import numpy as np
from GroupEvaluation import GroupEvaluation
from multiprocessing import Pool
from MeasureTime import MeasureTime


def run(combs):
    combs = np.array(combs).transpose()
    return sum(gval.error_total(combs))


n_students = 6
groups = [1, 2, 3]
foreigners = np.array([0, 0, 1, 1, 0, 0], np.int32)  #, 0, 1, 1, 1, 0, 1
assert len(foreigners) == n_students
gval = GroupEvaluation(foreigners, groups)

if __name__ == "__main__":
    comb_student = list(itertools.permutations(groups, 2))
    print(f'Number of combinations to check: {len(comb_student) ** n_students}')

    pool = Pool(6)
    with MeasureTime():
        errors = pool.map(run, itertools.product(comb_student, repeat=n_students))
    pool.close()
    pool.join()

    print(min(errors))
