"""Forms for quizzes."""
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField,
                     BooleanField, RadioField, SubmitField)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class QuizForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description")
    subject = StringField("Subject", validators=[DataRequired(), Length(max=100)])
    duration_minutes = IntegerField("Duration (minutes)",
                                    validators=[DataRequired(), NumberRange(min=1, max=300)],
                                    default=30)
    allow_retake = BooleanField("Allow Retake")
    submit = SubmitField("Save Quiz")


class QuizQuestionForm(FlaskForm):
    question_text = TextAreaField("Question", validators=[DataRequired()])
    option_a = StringField("Option A", validators=[DataRequired(), Length(max=500)])
    option_b = StringField("Option B", validators=[DataRequired(), Length(max=500)])
    option_c = StringField("Option C", validators=[DataRequired(), Length(max=500)])
    option_d = StringField("Option D", validators=[DataRequired(), Length(max=500)])
    correct_option = RadioField("Correct Answer",
                                choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
                                validators=[DataRequired()])
    marks = IntegerField("Marks", default=1,
                         validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField("Save Question")
