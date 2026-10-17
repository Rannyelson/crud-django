from django import forms
from .models import Category, Product

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=100, label='Nome completo')
    address = forms.CharField(
        max_length=200,
        label='Endereço de entrega',
        widget=forms.Textarea(attrs={'rows': 3}),
    )
    payment = forms.ChoiceField(
        label='Forma de pagamento',
        choices=[
            ('pix', 'Pix'),
            ('card', 'Cartão de crédito'),
            ('boleto', 'Boleto'),
        ],
    )