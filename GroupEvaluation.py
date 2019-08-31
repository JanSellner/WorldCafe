import numpy as np
from scipy.stats import entropy


class GroupEvaluation:
    def __init__(self, groups, n_users, foreigners=None):
        self.groups = groups
        self.n_users = n_users
        self.opt_group_size = self.n_users / len(self.groups)

        self.foreigners = foreigners
        if self.foreigners is not None:
            assert len(self.foreigners) == self.n_users, 'A foreigner state must be given for each student'

        self.others = np.empty(self.n_users, dtype=object)
        self.counts = None

    def add_last_comb(self, days: np.ndarray):
        # Mapping for the last day
        last_day = np.apply_along_axis(lambda x: np.setdiff1d(self.groups, x), axis=0, arr=days)

        return np.vstack([days, last_day])

    def error_group_sizes(self, days: np.ndarray):
        self.counts = np.zeros((days.shape[0], len(self.groups)))

        # Count how many students each group has on each day
        for i, day in enumerate(days):
            counts_day = np.unique(day, return_counts=True)[1]
            if len(counts_day) < len(self.groups):
                # At least one slot did not get a student at all --> high error
                return 10

            self.counts[i, :] = counts_day

        # Note: the counts values are currently not in the range [0; 1] and hence not directly comparable to the other measures. The counts values tend to be higher which means that they have a higher importance. This is probably not too bad since equal group sizes are favorable in general

        # The group sizes should be as close as possible to the optimum
        # The group sizes should be roughly equal
        return np.mean(np.abs(self.counts - self.opt_group_size)) + np.std(self.counts)

    def error_meetings(self, days: np.ndarray):
        meets_others = np.zeros(self.n_users)

        # Count how many other students each student meets (including herself/himself)
        for i in range(self.n_users):
            others_indices = set()

            for day in days:
                # At each day, find the other team members (they are assigned to the same group number as the current student)
                others_indices.update(np.where(day == day[i])[0])

            meets_others[i] = len(others_indices)
            self.others[i] = others_indices  # For statistics

        # Norm to [0; 1]
        meets_others /= self.n_users

        # The percentage of other students met should be as high as possible
        # The percentages should be roughly equal
        return 1 - np.mean(meets_others) + np.std(meets_others)

    def error_foreigners(self, days: np.ndarray):
        entropies = np.zeros((days.shape[0], len(self.groups)))

        for i, day in enumerate(days):
            entropies_day = []
            for group in self.groups:
                group_members_indices = np.where(day == group)[0]
                if len(group_members_indices) == 0:
                    entropies_day.append(0)
                    continue

                foreigners_group = self.foreigners[group_members_indices]

                # Calculate the fraction of foreigners and non-foreigners per group
                probabilities = np.zeros(2)
                unique, counts = np.unique(foreigners_group, return_counts=True)
                for value, count in zip(unique, counts):
                    probabilities[value] = count / len(foreigners_group)

                # The entropy is highest for the fraction (0.5, 0.5) which corresponds to a very well distributed group
                # It is lowest for e.g. (1, 0) which means that one group consists e.g. only of foreigners
                entropies_day.append(entropy(probabilities, base=2.0))

            entropies[i, :] = entropies_day

        # The entropy impurity measure has a maximum of 1 for (0.5, 0.5)
        entropies = 1 - entropies

        # The entropy values should be as low as possible
        # The entropy values should be roughly equal
        return np.mean(entropies) + np.std(entropies)

    def error_total(self, days: np.ndarray):
        if days.shape[0] == len(self.groups) - 1:
            days = self.add_last_comb(days)

        error = [self.error_group_sizes(days), self.error_meetings(days)]

        if self.foreigners is not None:
            error.append(self.error_foreigners(days))

        return error
