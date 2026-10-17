from datetime import timedelta
from io import BytesIO
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from accounts.models import User

from .models import Category, Order, OrderItem, Product


def test_image():
    image = BytesIO()
    Image.new('RGB', (10, 10), color='blue').save(image, format='PNG')
    return SimpleUploadedFile('produto.png', image.getvalue(), content_type='image/png')


class MediaTestCase(TestCase):
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


class ProductCrudTests(MediaTestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='1234', user_type='admin'
        )
        self.client.force_login(self.admin)
        self.category = Category.objects.create(name='Papelaria')
        self.product = Product.objects.create(
            name='Caderno',
            price=25,
            description='Caderno universitário',
            image=test_image(),
            category=self.category,
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
                'category': self.category.pk,
            },
        )

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(Product.objects.filter(name='Caneta').exists())

    def test_create_product_negative_price_rejected(self):
        response = self.client.post(
            reverse('create'),
            {
                'name': 'Produto Invalido',
                'price': -10,
                'description': 'Preço negativo não pode ser aceito',
                'image': test_image(),
                'category': self.category.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(name='Produto Invalido').exists())

    def test_create_page_shows_category_hint_when_none(self):
        Category.objects.all().delete()

        response = self.client.get(reverse('create'))

        self.assertContains(response, 'Nenhuma categoria cadastrada')

    def test_create_page_has_no_hint_with_categories(self):
        response = self.client.get(reverse('create'))

        self.assertNotContains(response, 'Nenhuma categoria cadastrada')

    def test_product_belongs_to_category(self):
        self.assertEqual(self.product.category, self.category)
        self.assertIn(self.product, self.category.products.all())

    def test_update_product(self):
        response = self.client.post(
            reverse('update_product', args=[self.product.pk]),
            {
                'name': 'Caderno atualizado',
                'price': 30,
                'description': 'Nova descrição',
                'category': self.category.pk,
            },
        )

        self.assertRedirects(response, reverse('update'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Caderno atualizado')
        self.assertEqual(self.product.price, 30)

    def test_update_product_invalid_price(self):
        response = self.client.post(
            reverse('update_product', args=[self.product.pk]),
            {
                'name': 'Caderno atualizado',
                'price': 'abc',
                'description': 'Nova descrição',
                'category': self.category.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informe um número inteiro.')
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Caderno')

    def test_delete_product(self):
        response = self.client.post(
            reverse('delete'),
            {'product_id': self.product.pk},
        )

        self.assertRedirects(response, reverse('delete'))
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_delete_nonexistent_product_returns_404(self):
        response = self.client.post(
            reverse('delete'),
            {'product_id': 9999},
        )

        self.assertEqual(response.status_code, 404)

    def test_seed_products_is_idempotent(self):
        call_command('seed_products', verbosity=0)
        call_command('seed_products', verbosity=0)

        self.assertEqual(Product.objects.count(), 7)
        self.assertTrue(Product.objects.filter(name='Smartphone Aurora').exists())
        self.assertTrue(Product.objects.filter(name='Smartphone Aurora', category__name='Eletrônicos').exists())
        self.assertTrue(Category.objects.filter(name='Eletrônicos').exists())


class CategoryCrudTests(MediaTestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='1234', user_type='admin'
        )
        self.client.force_login(self.admin)

    def test_list_categories(self):
        Category.objects.create(name='Papelaria')

        response = self.client.get(reverse('categories'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Papelaria')

    def test_create_category(self):
        response = self.client.post(
            reverse('category_create'),
            {'name': 'Eletrônicos'},
        )

        self.assertRedirects(response, reverse('categories'))
        self.assertTrue(Category.objects.filter(name='Eletrônicos').exists())

    def test_update_category(self):
        category = Category.objects.create(name='Papelaria')

        response = self.client.post(
            reverse('category_update', args=[category.pk]),
            {'name': 'Escritório'},
        )

        self.assertRedirects(response, reverse('categories'))
        category.refresh_from_db()
        self.assertEqual(category.name, 'Escritório')

    def test_delete_category_cascades_products(self):
        category = Category.objects.create(name='Papelaria')
        Product.objects.create(
            name='Caderno',
            price=25,
            description='Caderno universitário',
            image=test_image(),
            category=category,
        )

        response = self.client.post(
            reverse('category_delete', args=[category.pk]),
        )

        self.assertRedirects(response, reverse('categories'))
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())
        self.assertFalse(Product.objects.filter(category=category).exists())

    def test_delete_nonexistent_category_returns_404(self):
        response = self.client.post(
            reverse('category_delete', args=[9999]),
        )

        self.assertEqual(response.status_code, 404)


class CartTests(MediaTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cliente', password='1234', user_type='client'
        )
        self.client.force_login(self.user)
        self.category = Category.objects.create(name='Eletrônicos')
        self.product = Product.objects.create(
            name='Fone Pulse',
            price=100,
            description='Fone sem fio',
            image=test_image(),
            category=self.category,
        )

    def add_product(self, times=1):
        for _ in range(times):
            self.client.post(reverse('add_to_cart', args=[self.product.pk]))

    def test_add_to_cart(self):
        response = self.client.post(reverse('add_to_cart', args=[self.product.pk]))

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.client.session['cart'], {str(self.product.pk): 1})

    def test_add_to_cart_twice_increments_quantity(self):
        self.add_product(times=2)

        self.assertEqual(self.client.session['cart'], {str(self.product.pk): 2})

    def test_cart_page_shows_items_and_total(self):
        self.add_product(times=2)

        response = self.client.get(reverse('cart'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fone Pulse')
        self.assertContains(response, 'R$ 200')
        self.assertEqual(response.context['total'], 200)

    def test_cart_page_empty(self):
        response = self.client.get(reverse('cart'))

        self.assertContains(response, 'Seu carrinho está vazio')

    def test_remove_from_cart(self):
        self.add_product()

        response = self.client.post(reverse('remove_from_cart', args=[self.product.pk]))

        self.assertRedirects(response, reverse('cart'))
        self.assertEqual(self.client.session['cart'], {})

    def test_checkout_flow_creates_order_and_clears_cart(self):
        self.add_product()

        response = self.client.post(
            reverse('checkout'),
            {
                'name': 'Cliente Teste',
                'address': 'Rua A, 123',
                'payment': 'pix',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compra finalizada com sucesso')
        self.assertContains(response, 'Cliente Teste')
        self.assertEqual(self.client.session['cart'], {})

        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total, 100)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product, self.product)

    def test_checkout_invalid_form_shows_errors(self):
        self.add_product()

        response = self.client.post(reverse('checkout'), {'name': '', 'address': '', 'payment': ''})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este campo é obrigatório')
        self.assertNotEqual(self.client.session['cart'], {})
        self.assertFalse(Order.objects.exists())

    def test_checkout_with_empty_cart_blocked(self):
        response = self.client.get(reverse('checkout'))

        self.assertRedirects(response, reverse('cart'))
        self.assertEqual(self.client.session.get('cart', {}), {})

    def test_cart_badge_context_processor(self):
        self.add_product(times=2)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.context['cart_count'], 2)


class AuthTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='1234', user_type='admin'
        )
        self.user = User.objects.create_user(
            username='cliente', password='1234', user_type='client'
        )

    def test_register_creates_client_and_logs_in(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'novocliente',
                'full_name': 'Novo Cliente',
                'email': 'novo@example.com',
                'password1': 'Senha-Forte#2026',
                'password2': 'Senha-Forte#2026',
            },
        )

        self.assertRedirects(response, reverse('home'))
        user = User.objects.get(username='novocliente')
        self.assertEqual(user.user_type, 'client')
        self.assertEqual(user.full_name, 'Novo Cliente')
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_admin_redirects_to_dashboard(self):
        response = self.client.post(
            reverse('login'), {'username': 'admin', 'password': '1234'}
        )

        self.assertRedirects(response, reverse('dashboard'))

    def test_login_client_redirects_to_home(self):
        response = self.client.post(
            reverse('login'), {'username': 'cliente', 'password': '1234'}
        )

        self.assertRedirects(response, reverse('home'))

    def test_login_wrong_password_shows_error(self):
        response = self.client.post(
            reverse('login'), {'username': 'cliente', 'password': 'errada'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'senha corretos')

    def test_client_blocked_from_admin_pages(self):
        self.client.force_login(self.user)

        for url_name in [
            'dashboard', 'create', 'update', 'delete',
            'category_create', 'categories', 'category_update',
        ]:
            if url_name == 'category_update':
                response = self.client.get(reverse(url_name, args=[1]))
            else:
                response = self.client.get(reverse(url_name))
            self.assertRedirects(response, reverse('home'))

    def test_anonymous_blocked_from_categories(self):
        response = self.client.get(reverse('categories'))

        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('categories')}"
        )

    def test_anonymous_blocked_from_cart(self):
        response = self.client.get(reverse('cart'))

        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('cart')}"
        )

    def test_anonymous_add_to_cart_redirects_to_login(self):
        category = Category.objects.create(name='Casa')
        product = Product.objects.create(
            name='Caneca',
            price=50,
            description='Caneca',
            image=test_image(),
            category=category,
        )

        response = self.client.post(reverse('add_to_cart', args=[product.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_logout(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_navbar_hides_admin_links_from_client(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('home'))

        self.assertNotContains(response, 'Dashboard')

    def test_navbar_shows_admin_links_for_admin(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Administração')


class DashboardTests(MediaTestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='1234', user_type='admin'
        )
        self.user = User.objects.create_user(
            username='cliente', password='1234', user_type='client'
        )
        self.category = Category.objects.create(name='Eletrônicos')
        self.fone = Product.objects.create(
            name='Fone', price=100, description='Fone', image=test_image(), category=self.category
        )
        self.mochila = Product.objects.create(
            name='Mochila', price=200, description='Mochila', image=test_image(), category=self.category
        )

        order1 = Order.objects.create(
            user=self.user, name='Cliente', address='Rua A', payment='pix', total=600
        )
        OrderItem.objects.create(order=order1, product=self.fone, qty=4, price=100)
        OrderItem.objects.create(order=order1, product=self.mochila, qty=1, price=200)

        order2 = Order.objects.create(
            user=self.user, name='Cliente', address='Rua A', payment='card', total=200
        )
        OrderItem.objects.create(order=order2, product=self.mochila, qty=1, price=200)

        old_order = Order.objects.create(
            user=self.user, name='Cliente', address='Rua A', payment='boleto', total=100
        )
        OrderItem.objects.create(order=old_order, product=self.fone, qty=1, price=100)
        Order.objects.filter(pk=old_order.pk).update(
            created_at=timezone.now() - timedelta(days=40)
        )

        self.client.force_login(self.admin)

    def test_dashboard_shows_day_and_month_sales(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['sales_day_total'], 800)
        self.assertEqual(response.context['sales_day_count'], 2)
        self.assertEqual(response.context['sales_month_total'], 800)

    def test_dashboard_shows_top_products_ranking(self):
        response = self.client.get(reverse('dashboard'))

        top = list(response.context['top_products'])
        self.assertEqual(top[0]['product__name'], 'Fone')
        self.assertEqual(top[0]['qty'], 5)
        self.assertEqual(top[0]['revenue'], 500)
        self.assertEqual(top[1]['product__name'], 'Mochila')
        self.assertContains(response, 'Produtos mais vendidos')

    def test_dashboard_shows_stats_and_recent_orders(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['clients_count'], 1)
        self.assertEqual(response.context['products_count'], 2)
        self.assertEqual(response.context['avg_ticket'], 400)
        self.assertContains(response, 'Últimos pedidos')
        self.assertContains(response, 'cliente')

    def test_client_cannot_access_dashboard(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(response, reverse('home'))
