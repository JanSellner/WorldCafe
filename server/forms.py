from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, TextAreaField, FileField, RadioField
from wtforms.validators import DataRequired
from wtforms.widgets.html5 import NumberInput
from flask_wtf.file import FileAllowed


class InputDataForm(FlaskForm):
    n_groups = IntegerField('Number of groups/days', validators=[DataRequired()], widget=NumberInput(min=2, max=8), default=3)
    selection_type = RadioField('Selection type', choices=[('text', 'Specify users manually'), ('file', 'Upload a file')], validators=[DataRequired()], default='text')
    users = TextAreaField('Users', description='One name per line.')
    file = FileField('File', validators=[FileAllowed(['csv'])], description='CSV file')
    submit = SubmitField('Run!')
    progress_bar = 0
