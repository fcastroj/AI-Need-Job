from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UploadFileFormOffer, UploadVacancyForm
from .models import Vacancy
from PyPDF2 import PdfReader 
from users.models import User
import os
import numpy as np
from openai import OpenAI # type: ignore
from django.conf import settings


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
    if 'user_id' not in request.session:
        return redirect('login')
    user = User.objects.get(id=request.session['user_id'])


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
    return render(request, 'matchingPage.html', {'form': form, 'user': user})

def get_embedding(text, client):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def upload_vacancies(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        form = UploadVacancyForm(request.POST)
        if form.is_valid():
            title = request.POST['title']
            description = request.POST['description']
            requirements = request.POST['requirements']

            extracted_text = description + " " + requirements
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            embedding = get_embedding(extracted_text, client).tobytes()

            vacancy = Vacancy(
                title=title,
                description=description,
                requirements=requirements,
                uploaded_by=user,
                embedding=embedding,  
            )
            
            vacancy.save()
            messages.success(request, 'Vacante subida con éxito.')
            return redirect('history')
        else:
            messages.warning(request, 'Error al subir la vacante.')
    else:
        form = UploadVacancyForm()
    return render(request, 'offer.html', {'form':form, 'user': user})