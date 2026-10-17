from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Administrador'),
        ('client', 'Cliente'),
    ]

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='client',
        verbose_name='Tipo de usuário',
    )
    full_name = models.CharField(max_length=150, blank=True, verbose_name='Nome completo')

    @property
    def is_admin(self):
        return self.user_type == 'admin'

    @property
    def is_client(self):
        return self.user_type == 'client'
