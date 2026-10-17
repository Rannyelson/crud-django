from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import RegisterForm


class LoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        if self.request.user.is_admin:
            return reverse('dashboard')
        return reverse('home')

    def form_valid(self, form):
        messages.success(self.request, f'Bem-vindo(a), {form.get_user().username}!')
        return super().form_valid(form)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Conta criada com sucesso. Boas compras!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, 'Você saiu da sua conta.')
    return redirect('home')
