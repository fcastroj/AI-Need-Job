from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UploadFileFormOffer
from .models import Offer
from PyPDF2 import PdfReader 
# Create your views here.

def offer(request):
    offers = Offer.objects.all()
    return render(request, 'offer.html', {'offers': offers})

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

def uploadCVS(request):
    if request.method == 'POST':
        form = UploadFileFormOffer(request.POST, request.FILES)
        if form.is_valid() and request.FILES:
            if request.POST['vacancy'] != "": # vacancy specifications
                vacancy = request.POST['vacancy']
                uploaded_file = request.FILES['file']
                file_extension = uploaded_file.name.split('.')[-1].lower()
                if file_extension == "pdf":
                    print("cv_text: \n"+ extract_text_from_pdf(uploaded_file))
                    print("\nvacancy_specifications: \n" + vacancy)
                    # process with AI
                else:
                    print("cv_text: \n" + extract_text(uploaded_file))
                    print("\nvacancy_specifications: \n" + vacancy)
                    # process with AI
            else:
               messages.warning(request,"No hay un cv inicial") 
        else:
            messages.warning(request,"No hay un cv inicial")
    else:
        form = UploadFileFormOffer()
    return render(request, 'offer.html', {'form': form})