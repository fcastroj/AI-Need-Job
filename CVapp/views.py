from django.shortcuts import render, redirect
from .forms import UploadFileForm
from PyPDF2 import PdfReader

def home(request):
    return render(request, 'home.html')

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    return text

def extract_text(file):
    text = file.read().decode('utf-8')
    return text

def uploadCV(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension == "pdf":
                print(extract_text_from_pdf(uploaded_file))
                # process with AI
            else:
                print(extract_text(uploaded_file))
                # process with AI
            return redirect('upload_cv')  
    else:
        form = UploadFileForm()
    return render(request, 'JobseekerPage.html', {'form': form})