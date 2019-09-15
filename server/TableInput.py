import csv
import io
import json
import subprocess

import numpy as np
import pandas as pd
from flask import flash

from group_allocation_python.GroupEvaluation import GroupEvaluation
from group_allocation_python.GroupSearch import GroupSearch
from JSONNumpyEncoder import JSONNumpyEncoder
from server import UserError, ServerError


class TableInput:
    def __init__(self, df: pd.DataFrame, n_groups: int, alphas: list, listener=None):
        assert len(alphas) == 3, 'Three weights required'
        self.df = df

        if len(self.df) < n_groups:
            raise UserError('There are not enough users available to fill the groups.')

        if not np.isclose(sum(alphas), 1):
            raise UserError('The alpha weights need to sum up to 1.')

        if 'Foreigner' in self.df:
            self.foreigners = self.df['Foreigner'].to_numpy().astype(np.int32)
            if len(self.foreigners) != len(self.df):
                raise UserError('A foreigner state must be given for each user.')
        else:
            self.foreigners = None

            # We only need the first to weights when no foreigners are given
            alphas = alphas[:2]
            alphas_total = sum(alphas)
            if not np.isclose(alphas_total, 1):
                # Make sure they sum up to 1
                alphas[0] /= alphas_total
                alphas[1] /= alphas_total

                flash(fr'The weights were rescaled to \(\alpha_s = {alphas[0]:.2}\) and \(\alpha_m = {alphas[1]:.2}\) since they had not summed up to 1.')

        self.alphas = alphas

        iterations = GroupSearch(n_groups, len(self.df)).total_iterations()
        if iterations > 10_000_000:
            raise UserError('The computation would take too long for this configuration. Please specify less groups and/or less users.')

        # The algorithm is run as a separate process
        cmd = ['group_allocation_c++/x64/Release/group_allocation_c++.exe', '--n_groups', str(n_groups), '--n_users', str(len(self.df))]

        if self.foreigners is not None:
            cmd.append('--foreigners')
            cmd.append(json.dumps(self.foreigners, cls=JSONNumpyEncoder))

        cmd.append('--alphas')
        cmd.append(json.dumps(self.alphas, cls=JSONNumpyEncoder))

        # Popen works asynchronously (approach inspired by https://stackoverflow.com/a/28319191)
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) as process:
            for line in process.stdout:
                try:
                    # The first lines denote the progress
                    progress = float(line)
                    if listener is not None:
                        listener(progress)
                except ValueError:
                    try:
                        print(line)
                        # The last line contains the result of the algorithm
                        self.alloc = np.asarray(json.loads(line))
                    except json.JSONDecodeError as error:
                        raise ServerError(ServerError.CODE_RESULT_PARSING, str(error))

            process.wait()
            if process.returncode != 0:
                raise ServerError(ServerError.CODE_EXTERNAL_PROGRAM, process.stderr.read())

    def table_data(self):
        days = []
        for idx in range(self.alloc.shape[0]):
            day_alloc = self.alloc[idx, :]
            group_numbers = np.unique(day_alloc)

            group_data = []
            for group in group_numbers:
                current_group = {
                    'members': self.df[day_alloc == group].values.tolist(),
                    'name': f'Group {group + 1}'
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

    def csv_table(self, table_data=None):
        if table_data is None:
            table_data = self.table_data()

        with io.StringIO() as file:
            writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)

            # Header
            writer.writerow(['Group'] + table_data['columns'].tolist())

            for i, day in enumerate(table_data['days']):
                writer.writerow([f'Day {i+1}'])
                for g, group in enumerate(day):
                    [writer.writerow([f'Group {g+1}'] + row) for row in group['members']]

            file.seek(0)
            return file.read()

    def stats(self):
        gval = GroupEvaluation(np.unique(self.alloc), self.alloc.shape[1], self.foreigners, self.alphas)
        errors = gval.error_components(self.alloc)
        group_sizes = gval.counts.transpose().tolist()

        stats = {
            'error_size': round(errors[0], 2),
            'error_meetings': round(errors[1], 2),
            'error': round(gval.error_total(self.alloc), 2),
            'groups': {
                'sizes': group_sizes,
                'sizes_mean': np.round(np.mean(gval.counts), 2)
            }
        }

        if len(errors) == 3:
            stats['error_foreigners'] = round(errors[2], 2)

        if 'First Name' in self.df and 'Family Name':
            names = (self.df['First Name'] + ' ' + self.df['Family Name']).tolist()
        elif 'Name' in self.df:
            names = self.df['Name'].tolist()
        else:
            names = [f'Student {i}' for i in range(len(self.df))]

        meets_others = [len(others) for others in gval.others]
        member_stats = {
            'names': names,
            'meets_others': meets_others,
            'meets_others_mean': np.round(np.mean(meets_others), 2)
        }

        if self.foreigners is not None:
            member_stats['foreigners'] = self.foreigners.tolist()
            member_stats['meets_non-foreigners'] = []
            member_stats['meets_foreigners'] = []

            for others in gval.others:
                _, counts = np.unique(self.foreigners[list(others)], return_counts=True)
                member_stats['meets_non-foreigners'].append(counts[0])
                member_stats['meets_foreigners'].append(counts[1])

            _, counts = np.unique(self.foreigners, return_counts=True)

            stats['n_non-foreigners'] = counts[0]
            stats['n_foreigners'] = counts[1]

        stats['members'] = member_stats
        return stats
