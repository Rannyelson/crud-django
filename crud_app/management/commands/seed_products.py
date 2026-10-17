from django.core.management.base import BaseCommand

from crud_app.models import Category, Product
from crud_app.product_images import make_product_image


SEED_CATEGORIES = ['Eletrônicos', 'Acessórios', 'Casa']

SEED_PRODUCTS = [
    {
        'name': 'Smartphone Aurora',
        'price': 2499,
        'description': 'Smartphone fictício com acabamento azul, tela ampla e câmeras de alta resolução.',
        'category': 'Eletrônicos',
        'color': '#3b82f6',
    },
    {
        'name': 'Fone Pulse',
        'price': 399,
        'description': 'Fone sem fio circum-aural com isolamento acústico e almofadas confortáveis.',
        'category': 'Eletrônicos',
        'color': '#8b5cf6',
    },
    {
        'name': 'Mochila Horizonte',
        'price': 289,
        'description': 'Mochila urbana resistente com compartimentos para notebook e acessórios.',
        'category': 'Acessórios',
        'color': '#10b981',
    },
    {
        'name': 'Relógio Atlas',
        'price': 799,
        'description': 'Relógio inteligente fictício com monitoramento de atividades e notificações.',
        'category': 'Eletrônicos',
        'color': '#f59e0b',
    },
    {
        'name': 'Caixa de Som Brisa',
        'price': 249,
        'description': 'Caixa de som portátil com conexão sem fio e acabamento em tecido terracota.',
        'category': 'Eletrônicos',
        'color': '#ef4444',
    },
    {
        'name': 'Caneca Térmica Nuvem',
        'price': 119,
        'description': 'Caneca térmica de cerâmica com tampa, ideal para bebidas quentes ou frias.',
        'category': 'Casa',
        'color': '#14b8a6',
    },
]


class Command(BaseCommand):
    help = 'Cria ou atualiza os produtos fictícios usados na demonstração.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove os produtos existentes antes de carregar os dados padrão.',
        )
        parser.add_argument(
            '--reset-images',
            action='store_true',
            help='Regenera as imagens ilustradas de todos os produtos do seed.',
        )

    def handle(self, *args, **options):
        if options['reset']:
            deleted, _ = Product.objects.all().delete()
            self.stdout.write(f'{deleted} registro(s) anterior(es) removido(s).')

        categories = {
            name: Category.objects.get_or_create(name=name)[0]
            for name in SEED_CATEGORIES
        }

        created_count = 0
        updated_count = 0

        for seed in SEED_PRODUCTS:
            product, created = Product.objects.update_or_create(
                name=seed['name'],
                defaults={
                    'price': seed['price'],
                    'description': seed['description'],
                    'category': categories[seed['category']],
                },
            )

            if not product.image or options['reset_images']:
                product.image.save(
                    f'seeds/{seed["name"].lower().replace(" ", "-")}.png',
                    make_product_image(seed['name'], seed['color']),
                    save=True,
                )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeds concluídos: {created_count} criado(s) e '
                f'{updated_count} atualizado(s).'
            )
        )
