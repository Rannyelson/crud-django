from django.urls import path

from . import views

urlpatterns = [
    path('entrar', views.LoginView.as_view(), name='login'),
    path('registrar', views.register_view, name='register'),
    path('sair', views.logout_view, name='logout'),
]
