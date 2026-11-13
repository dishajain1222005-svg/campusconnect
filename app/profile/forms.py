"""Profile edit forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.models import User
from flask_login import current_user


class ProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    roll_no = StringField("Roll No.", validators=[Optional(), Length(max=40)])
    department = StringField("Department", validators=[Optional(), Length(max=80)])
    submit = SubmitField("Update Profile")

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user and user.id != current_user.id:
            raise ValidationError("Email already in use by another account.")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired()])
    submit = SubmitField("Change Password")

    def validate_confirm_password(self, field):
        if field.data != self.new_password.data:
            raise ValidationError("Passwords must match.")
