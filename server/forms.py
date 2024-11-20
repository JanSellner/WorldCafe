from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, IntegerField, TextAreaField, FileField, RadioField, FloatField, HiddenField
from wtforms.validators import InputRequired, Regexp
from wtforms.widgets import NumberInput


class InputDataForm(FlaskForm):
    n_groups = IntegerField('Number of groups/days', validators=[InputRequired()], widget=NumberInput(min=2, max=8), default=3)
    selection_type = RadioField('Selection type', choices=[('text', 'Specify users manually'), ('file', 'Upload a file')], validators=[InputRequired()], default='text')
    users = TextAreaField('Users', description='One name per line.')
    file = FileField('File', validators=[FileAllowed(['csv'])], description='CSV file')
    alpha1 = FloatField('alpha1', validators=[InputRequired()], widget=NumberInput(min=0, max=1, step='any'), default=1/3)
    alpha2 = FloatField('alpha2', validators=[InputRequired()], widget=NumberInput(min=0, max=1, step='any'), default=1/3)
    alpha3 = FloatField('alpha3', validators=[InputRequired()], widget=NumberInput(min=0, max=1, step='any'), default=1/3)
    sid = HiddenField('sid', validators=[Regexp('^[a-zA-Z0-9_-]+$', message='Invalid session id.')])
    submit = SubmitField('Run!')
    progress_bar = 0

    def __init__(self, *args, **kwargs):
        # csrf protection is disabled since this would require a session cookie
        super(InputDataForm, self).__init__(meta={'csrf': False}, *args, **kwargs)
