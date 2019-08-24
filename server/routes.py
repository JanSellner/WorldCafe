from GroupSearch import GroupSearch
from server import app
from flask import render_template

import pandas as pd
import numpy as np


@app.route('/')
@app.route('/index')
def index():
    df = pd.read_csv('example_data.csv')

    if 'Foreigners' in df:
        foreigners = df['Foreigner'].to_numpy().astype(np.int32)
    else:
        foreigners = None

    group_search = GroupSearch(3, len(df), foreigners)
    alloc, error = group_search.find_best_allocation()
    print(error)

    days = []
    for idx in range(alloc.shape[0]):
        day = alloc[idx, :]
        group_numbers = np.unique(day)
        data = [{
                'members': df[day == g].values.tolist(),
                'name': f'Group {g}'
             } for g in group_numbers
        ]
        days.append(data)

    return render_template('index.html', columns=df.columns, days=days)
