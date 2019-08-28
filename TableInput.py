import numpy as np

from GroupEvaluation import GroupEvaluation
from GroupSearch import GroupSearch


class TableInput:
    def __init__(self, df, n_groups):
        self.df = df

        if len(self.df) < n_groups:
            raise ValueError('There are not enough students available to fill the groups')

        if 'Foreigner' in self.df:
            self.foreigners = self.df['Foreigner'].to_numpy().astype(np.int32)
            if len(self.foreigners) != len(self.df):
                raise ValueError('A foreigner state must be given for each student')
        else:
            self.foreigners = None

        group_search = GroupSearch(n_groups, len(self.df), self.foreigners)
        self.alloc = group_search.find_best_allocation()

    def table_data(self):
        days = []
        for idx in range(self.alloc.shape[0]):
            day_alloc = self.alloc[idx, :]
            group_numbers = np.unique(day_alloc)

            group_data = []
            for group in group_numbers:
                current_group = {
                    'members': self.df[day_alloc == group].values.tolist(),
                    'name': f'Group {group}'
                }

                if self.foreigners is not None:
                    _, counts = np.unique(self.foreigners[day_alloc == group], return_counts=True)
                    current_group['non-foreigners'] = counts[0]
                    current_group['foreigners'] = counts[1]

                group_data.append(current_group)

            days.append(group_data)

        return {
            'columns': self.df.columns,
            'days': days
        }

    def stats(self):
        gval = GroupEvaluation(np.unique(self.alloc), self.alloc.shape[1], self.foreigners)
        error = sum(gval.error_total(self.alloc))

        if 'First Name' in self.df and 'Family Name':
            names = (self.df['First Name'] + ' ' + self.df['Family Name']).tolist()
        elif 'Name' in self.df:
            names = self.df['Name'].tolist()
        else:
            names = [f'Student {i}' for i in range(len(self.df))]

        member_stats = {
            'names': names
        }

        if self.foreigners is None:
            return {
                'error': error,
                'members': member_stats
            }
        else:
            member_stats['foreigners'] = self.foreigners.tolist()
            member_stats['meets_non-foreigners'] = []
            member_stats['meets_foreigners'] = []

            for others in gval.others:
                _, counts = np.unique(self.foreigners[list(others)], return_counts=True)
                member_stats['meets_non-foreigners'].append(counts[0])
                member_stats['meets_foreigners'].append(counts[1])

            _, counts = np.unique(self.foreigners, return_counts=True)

            return {
                'error': error,
                'members': member_stats,
                'n_non-foreigners': counts[0],
                'n_foreigners': counts[1]
            }
