from django import forms
from .models import Vacancy

class UploadFileFormOffer(forms.Form):
    file = forms.FileField(
        label='Sube un archivo',
        help_text='Solo archivos .pdf, .txt o .md', 
        required=False,
    )
    vacancy = forms.Textarea()

class UploadVacancyForm(forms.Form):
    title = forms.CharField(max_length=100, required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)
    requirements = forms.CharField(widget=forms.Textarea, required=False)