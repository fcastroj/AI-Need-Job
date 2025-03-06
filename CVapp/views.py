from django.shortcuts import render, redirect
from .forms import UploadFileForm

def home(request):
    return render(request, 'home.html')

def uploadCV(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            # process  uploaded file 
            return redirect('upload_cv')  
    else:
        form = UploadFileForm()
    return render(request, 'JobseekerPage.html', {'form': form})