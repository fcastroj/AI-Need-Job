from django import forms

class UploadFileFormOffer(forms.Form):
    file = forms.FileField(
        label='Sube un archivo',
        help_text='Solo archivos .pdf, .txt o .md', 
        required=False,
    )
    vacancy = forms.Textarea()
