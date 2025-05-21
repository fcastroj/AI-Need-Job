from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UploadFileFormOffer, UploadVacancyForm
from .models import Vacancy
from CVapp.models import Applied_resume 
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

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def uploadCVS(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = User.objects.get(id=request.session['user_id'])

    best_cv = None
    best_score = -1
    ranking = []

    if request.method == 'POST':
        form = UploadFileFormOffer(request.POST, request.FILES)
        if form.is_valid() and request.FILES:
            if request.POST['vacancy'] != "":
                vacancy = request.POST['vacancy']
                files = request.FILES.getlist('file')
                if not files:
                    messages.warning(request, "No se seleccionaron archivos.")
                else:
                    client = OpenAI(api_key=settings.OPENAI_API_KEY)
                    vacancy_embedding = get_embedding(vacancy, client)
                    for uploaded_file in files:
                        file_extension = uploaded_file.name.split('.')[-1].lower()
                        if file_extension == "pdf":
                            cv_text = extract_text_from_pdf(uploaded_file)
                        else:
                            cv_text = extract_text(uploaded_file)
                        cv_embedding = get_embedding(cv_text, client)
                        score = cosine_similarity(vacancy_embedding, cv_embedding)
                        ranking.append({
                            'filename': uploaded_file.name,
                            'cv_text': cv_text,
                            'score': score,
                        })
                        if score > best_score:
                            best_score = score
                            best_cv = {
                                'filename': uploaded_file.name,
                                'cv_text': cv_text,
                                'score': score,
                            }
                    # Ordenar ranking de mayor a menor score
                    ranking = sorted(ranking, key=lambda x: x['score'], reverse=True)
                    messages.success(request, "Todos los archivos fueron procesados correctamente.")
                    return render(request, 'matchingPage.html', {
                        'form': form,
                        'user': user,
                        'ranking': ranking,
                        'best_cv': best_cv,
                        'vacancy': vacancy,
                    })
            else:
                messages.warning(request, "No hay un cv inicial")
        else:
            messages.warning(request, "No hay un cv inicial")
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

def change_state_vacancy(request, vacancy_id):
    if 'user_id' not in request.session:
        return redirect('login')
    vacancy = Vacancy.objects.get(id=vacancy_id)
    if vacancy.uploaded_by.id != request.session['user_id']:
        messages.error(request, 'No tienes permiso para cambiar el estado de esta vacante.')
        return redirect('history')
    if vacancy.state == 'open':
        vacancy.state = 'closed'
        vacancy.save()
        messages.success(request, 'Vacante cerrada con éxito.')
        return redirect('history')

    if vacancy.state == 'closed':
        vacancy.state = 'open'
        vacancy.save()
        messages.success(request, 'Vacante abierta con éxito.')
    return redirect('history')


def accept_resume(request, resume_id):
    if 'user_id' not in request.session:
        return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    resume = Applied_resume.objects.get(id=resume_id)
    if resume.vacancy.uploaded_by.id != user.id:
        messages.error(request, 'No tienes permiso para aceptar este CV.')
        return redirect('history')
    if resume.state != 'applied':
        messages.error(request, 'Este CV ya ha sido procesado.')
        return redirect('history')
    resume.state = 'accepted'
    resume.save()
    messages.success(request, 'CV aceptado con éxito.')
    return redirect('history')

def reject_resume(request, resume_id):
    if 'user_id' not in request.session:
        return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    resume = Applied_resume.objects.get(id=resume_id)
    if resume.vacancy.uploaded_by.id != user.id:
        messages.error(request, 'No tienes permiso para rechazar este CV.')
        return redirect('history')
    if resume.state != 'applied':
        messages.error(request, 'Este CV ya ha sido procesado.')
        return redirect('history')
    resume.state = 'rejected'
    resume.save()
    messages.success(request, 'CV rechazado con éxito.')
    return redirect('history')