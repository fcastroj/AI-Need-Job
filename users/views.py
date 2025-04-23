from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm
from .models import User
from django.contrib.auth.hashers import check_password
from django.contrib import messages

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username=form.cleaned_data['username'])
                if check_password(form.cleaned_data['password'], user.password):
                    user.is_authenticated = True  # Actualiza el estado de autenticación del usuario
                    user.save()
                    request.session['user_id'] = user.id
                    request.session['role'] = user.role
                    return redirect('home')  # redirige según el tipo de usuario si quieres
                else:
                    messages.error(request, 'Contraseña incorrecta.')
            except User.DoesNotExist:
                messages.error(request, 'Usuario no encontrado.')
    else:
        form = LoginForm()
    return render(request, 'loginPage.html', {'form': form})
        

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        print(request.POST)
        print(form.errors)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signupPage.html', {'form': form})

def logout(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        user.is_authenticated = False  # Actualiza el estado de autenticación del usuario
        user.save()
        del request.session['user_id']
        del request.session['role']
    else:
        messages.warning(request, "No hay un usuario autenticado.")
    request.session.flush()
    return redirect('login')

def history(request):
    return render(request, 'historyPage.html')