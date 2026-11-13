"""Forms for study materials."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class MaterialUploadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Length(max=1000)])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=100)])
    file = FileField("File", validators=[FileRequired()])
    submit = SubmitField("Upload Material")
