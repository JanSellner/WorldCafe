from multiprocessing import Pool, cpu_count

import numpy as np
import itertools

from GroupEvaluation import GroupEvaluation
from MeasureTime import MeasureTime


class GroupSearch:
    def __init__(self, n_groups: int, n_users: int, foreigners=None):
        assert n_groups <= 8, 'The number of groups should not be too high as otherwise the algorithm takes too long'

        self.groups = np.arange(1, n_groups + 1)
        self.n_users = n_users

        self.gval = GroupEvaluation(self.groups, self.n_users, foreigners)

    def find_best_allocation(self):
        seeds = range(20)

        with MeasureTime():
            pool = Pool(cpu_count())
            results = pool.map(self._start_random_walk, seeds)
            pool.close()
            pool.join()

        best_error = np.inf
        best_combs = None
        for result in results:
            error, last_improvement, combs = result
            error = sum(result[0])
            if error < best_error:
                best_error = error
                best_combs = combs

        return self.gval.add_last_comb(best_combs)

    def _start_random_walk(self, seed):
        np.random.seed(seed)
        # Random combination for all users (columns) and all days (rows)
        combs = np.stack([np.random.choice(self.groups, size=len(self.groups) - 1, replace=False) for _ in range(self.n_users)]).transpose()

    def _start_random_walk(self, seed):
        if seed == 0:
            # The randomly initialized starting configuration may lead to degenerated results in extreme settings like 9 users and 6 groups. For this case, it is possible that some groups don't get users at all. Since this is something we want to avoid, we add an evenly distributed starting configuration manually so that there is at least one configuration which fills each group
            # The goal is to produce something like the following (4 users and 3 groups):
            # day1: 1 1 2 3
            # day2: 2 2 3 1
            first_day = np.sort(np.resize(self.groups, self.n_users))
            days = [first_day]

            for g in range(1, len(self.groups) - 1):
                prev_day = days[g - 1]
                next_day = prev_day % (len(self.groups)) + 1
                days.append(next_day)

            days = np.asarray(days)
        else:
            np.random.seed(seed)
            # Random combination for all users (columns) and all days (rows)
            days = np.stack([np.random.choice(self.groups, size=len(self.groups) - 1, replace=False) for _ in range(self.n_users)]).transpose()

        error = self.gval.error_total(days)
        last_improvement = -1

        for i in range(64):
            idx_user = np.random.randint(0, self.n_users)

            # For the selected user, iterate over every possible group assignment
            for new_slots in list(itertools.permutations(self.groups, len(self.groups) - 1)):
                # Temporarily assign the user to new groups (for all days)
                days_copy = days.copy()
                days_copy[:, idx_user] = new_slots

                error_new = self.gval.error_total(days_copy)
                if sum(error_new) < sum(error):
                    error = error_new
                    days = days_copy
                    last_improvement = i
                    print(i, error)

        return error, last_improvement, days
