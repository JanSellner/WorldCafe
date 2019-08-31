import base64
from io import StringIO

import pandas as pd
from flask import render_template, request, flash
from werkzeug.datastructures import CombinedMultiDict

from TableInput import TableInput
from server import app
from server.forms import InputDataForm


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
                raise ValueError('Please provide either a lists of users or upload a csv file')

            if any(df.duplicated()):
                flash(f'Duplicate lines found in the input ({str(df[df.duplicated()].iloc[:, 0].tolist())}). Please check whether your input contains some errors. The lines are not removed and the algorithm proceeds as usual.')

            if len(df) == form.n_groups.data:
                flash('The number of groups equals the number of users. It does not really make sense to run the algorithm in this case since there is only one solution. Please add more users or specify less groups.')

            table_input = TableInput(df, form.n_groups.data)

            # Generate CSV file data and wrap it in a data URI
            table_data = table_input.table_data()
            csv = table_input.csv_table(table_data)
            csv_base64 = base64.b64encode(csv.encode('utf-8')).decode('utf-8')

            return render_template('index.html', form=form, table=table_data, stats=table_input.stats(), csv_data=csv_base64)
        else:
            return render_template('index.html', form=form)
    except ValueError as error:
        return render_template('index.html', form=form, error=str(error))
