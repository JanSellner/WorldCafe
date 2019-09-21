import unittest
import numpy as np

from group_allocation_python.GroupSearch import GroupSearch
from group_allocation_python.GroupEvaluation import GroupEvaluation


class TestGroupSearch(unittest.TestCase):
    def test_find_alloc(self):
        n_groups = 3
        n_users = 4
        group_search = GroupSearch(n_groups, n_users, np.array([0, 0, 1, 1]))
        alloc = group_search.find_best_allocation()

        alloc_true = np.array([[0, 1, 0, 1],
                               [1, 2, 2, 0],
                               [2, 0, 1, 2]])

        self.assertTrue(alloc.shape == alloc_true.shape)
        self.assertTrue((np.unique(alloc) == np.unique(alloc_true)).all())
        self.assertTrue((alloc == alloc_true).all())


class TestGroupEvaluation(unittest.TestCase):
    def test_errors(self):
        alloc = np.array([
            [1, 2, 4, 2, 3, 0, 3, 0, 3, 4],
            [4, 0, 0, 3, 2, 4, 2, 4, 1, 1],
            [0, 4, 3, 1, 0, 2, 0, 2, 0, 2],
            [3, 3, 2, 0, 1, 1, 1, 3, 4, 3],
            [2, 1, 1, 4, 4, 3, 4, 1, 2, 0]])
        foreigners = np.array([0, 0, 1, 1, 0, 1, 1, 1, 0, 1])
        self.assertEqual(alloc.shape[1], len(foreigners))

        gval = GroupEvaluation(np.unique(alloc), alloc.shape[1], foreigners)
        self.assertEqual(gval.error_group_sizes(alloc), 0.9)
        self.assertEqual(gval.error_meetings(alloc), 0.5429272594305719)
        self.assertEqual(gval.error_foreigners(alloc), 1.0645929264282177)
        self.assertEqual(gval.error_total(alloc), 0.8358400619529298)


if __name__ == '__main__':
    unittest.main(verbosity=2)
