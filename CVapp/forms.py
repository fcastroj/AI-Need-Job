from django import forms
from .models import CV

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ['file']
