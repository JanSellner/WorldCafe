from GroupSearch import GroupSearch
from server import app
from flask import render_template, flash
from flask import request
from werkzeug.datastructures import CombinedMultiDict
from io import StringIO

import pandas as pd
import numpy as np

from server.forms import InputDataForm


def get_data(df, n_groups):
    if len(df) < n_groups:
        raise ValueError('There are not enough students available to fill the groups')

    if 'Foreigners' in df:
        foreigners = df['Foreigner'].to_numpy().astype(np.int32)
        if len(foreigners) != len(df):
            raise ValueError('A foreigner state must be given for each student')
    else:
        foreigners = None

    group_search = GroupSearch(n_groups, len(df), foreigners)
    alloc, error = group_search.find_best_allocation()
    print(error)

    days = []
    for idx in range(n_groups):
        day = alloc[idx, :]
        group_numbers = np.unique(day)
        data = [{
            'members': df[day == g].values.tolist(),
            'name': f'Group {g}'
        } for g in group_numbers]
        days.append(data)

    return df.columns, days


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = InputDataForm(CombinedMultiDict((request.files, request.form)))
    try:
        if form.validate_on_submit():
            if form.selection_type.data == 'text':
                data = pd.DataFrame(form.users.data.split(), columns=['Name'])
            elif form.selection_type.data == 'file':
                file_content = form.file.data.read().decode('utf-8')
                data = pd.read_csv(StringIO(file_content))
            else:
                raise ValueError('Please provide either a lists of users or upload a csv file')

            columns, days = get_data(data, form.n_groups.data)
            return render_template('index.html', columns=columns, days=days, form=form)
        else:
            return render_template('index.html', form=form)
    except ValueError as error:
        return render_template('index.html', form=form, error=str(error))
