from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    price = models.IntegerField(validators=[MinValueValidator(0)], verbose_name='Preço')
    description = models.TextField(verbose_name='Descrição')
    image = models.ImageField(upload_to='products/', verbose_name='Imagem')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Categoria',
    )

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return self.name


class Order(models.Model):
    PAYMENT_LABELS = {
        'pix': 'Pix',
        'card': 'Cartão de crédito',
        'boleto': 'Boleto',
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Cliente',
    )
    name = models.CharField(max_length=150, verbose_name='Nome')
    address = models.CharField(max_length=200, verbose_name='Endereço')
    payment = models.CharField(max_length=20, verbose_name='Pagamento')
    total = models.IntegerField(verbose_name='Total')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    @property
    def payment_label(self):
        return self.PAYMENT_LABELS.get(self.payment, self.payment)

    def __str__(self):
        return f'Pedido #{self.pk} — {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Produto')
    qty = models.IntegerField(verbose_name='Quantidade')
    price = models.IntegerField(verbose_name='Preço unitário')

    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens do pedido'

    def __str__(self):
        return f'{self.qty}x {self.product.name}'
