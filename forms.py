#   © 2021 정선우 <seonwoo0808@kakao.com>
#   forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField ,SelectField , IntegerField
from wtforms.validators import DataRequired, Length

class login(FlaskForm):
    id = StringField('ID' , validators=[DataRequired()])
    password = PasswordField('PW' , validators=[DataRequired()])

class sign_up_1(FlaskForm):
    schoolcode = StringField('표준 학교 코드' , validators=[DataRequired()])

class sign_up_2(FlaskForm):
    id = StringField('ID' , validators=[DataRequired()])
    email = StringField('E-mail' , validators=[DataRequired()])
    name = StringField('이름' , validators=[DataRequired()])
    role = SelectField('신분' , choices=[(1,"교사"),(2,"학생")])
    grade = IntegerField('학년', validators=[DataRequired()])
    user_class = IntegerField('반', validators=[DataRequired()])
    no = IntegerField('번호')
    password = PasswordField('PW' , validators=[DataRequired()])
    