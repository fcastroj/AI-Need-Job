from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

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