from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UploadFileForm, SelectOutputFormat
from PyPDF2 import PdfReader # type: ignore
from docx import Document # type: ignore
from io import BytesIO # type: ignore
from reportlab.lib.units import inch # type: ignore
from reportlab.pdfgen import canvas # type: ignore
from reportlab.lib import colors # type: ignore
from reportlab.lib.pagesizes import letter # type: ignore
from users.models import User
from offer.models import Vacancy
from .models import Resume, Applied_resume, Saved_vacancy
import os
import numpy as np
from openai import OpenAI # type: ignore
from django.conf import settings

def home(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)
        return render(request, 'home.html', {'user': user})
    else:
        return redirect('login')

def feed(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)
        vacancies = Vacancy.objects.filter(state='open').order_by('-uploaded_at')
        return render(request, 'feed.html', {'user': user, 'vacancies': vacancies})
    else:
        return redirect('login')
    
def apply_vacancy(request, vacancy_id):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    if 'user_id' not in request.session:
        return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    resume = Resume.objects.filter(uploaded_by=user).first()  # Assuming the user has only one resume
    vacancy = Vacancy.objects.get(id=vacancy_id)
    if not resume:
        messages.warning(request, "No tienes un CV subido")
        return redirect('upload_cv')
    if Applied_resume.objects.filter(resume=resume, vacancy=vacancy).exists():
        messages.warning(request, "Ya has aplicado a esta vacante")
        return redirect('feed')
    if resume.embedding is None or vacancy.embedding is None:
        resume.embedding = get_embedding(resume.extracted_text, client)  # Ensure the resume has an embedding
        vacancy.embedding = get_embedding(vacancy.description+ vacancy.requirements, client)
        resume.save()
        vacancy.save()
    applied_resume = Applied_resume.objects.create(
        resume=resume,
        vacancy=vacancy,
        match_rate=cosine_similarity(resume.embedding, vacancy.embedding),  # Placeholder for the match rate
    )
    applied_resume.save()
    messages.success(request, "Has aplicado a la vacante con éxito")
    return redirect('feed')

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

def get_embedding(text, client):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
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

            extracted_text = ""
            if file:
                extension = file.name.split('.')[-1].lower()
                if extension == 'pdf':
                    extracted_text = extract_text_from_pdf(file)
                else:
                    extracted_text = extract_text(file)
            elif cv_text != "":
                extracted_text = cv_text
            else:
                messages.warning(request, "No hay un CV inicial") 
                return render(request, 'JobseekerPage.html', {'form': form, 'user': user})
            
            
            client = OpenAI(api_key=os.environ.get('openai_api_key'))
            embedding = get_embedding(extracted_text, client)

            resume = Resume.objects.create(
                version="1.0",
                name=file.name if file else "Manual Entry",
                vacancy_text=vacancy,
                image=image,
                extracted_text=extracted_text,
                upgraded_cv="",
                uploaded_by=user,
                embedding=embedding.tolist() if embedding is not None else None
            )
            resume.save()
            messages.success(request, "CV subido y procesado con éxito")
            # return redirect('process_cv', resume_id=resume.id)
        else:
            messages.error(request, "Formulario no válido")
    else:
        form = UploadFileForm()

    return render(request, 'JobseekerPage.html', {'form': form, 'user': user})



def generate_docx_response(text):
    """Genera una respuesta en formato DOCX."""
    doc = Document()
    doc.add_paragraph(text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=mejorado_cv.docx'
    return response

def generate_pdf_response(text):
    """Genera una respuesta en formato PDF usando ReportLab con ajuste de estilo y ajuste de línea."""
    from textwrap import wrap
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y_position = height - inch  # Posición inicial para el contenido

    # Margen y ancho máximo de línea
    left_margin = 1 * inch
    right_margin = width - inch
    max_width = right_margin - left_margin  # Ancho disponible para el texto

    # Estilos de fuente
    p.setFont("Helvetica", 12)

    # Divide el texto en líneas según el formato Markdown
    lines = text.splitlines()

    for line in lines:
        # Estilos para encabezados
        if line.startswith("## "):  # Encabezado de segundo nivel
            p.setFont("Helvetica-Bold", 12)
            line = line[3:]
            y_position -= 15  # Espacio adicional antes del encabezado
        elif line.startswith("# "):  # Encabezado de primer nivel
            p.setFont("Helvetica-Bold", 14)
            line = line[2:]
            y_position -= 20
        elif line.startswith("- "):  # Elemento de lista
            p.setFont("Helvetica", 12)
            line = f"• {line[2:]}"  # Cambia el guion por un punto de viñeta
        elif "**" in line:  # Texto en negrita
            line = line.replace("**", "")  # Elimina los asteriscos dobles
            p.setFont("Helvetica-Bold", 12)
        else:
            p.setFont("Helvetica", 12)  # Fuente normal para el resto del texto

        # Ajuste para nueva página si el espacio no es suficiente
        if y_position <= inch:
            p.showPage()
            p.setFont("Helvetica", 12)
            y_position = height - inch

        # Ajuste de línea con ancho máximo
        wrapped_lines = wrap(line, width=int(max_width / 6))  # Ajusta el ancho dividiendo por un factor

        # Dibujar cada línea envuelta
        for wrapped_line in wrapped_lines:
            if y_position <= inch:  # Nueva página si no hay espacio
                p.showPage()
                p.setFont("Helvetica", 12)
                y_position = height - inch

            p.drawString(left_margin, y_position, wrapped_line)
            y_position -= 14  # Espacio entre las líneas

    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=mejorado_cv.pdf'
    return response

def generate_txt_response(text):
    """Generates a response to download a .txt file."""
    buffer = BytesIO()
    buffer.write(text.encode('utf-8'))  # Encode text to bytes
    buffer.seek(0)  # Reset the buffer position

    response = HttpResponse(buffer, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=mejorado_cv.txt'
    return response

def download_cv_generated(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)
    else:
        return redirect('login')
    if request.method == 'POST':
        form = SelectOutputFormat(request.POST)
        if form.is_valid():
            outputFormat = request.POST['outputFormat']
            if outputFormat == "pdf":
                return generate_pdf_response("Hola PDF")
            if outputFormat == "docx":
                return generate_docx_response("Hola Docx")  
            if outputFormat == "txt":
                return generate_txt_response("Hola Txt")
        else:
            form = SelectOutputFormat()
    return render(request, 'jobseekerPage.html')
