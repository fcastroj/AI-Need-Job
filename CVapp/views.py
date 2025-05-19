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


def mejorar_cv(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    resume = Resume.objects.filter(uploaded_by=user).last()
    if not resume:
        messages.error(request, "No has subido un CV aún.")
        return redirect('upload_cv')

    vacancy_text = resume.vacancy_text
    cv_text = resume.extracted_text

    prompt = (
            f"VACANTE:\n{vacancy_text}\n\n"
            f"CV ACTUAL:\n{cv_text}\n\n"
            f"""
        Eres un experto en redacción de currículums optimizados para vacantes específicas. A partir del CV actual y la descripción de la vacante que te proporciono, realiza una versión mejorada del CV que:

        - Destaque con claridad las habilidades, experiencias y logros relevantes para la vacante.
        - Reorganice o reformule el contenido para hacerlo más atractivo, convincente y profesional.
        - Elimine y omita la información que no aporte valor a la postulación.
        - Use un lenguaje proactivo, orientado a resultados y alineado con la terminología de la vacante.
        - Mantenga intacta la información personal como nombre, correo y teléfono.
        - No inventes datos, títulos ni experiencia que no estén presentes en el CV original.
        - NO incluyas ninguna introducción, comentario, conclusión ni frases como "Aquí está el CV mejorado". Solo entrega el texto final del currículum optimizado y estructurado.
        - Mejora el orden y los títulos de las secciones si es necesario para que el CV sea más claro y enfocado.

        Tu objetivo es que el CV sea visual y estratégicamente más potente para aplicar a esta vacante específica.
        """
    )


    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.7,
    )

    new_cv = response.choices[0].message.content.strip()
    resume.upgraded_cv = new_cv
    resume.save()
    if request.method == 'POST':
        form = SelectOutputFormat(request.POST)
        if form.is_valid():
            format_selected = form.cleaned_data['outputFormat']
            if format_selected == "pdf":
                return generate_pdf_response(resume.upgraded_cv)
            elif format_selected == "docx":
                return generate_docx_response(resume.upgraded_cv)
            elif format_selected == "txt":
                return generate_txt_response(resume.upgraded_cv)
    else:
        form = SelectOutputFormat()

    return render(request, 'jobseekerPage.html', {'form': form})


# Guardar y aplicar a vacantes
def apply_vacancy(request, vacancy_id):
    if 'user_id' not in request.session:
        return redirect('login')

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    user = User.objects.get(id=request.session['user_id'])
    resume = Resume.objects.filter(uploaded_by=user).first()
    vacancy = Vacancy.objects.get(id=vacancy_id)

    if not resume:
        messages.warning(request, "No tienes un CV subido")
        return redirect('upload_cv')

    if Applied_resume.objects.filter(resume=resume, vacancy=vacancy).exists():
        messages.warning(request, "Ya has aplicado a esta vacante")
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
