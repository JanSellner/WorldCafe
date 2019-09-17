import itertools

import numpy as np
from group_allocation_python.GroupEvaluation import GroupEvaluation
from multiprocessing import Pool, cpu_count
from MeasureTime import MeasureTime


def run(combs):
    combs = np.array(combs).transpose()
    return sum(gval.error_components(combs))


n_students = 8
groups = [0, 1, 2]
# foreigners = np.array([0, 0, 1, 1, 0, 0], np.int32)  #, 0, 1, 1, 1, 0, 1
# assert len(foreigners) == n_students
gval = GroupEvaluation(groups, n_students)

if __name__ == "__main__":
    # Test every possible combination (works only for small problems)
    time_per_comb = 23.27 / 279936
    comb_student = list(itertools.permutations(groups, len(groups) - 1))
    n_combs = len(comb_student) ** n_students
    print(f'Number of combinations to check: {n_combs}')
    print(f'Estimated time: {time_per_comb * n_combs} s')

    with MeasureTime():
        pool = Pool(cpu_count())
        errors = pool.map(run, itertools.product(comb_student, repeat=n_students))
        pool.close()
        pool.join()

    print(min(errors))
