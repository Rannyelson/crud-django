from pathlib import Path

from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from crud_app.models import Product


SEED_PRODUCTS = [
    {
        'name': 'Smartphone Aurora',
        'price': 2499,
        'description': 'Smartphone fictício com acabamento azul, tela ampla e câmeras de alta resolução.',
        'image': 'smartphone-azul.png',
    },
    {
        'name': 'Fone Pulse',
        'price': 399,
        'description': 'Fone sem fio circum-aural com isolamento acústico e almofadas confortáveis.',
        'image': 'fone-sem-fio.png',
    },
    {
        'name': 'Mochila Horizonte',
        'price': 289,
        'description': 'Mochila urbana resistente com compartimentos para notebook e acessórios.',
        'image': 'mochila-urbana.png',
    },
    {
        'name': 'Relógio Atlas',
        'price': 799,
        'description': 'Relógio inteligente fictício com monitoramento de atividades e notificações.',
        'image': 'relogio-inteligente.png',
    },
    {
        'name': 'Caixa de Som Brisa',
        'price': 249,
        'description': 'Caixa de som portátil com conexão sem fio e acabamento em tecido terracota.',
        'image': 'caixa-de-som.png',
    },
    {
        'name': 'Caneca Térmica Nuvem',
        'price': 119,
        'description': 'Caneca térmica de cerâmica com tampa, ideal para bebidas quentes ou frias.',
        'image': 'caneca-termica.png',
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

    def handle(self, *args, **options):
        if options['reset']:
            deleted, _ = Product.objects.all().delete()
            self.stdout.write(f'{deleted} registro(s) anterior(es) removido(s).')

        assets_directory = Path(__file__).resolve().parents[2] / 'seed_assets'
        created_count = 0
        updated_count = 0

        for seed in SEED_PRODUCTS:
            image_filename = seed['image']
            image_target = f'products/seeds/{image_filename}'
            product, created = Product.objects.update_or_create(
                name=seed['name'],
                defaults={
                    'price': seed['price'],
                    'description': seed['description'],
                },
            )

            if not default_storage.exists(image_target):
                with (assets_directory / image_filename).open('rb') as image_file:
                    default_storage.save(image_target, File(image_file))

            if product.image.name != image_target:
                product.image.name = image_target
                product.save(update_fields=['image'])

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
