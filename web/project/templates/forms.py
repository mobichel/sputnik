from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from project import upload_images, upload_exported_templates, upload_exported_options


class AddTemplateForm(FlaskForm):
    template_export = FileField('Template definition', validators=[DataRequired(),FileAllowed(upload_exported_templates, 'JSON only!')])
    template_image = FileField('Template screenshot', validators=[FileRequired(), FileAllowed(upload_images, 'Images only!')])
    ss_options_export = FileField('Template SS Options', validators=[FileRequired(), FileAllowed(upload_exported_options, 'Options only!')])
    template_rating = IntegerField('Rating 1-5')