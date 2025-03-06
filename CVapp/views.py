from django.shortcuts import render, redirect
from .forms import UploadFileForm
import PyPDF2 # type: ignore
import os

def home(request):
    return render(request, 'home.html')

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        extracted_text = ""
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            extracted_text += page.extract_text()
        
        return extracted_text

def extract_text(md_path):
    with open(md_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def uploadCV(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            file_name = uploaded_file.file.name  
            file_extension = os.path.splitext(file_name)[1]
            file_path = uploaded_file.file.path 
            if file_extension == ".pdf":
                print(extract_text_from_pdf(file_path))
                # process with AI
            else:
                print(extract_text(file_path))
                # process with AI
            return redirect('upload_cv')  
    else:
        form = UploadFileForm()
    return render(request, 'JobseekerPage.html', {'form': form})