from server import app
from flask import render_template
from flask import request
from werkzeug.datastructures import CombinedMultiDict
from io import StringIO

import pandas as pd

from TableInput import TableInput
from server.forms import InputDataForm


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = InputDataForm(CombinedMultiDict((request.files, request.form)))
    try:
        if form.validate_on_submit():
            if form.selection_type.data == 'text':
                df = pd.DataFrame(form.users.data.split(), columns=['Name'])
            elif form.selection_type.data == 'file':
                file_content = form.file.data.read().decode('utf-8')
                df = pd.read_csv(StringIO(file_content))
            else:
                raise ValueError('Please provide either a lists of users or upload a csv file')

            table_input = TableInput(df, form.n_groups.data)
            return render_template('index.html', form=form, table=table_input.table_data(), stats=table_input.stats())
        else:
            return render_template('index.html', form=form)
    except ValueError as error:
        return render_template('index.html', form=form, error=str(error))
