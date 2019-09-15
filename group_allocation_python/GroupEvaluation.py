import numpy as np
from scipy.stats import entropy


class GroupEvaluation:
    def __init__(self, groups, n_users, foreigners=None, alphas=None):
        self.groups = groups
        self.n_users = n_users
        self.opt_group_size = self.n_users / len(self.groups)

        if alphas is None:
            self.alphas = [1/3] * 3
        else:
            self.alphas = alphas
            assert 2 <= len(self.alphas) <= 3, 'Each error component must have a corresponding alpha weight.'
            assert np.isclose(sum(self.alphas), 1), 'The alpha weights need to sum up to 1.'

        self.foreigners = foreigners
        if self.foreigners is None:
            self.alphas = self.alphas[:2]
        else:
            assert len(self.foreigners) == self.n_users, 'A foreigner state must be given for each student.'
            assert len(self.alphas) == 3, 'There are three error components when using foreigner states.'
            self.foreigners = np.asarray(self.foreigners)

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
            # The group assignments are valid indices so we can use them directly to count the members per group
            counts_day = np.zeros(len(self.groups), np.int32)
            for value in day:
                counts_day[value] += 1

            self.counts[i, :] = counts_day

        # Apply some basic normalization to make this error more comparable to the other errors
        # Note: this does not ensure that the normalized values are in the range [0; 1]. But at least good solutions should be in the near vicinity of this range (bad solutions have values > 1 which leads to additional penalization which is probably good since we want equal groups sizes in general)
        normalized_counts = self.counts / self.opt_group_size

        # The group sizes should be as close as possible to the optimum
        # The group sizes should be roughly equal
        return np.mean(np.abs(normalized_counts - 1)) + np.std(normalized_counts, ddof=1)

    def error_meetings(self, days: np.ndarray):
        meetings = np.zeros(self.n_users)

        # Count how many other students each student meets (including herself/himself)
        for i in range(self.n_users):
            indices = set()

            for day in days:
                # At each day, find the other team members (they are assigned to the same group number as the current student)
                indices.update(np.where(day == day[i])[0])

            meetings[i] = len(indices)
            self.others[i] = indices  # For statistics

        # Norm to [0; 1]
        meetings /= self.n_users

        # The percentage of other students met should be as high as possible
        # The percentages should be roughly equal
        return 1 - np.mean(meetings) + np.std(meetings, ddof=1)

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
                unique, counts = np.unique(foreigners_group, return_counts=True)  # Number of foreigners and non-foreigners
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
        return np.mean(entropies) + np.std(entropies, ddof=1)

    def error_components(self, days: np.ndarray):
        if days.shape[0] == len(self.groups) - 1:
            days = self.add_last_comb(days)

        error = [self.error_group_sizes(days), self.error_meetings(days)]

        if self.foreigners is not None:
            error.append(self.error_foreigners(days))

        return error

    def error_total(self, days: np.ndarray):
        errors = self.error_components(days)

        return np.dot(self.alphas, errors)
