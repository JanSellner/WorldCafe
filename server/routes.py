import base64
import os
import re
from io import StringIO
from timeit import default_timer

import numpy as np
import pandas as pd
from flask import render_template, request
from werkzeug.datastructures import CombinedMultiDict

from server import app, socketio, UserError, ServerError
from server.TableInput import TableInput
from server.forms import InputDataForm

session_mapper = {}
disconnected = []


class ExecutionStats:
    def __init__(self, sid):
        self.sid = sid
        self.last_progress = 0
        self.last_time = None
        self.progress_diffs = []
        self.time_diffs = []
        self.average_times = []

    def progress_listener(self, value):
        time = default_timer()
        if self.last_time is not None:
            self.progress_diffs.append(value - self.last_progress)
            self.time_diffs.append(time - self.last_time)

        if self.last_progress > 0.1:  # The first few updates tend to be unstable
            # Estimate average time per progress value
            current_average = np.average(self.time_diffs, weights=self.progress_diffs) / np.mean(self.progress_diffs)
            self.average_times.append(current_average)

            remaining_time = round(np.median(self.average_times) * (1 - value))  # The median should be relatively stable
        else:
            remaining_time = None

        self.last_progress = value
        self.last_time = time

        data = {
            'progress': value,
            'remaining_time': remaining_time
        }
        socketio.emit('update_progress', data, room=session_mapper[self.sid])

        # When using eventlet as webserver instead of the default development server, emits get stalled and only passed to the client at the end. This is most likely because the eventlet thread gets no CPU time (https://github.com/miguelgrinberg/Flask-SocketIO/issues/394#issuecomment-273842453).
        # The following call flushes the emits and ensures that the client gets the status updates faster (https://stackoverflow.com/a/36204786)
        # Note: at least currently, monkeypatching (https://stackoverflow.com/questions/34581255/python-flask-socketio-send-message-from-thread-not-always-working) seems not to be required which is another common cause of problems
        socketio.sleep(0)


@socketio.on('session_change')
def test_connect(old_sid):
    global session_mapper, disconnected

    if re.search('^[a-z0-9]+$', old_sid) and old_sid in disconnected:
        # Firefox immediately moves to the target page after the submit button is triggered. This leads to a new sid being generated (and another one when the response from the POST request is ready). Hence, the progress bar update fails since the connection to the old sid does not exist anymore
        # As a solution, the client informs the server when a new connection is established from an old one (the sid is known from the hidden input field)
        session_mapper[old_sid] = request.sid
        disconnected.remove(old_sid)


@socketio.on('disconnect')
def test_disconnect():
    global disconnected
    disconnected.append(request.sid)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = InputDataForm(CombinedMultiDict((request.files, request.form)))
    hosting_information = os.getenv('HOSTING_INFORMATION', 'No hosting information provided (this instance may be self-hosted).')

    try:
        if form.validate_on_submit():
            if form.selection_type.data == 'text':
                df = pd.DataFrame(form.users.data.splitlines(), columns=['Name'])
            elif form.selection_type.data == 'file':
                file_content = form.file.data.read().decode('utf-8')
                if file_content:
                    df = pd.read_csv(StringIO(file_content))
                else:
                    df = pd.DataFrame()
            else:
                raise UserError('Please provide either a lists of users or upload a csv file.')

            if df.empty:
                raise UserError('No data provided.')

            messages = {
                'notes': [],
                'warnings': []
            }

            if any(df.duplicated()):
                messages['warnings'].append(f'Duplicate lines found in the input ({str(df[df.duplicated()].iloc[:, 0].tolist())}). Please check whether your input contains some errors. The lines are not removed and the algorithm proceeds as usual.')
            if len(df) == form.n_groups.data:
                messages['warnings'].append('The number of groups equals the number of users. It does not really make sense to run the algorithm in this case since there is only one solution. Please add more users or specify less groups.')

            if form.sid.data:
                execution_stats = ExecutionStats(form.sid.data)
                listener = execution_stats.progress_listener

                # Default state: map sid to itself
                session_mapper[form.sid.data] = form.sid.data
            else:
                listener = None

            alphas = [form.alpha1.data, form.alpha2.data, form.alpha3.data]
            table_input = TableInput(df, form.n_groups.data, alphas, messages, listener)

            # Generate CSV file data and wrap it in a data URI
            table_data = table_input.table_data()
            csv = table_input.csv_table(table_data)
            csv_base64 = base64.b64encode(csv.encode('utf-8')).decode('utf-8')

            form.progress_bar = 1

            return render_template('index.html', form=form, table=table_data, stats=table_input.stats(), csv_data=csv_base64, messages=messages, hosting_information=hosting_information)
        else:
            return render_template('index.html', form=form, hosting_information=hosting_information)
    except UserError as error:
        return render_template('index.html', form=form, error=str(error), hosting_information=hosting_information)
    except ServerError as error:
        print(error)
        return render_template('index.html', form=form, error=f'An internal server error occurred. Please report this problem to the developers (code {error.code}).', hosting_information=hosting_information)
