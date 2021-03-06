from flask_wtf import FlaskForm, RecaptchaField
from wtforms import IntegerField, SubmitField, FileField, TextAreaField, RadioField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired
from project import upload_images, upload_exported_templates, upload_exported_options


class AddTemplateForm(FlaskForm):
    template_export = FileField('Template definition', validators=[DataRequired(),FileAllowed(upload_exported_templates, 'JSON only!')])
    template_image = FileField('Screenshot', validators=[FileAllowed(upload_images, 'Images only!')])
    ss_options_export = FileField('Template SS Options', validators=[FileRequired(), FileAllowed(upload_exported_options, 'Options only!')])
    template_rating = IntegerField('Rating 1-5')
    template_support = TextAreaField('Additional information (external link, support team,...)')
    template_type = RadioField('Label', choices=[('pulse', 'Pulse Template')], default='pulse', validators=[DataRequired()])
    #recaptcha = RecaptchaField('')
    submit_button = SubmitField('Submit Template')