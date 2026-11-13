"""Forms for assignments."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class AssignmentForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=100)])
    deadline = DateTimeLocalField("Deadline", format="%Y-%m-%dT%H:%M",
                                  validators=[DataRequired()])
    reference_file = FileField("Reference File (optional)")
    submit = SubmitField("Save Assignment")


class SubmissionForm(FlaskForm):
    file = FileField("Your Submission File", validators=[])
    submit = SubmitField("Submit Assignment")
