from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Sube un archivo',
        help_text='Solo archivos .pdf, .txt o .md'
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        allowed_extensions = ['pdf', 'txt', 'md']
        extension = file.name.split('.')[-1].lower()

        # Validar que la extensión esté permitida
        if extension not in allowed_extensions:
            raise forms.ValidationError('Solo se permiten archivos .pdf, .txt o .md.')

        return file
