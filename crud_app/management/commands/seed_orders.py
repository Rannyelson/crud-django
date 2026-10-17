import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from crud_app.models import Order, OrderItem, Product


class Command(BaseCommand):
    help = 'Gera pedidos fictícios dos últimos 30 dias para o dashboard.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--total',
            type=int,
            default=45,
            help='Número de pedidos fictícios a gerar (padrão: 45).',
        )

    def handle(self, *args, **options):
        client, created = User.objects.get_or_create(
            username='cliente',
            defaults={'full_name': 'Cliente Demo', 'user_type': 'client'},
        )
        if created:
            client.set_password('1234')
            client.save()

        products = list(Product.objects.all())
        if not products:
            self.stdout.write(self.style.ERROR('Nenhum produto. Rode seed_products antes.'))
            return

        Order.objects.filter(user=client).delete()

        rng = random.Random(42)
        now = timezone.now()
        created = 0
        for _ in range(options['total']):
            days_ago = rng.randint(0, 29)
            order_date = now - timedelta(
                days=days_ago,
                hours=rng.randint(0, 12),
                minutes=rng.randint(0, 59),
            )

            chosen = rng.sample(products, k=rng.randint(1, min(3, len(products))))
            total = 0
            order = Order.objects.create(
                user=client,
                name=client.full_name or client.username,
                address='Rua da Demonstração, 123 — Fortaleza/CE',
                payment=rng.choice(['pix', 'card', 'boleto']),
                total=0,
            )
            for product in chosen:
                qty = rng.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    qty=qty,
                    price=product.price,
                )
                total += product.price * qty
            order.total = total
            order.save(update_fields=['total'])
            order.created_at = order_date
            order.save(update_fields=['created_at'])
            created += 1

        self.stdout.write(
            self.style.SUCCESS(f'{created} pedido(s) fictício(s) criado(s) para o dashboard.')
        )
