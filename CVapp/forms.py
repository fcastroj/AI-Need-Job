from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Sube tus archivos',
        help_text='Solo archivos .pdf, .txt o .md',
        required=False,
        
    )
    vacancy = forms.Textarea()
    cv_text = forms.Textarea()

class SelectOutputFormat(forms.Form):
    outputFormat = forms.Select()