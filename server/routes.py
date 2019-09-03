import base64
from io import StringIO

import pandas as pd
import numpy as np
from flask import render_template, request, flash
from werkzeug.datastructures import CombinedMultiDict

from server.TableInput import TableInput
from server import app, socketio, UserError, ServerError
from server.forms import InputDataForm
from timeit import default_timer


class ExecutionStats:
    def __init__(self):
        self.last_progress = 0
        self.last_time = None
        self.progress_diffs = []
        self.time_diffs = []

    def progress_listener(self, value):
        print(value)
        time = default_timer()
        if self.last_time is not None:
            self.progress_diffs.append(value - self.last_progress)
            self.time_diffs.append(time - self.last_time)

            average_time = np.average(self.time_diffs, weights=self.progress_diffs) / np.mean(self.progress_diffs)
            remaining_time = round(average_time * (1 - value))
            socketio.emit('update remaining time', remaining_time)

        self.last_progress = value
        self.last_time = time
        socketio.emit('update progress', value)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = InputDataForm(CombinedMultiDict((request.files, request.form)))
    try:
        if form.validate_on_submit():
            if form.selection_type.data == 'text':
                df = pd.DataFrame(form.users.data.splitlines(), columns=['Name'])
            elif form.selection_type.data == 'file':
                file_content = form.file.data.read().decode('utf-8')
                df = pd.read_csv(StringIO(file_content))
            else:
                raise UserError('Please provide either a lists of users or upload a csv file.')

            if df.empty:
                raise UserError('No data provided.')

            if any(df.duplicated()):
                flash(f'Duplicate lines found in the input ({str(df[df.duplicated()].iloc[:, 0].tolist())}). Please check whether your input contains some errors. The lines are not removed and the algorithm proceeds as usual.')
            if len(df) == form.n_groups.data:
                flash('The number of groups equals the number of users. It does not really make sense to run the algorithm in this case since there is only one solution. Please add more users or specify less groups.')

            execution_stats = ExecutionStats()
            table_input = TableInput(df, form.n_groups.data, execution_stats.progress_listener)

            # Generate CSV file data and wrap it in a data URI
            table_data = table_input.table_data()
            csv = table_input.csv_table(table_data)
            csv_base64 = base64.b64encode(csv.encode('utf-8')).decode('utf-8')

            form.progress_bar = 1

            return render_template('index.html', form=form, table=table_data, stats=table_input.stats(), csv_data=csv_base64)
        else:
            return render_template('index.html', form=form)
    except UserError as error:
        return render_template('index.html', form=form, error=str(error))
    except ServerError as error:
        print(error)
        return render_template('index.html', form=form, error=f'An internal server error occurred. Please report this problem to the developers (code {error.code}).')
