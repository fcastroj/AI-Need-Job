# Django
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Formularios
from .forms import SelectOutputFormat, UploadFileForm

# Modelos
from users.models import User
from offer.models import Vacancy
from .models import Resume, Applied_resume, Saved_vacancy

# Librerías externas
from openai import OpenAI  # type: ignore
from PyPDF2 import PdfReader  # type: ignore
from docx import Document  # type: ignore
from io import BytesIO  # type: ignore
from reportlab.lib import colors  # type: ignore
from reportlab.lib.pagesizes import letter  # type: ignore
from reportlab.lib.units import inch  # type: ignore
from reportlab.pdfgen import canvas  # type: ignore
import numpy as np
from textwrap import wrap


# vistas Navegación
def home(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        return render(request, 'home.html', {'user': user})
    return redirect('login')


def feed(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        vacancies = Vacancy.objects.filter(state='open').order_by('-uploaded_at')
        return render(request, 'feed.html', {'user': user, 'vacancies': vacancies})
    return redirect('login')

# Mejorar el CV
def uploadCV(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES.get('file')
            image = request.FILES.get('image')
            vacancy = form.cleaned_data['vacancy']
            cv_text = form.cleaned_data['cv_text']

            if file:
                extension = file.name.split('.')[-1].lower()
                extracted_text = extract_text_from_pdf(file) if extension == 'pdf' else extract_text(file)
            elif cv_text.strip():
                extracted_text = cv_text
            else:
                messages.warning(request, "No hay un CV inicial")
                return render(request, 'JobseekerPage.html', {'form': form, 'user': user})

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            embedding = get_embedding(extracted_text, client).tobytes()

            Resume.objects.create(
                version="1.0",
                name=file.name if file else "Manual Entry",
                vacancy_text=vacancy,
                image=image,
                extracted_text=extracted_text,
                upgraded_cv="",
                uploaded_by=user,
                embedding=embedding
            )

            messages.success(request, "CV subido y procesado con éxito")
        else:
            print(form.errors)
            messages.error(request, "Formulario no válido")
    else:
        form = UploadFileForm()

    return render(request, 'JobseekerPage.html', {'form': form, 'user': user})


# Guardar y aplicar a vacantes
def apply_vacancy(request, vacancy_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    vacancy = Vacancy.objects.get(id=vacancy_id)
    resumes = Resume.objects.filter(uploaded_by=user)

    if not resumes.exists():
        messages.warning(request, "No tienes un CV subido")
        return redirect('upload_cv')

    if request.method == 'POST':
        selected_resume_id = request.POST.get('resume_id')
        resume = Resume.objects.filter(id=selected_resume_id, uploaded_by=user).first()
        if not resume:
            messages.error(request, "Debes seleccionar un CV válido.")
            return redirect('apply', vacancy_id=vacancy_id)

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        if Applied_resume.objects.filter(resume=resume, vacancy=vacancy).exists():
            messages.warning(request, "Ya has aplicado a esta vacante con este CV")
            return redirect('feed')

        if resume.embedding is None or vacancy.embedding is None:
            resume.embedding = get_embedding(resume.extracted_text, client).tobytes()
            vacancy.embedding = get_embedding(vacancy.description + vacancy.requirements, client).tobytes()
            resume.save()
            vacancy.save()
        resume_emb = np.frombuffer(resume.embedding, dtype=np.float32)
        vacancy_emb = np.frombuffer(vacancy.embedding, dtype=np.float32)
        Applied_resume.objects.create(
            resume=resume,
            vacancy=vacancy,
            match_rate=cosine_similarity(resume_emb, vacancy_emb),
        )

        messages.success(request, "Has aplicado a la vacante con éxito")
        return redirect('feed')

    return render(request, 'select_resume.html', {
        'vacancy': vacancy,
        'resumes': resumes,
        'user': user,
    })

def save_vacancy(request, vacancy_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    vacancy = Vacancy.objects.get(id=vacancy_id)

    if Saved_vacancy.objects.filter(user=user, vacancy=vacancy).exists():
        messages.warning(request, "Ya has guardado esta vacante")
    else:
        Saved_vacancy.objects.create(user=user, vacancy=vacancy)
        messages.success(request, "Vacante guardada con éxito")

    return redirect('feed')

# funciones auxiliares
def get_embedding(text, client):
    response = client.embeddings.create(input=[text], model="text-embedding-3-small")
    return np.array(response.data[0].embedding, dtype=np.float32)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Extract text

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    return ''.join([page.extract_text() for page in pdf_reader.pages])


def extract_text(file):
    return file.read().decode('utf-8')


# Descargar CV
def download_cv_generated(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    resume = Resume.objects.filter(uploaded_by=user).first()

    if request.method == 'POST':
        form = SelectOutputFormat(request.POST)
        if form.is_valid():
            format_selected = form.cleaned_data['outputFormat']
            if format_selected == "pdf":
                return generate_pdf_response(resume.extracted_text)
            elif format_selected == "docx":
                return generate_docx_response(resume.extracted_text)
            elif format_selected == "txt":
                return generate_txt_response(resume.extracted_text)
    else:
        form = SelectOutputFormat()

    return render(request, 'jobseekerPage.html', {'form': form})

# generar CV file

def generate_docx_response(text):
    doc = Document()
    doc.add_paragraph(text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', headers={'Content-Disposition': 'attachment; filename=mejorado_cv.docx'})


def generate_pdf_response(text):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - inch
    left_margin = inch
    right_margin = width - inch
    max_width = right_margin - left_margin

    lines = text.splitlines()
    for line in lines:
        if line.startswith("# "):
            p.setFont("Helvetica-Bold", 14)
            line = line[2:]
            y -= 20
        elif line.startswith("## "):
            p.setFont("Helvetica-Bold", 12)
            line = line[3:]
            y -= 15
        elif line.startswith("- "):
            p.setFont("Helvetica", 12)
            line = f"• {line[2:]}"
        elif "**" in line:
            p.setFont("Helvetica-Bold", 12)
            line = line.replace("**", "")
        else:
            p.setFont("Helvetica", 12)

        if y <= inch:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = height - inch

        for l in wrap(line, width=int(max_width / 6)):
            if y <= inch:
                p.showPage()
                p.setFont("Helvetica", 12)
                y = height - inch
            p.drawString(left_margin, y, l)
            y -= 14

    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={'Content-Disposition': 'attachment; filename=mejorado_cv.pdf'})


def generate_txt_response(text):
    buffer = BytesIO()
    buffer.write(text.encode('utf-8'))
    buffer.seek(0)
    return HttpResponse(buffer, content_type='text/plain', headers={'Content-Disposition': 'attachment; filename=mejorado_cv.txt'})

def resume_history(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)
        resumes = Resume.objects.filter(user=user).order_by('-upload_date')
        return render(request, 'historyPage.html', {'resumes': resumes})
    else:
        return redirect('login')