import numpy as np
from scipy.stats import entropy
import copy

class GroupEvaluation:
    def __init__(self, foreigners):
        self.n_students = len(foreigners)

        self.labels = [1, 2, 3]
        self.n_group_opt = self.n_students / len(self.labels)

        self.foreigners = foreigners

    # Mapping for the last day
    def last_comb(self, combs: list):
        comb_remaining = []

        for i in range(self.n_students):
            available = [comb[i] for comb in combs]
            comb_remaining.append(np.setdiff1d(self.labels, available)[0])

        return comb_remaining

    def error_group_sizes(self, combs: list):
        errors = []

        for comb in combs:
            counts = np.unique(comb, return_counts=True)[1]
            if len(counts) < len(self.labels):
                # At least one slot did not get a student at all --> max error
                errors.append(1)

            # Use the difference to the optimal solution as error
            diffs = np.abs(counts - self.n_group_opt)
            # The weakest group size counts (all groups should have an equal number of members)
            diffs = np.max(diffs)
            errors.append(diffs / self.n_group_opt)

        # The group sizes should be good on every day
        return max(errors)

    def error_diffusion(self, combs: list):
        confusions = np.zeros(self.n_students)
        for i in range(self.n_students):
            index_others = set()

            for comb in combs:
                comb = np.asarray(comb)
                index_others.update(np.where(comb == comb[i])[0])

            confusions[i] = len(index_others)

        return 1 - np.min(confusions) / self.n_students

    def error_foreigners(self, combs:list):
        errors = []

        for comb in combs:
            comb = np.asarray(comb)

            entropies = []
            for label in self.labels:
                indices = np.where(comb == label)[0]
                if len(indices) == 0:
                    entropies.append(0)
                    continue

                foreigners_group = self.foreigners[indices]

                probabilities = np.zeros(2)
                unique, counts = np.unique(foreigners_group, return_counts=True)
                for value, count in zip(unique, counts):
                    probabilities[value] = count / len(foreigners_group)

                entropies.append(entropy(probabilities, base=2.0))

            errors.append(1 - np.min(entropies))

        return max(errors)

    def error_total(self, combs: list):
        combs = copy.deepcopy(combs) + [self.last_comb(combs)]

        return [self.error_group_sizes(combs), self.error_diffusion(combs), self.error_foreigners(combs)]
