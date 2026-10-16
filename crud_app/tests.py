from io import BytesIO
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Product


def test_image():
    image = BytesIO()
    Image.new('RGB', (10, 10), color='blue').save(image, format='PNG')
    return SimpleUploadedFile('produto.png', image.getvalue(), content_type='image/png')


class ProductCrudTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.media_directory = TemporaryDirectory(dir=settings.BASE_DIR)
        cls.media_override = override_settings(MEDIA_ROOT=cls.media_directory.name)
        cls.media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.media_override.disable()
        cls.media_directory.cleanup()

    def setUp(self):
        self.product = Product.objects.create(
            name='Caderno',
            price=25,
            description='Caderno universitário',
            image=test_image(),
        )

    def test_list_products(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Caderno')

    def test_create_product(self):
        response = self.client.post(
            reverse('create'),
            {
                'name': 'Caneta',
                'price': 5,
                'description': 'Caneta azul',
                'image': test_image(),
            },
        )

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(Product.objects.filter(name='Caneta').exists())

    def test_update_product(self):
        response = self.client.post(
            reverse('update'),
            {
                'product_id': self.product.pk,
                'name': 'Caderno atualizado',
                'price': 30,
                'description': 'Nova descrição',
            },
        )

        self.assertRedirects(response, reverse('update'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Caderno atualizado')
        self.assertEqual(self.product.price, 30)

    def test_delete_product(self):
        response = self.client.post(
            reverse('delete'),
            {'product_id': self.product.pk},
        )

        self.assertRedirects(response, reverse('delete'))
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_seed_products_is_idempotent(self):
        call_command('seed_products', verbosity=0)
        call_command('seed_products', verbosity=0)

        self.assertEqual(Product.objects.count(), 7)
        self.assertTrue(Product.objects.filter(name='Smartphone Aurora').exists())
