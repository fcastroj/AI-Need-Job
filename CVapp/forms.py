from django import forms
from .models import CV
from django.core.exceptions import ValidationError
import os 

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')

        ext = os.path.splitext(file.name)[1].lower()

        valid_extensions = ['.pdf', '.md', '.txt']

        if ext not in valid_extensions:
            raise ValidationError(f"Solo se permiten archivos con extensiones: {', '.join(valid_extensions)}")

        return file
