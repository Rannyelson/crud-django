from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, label='Nome completo')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'full_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.user_type = 'client'
        if commit:
            user.save()
        return user
