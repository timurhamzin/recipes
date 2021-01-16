from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from recipes.forms import SignUpForm, SignInForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm


def register(request):
    if request.method == 'POST':
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(reverse('index'))
    else:
        form = UserCreationForm()
    return render(request, 'reg.html', {'form': form, 'errors': form.errors})


def auth(request):
    errors = {}
    if request.method == 'POST':
        form = SignInForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            if user:
                login(request, user)
                return redirect(reverse('index'))
            else:
                errors = {'__all__': ['User and password didn\'t match']}
        else:
            errors = form.errors
    else:
        form = SignInForm()
    return render(request, 'authForm.html',
                  {'form': form, 'errors': errors})


@login_required
def signout(request):
    logout(request)
    return redirect(reverse('index'))


def password_change_done(request):
    return redirect(reverse('index'))
