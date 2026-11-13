"""Forms for notices."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class AnnouncementForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    body = TextAreaField("Body", validators=[DataRequired()])
    is_important = BooleanField("Mark as Important")
    publish_date = DateTimeLocalField("Publish Date", format="%Y-%m-%dT%H:%M",
                                      validators=[Optional()])
    submit = SubmitField("Publish")
