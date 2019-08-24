from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, TextAreaField, FileField
from wtforms.validators import DataRequired
from wtforms.widgets.html5 import NumberInput
from flask_wtf.file import FileAllowed


class InputDataForm(FlaskForm):
    n_groups = IntegerField('Number of groups', validators=[DataRequired()], widget=NumberInput(min=2), default=3)
    users = TextAreaField('Users', description='One name per line')
    file = FileField('File', validators=[FileAllowed(['csv'])])
    submit = SubmitField('Start calculation')
