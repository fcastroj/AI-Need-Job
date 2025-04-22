from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UploadFileForm, SelectOutputFormat, UploadImageForm
from PyPDF2 import PdfReader # type: ignore
from docx import Document # type: ignore
from io import BytesIO # type: ignore
from reportlab.lib.units import inch # type: ignore
from reportlab.pdfgen import canvas # type: ignore
from reportlab.lib import colors # type: ignore
from reportlab.lib.pagesizes import letter # type: ignore
from django.core.files.storage import FileSystemStorage


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

def upload_image(request):
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            uploaded_image_url = fs.url(filename)
            return render(request, 'JobseekerPage.html', {
                'uploaded_image_url': uploaded_image_url,
                'image_success': True
            })
    else:
        form = UploadImageForm()
    return render(request, 'JobseekerPage.html', {'image_form': form})

def uploadCV(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid() and request.FILES:
            uploaded_file = request.FILES['file']
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if request.POST['vacancy'] != "": # vacancy specifications
                vacancy = request.POST['vacancy']
                if file_extension == "pdf":
                    print("cv_text: \n"+ extract_text_from_pdf(uploaded_file))
                    print("vacancy_specifications:" + vacancy)
                    # process with AI
                else:
                    print("cv_text: \n" + extract_text(uploaded_file))
                    print("\nvacancy_specifications: \n" + vacancy)
                    # process with AI
            # return redirect('upload_cv')  
        elif request.POST['cvText']:
            cv_text = request.POST['cvText']
            if request.POST['vacancy'] != "": # vacancy specifications
                vacancy = request.POST['vacancy']
                print("cv_text: \n" + cv_text)
                print("\nvacancy_specifications: \n" + vacancy)
                # process with AI
        else:
            messages.warning(request,"No hay un cv inicial")
    else:
        form = UploadFileForm()
    return render(request, 'JobseekerPage.html', {'form': form})

#EXAMPLE TEXT
text = "EXAMPLE OF OUTPUT SELECTION AND DOWNLOAD. " \
"AI-Need-Job"

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
