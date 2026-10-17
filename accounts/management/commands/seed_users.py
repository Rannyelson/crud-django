from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = 'Cria os usuários de demonstração (admin e cliente).'

    def handle(self, *args, **options):
        admin, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={
                'full_name': 'Administrador',
                'user_type': 'admin',
                'email': 'admin@techshop.com',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if admin_created:
            admin.set_password('1234')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Usuário "admin" criado (senha: 1234).'))
        else:
            self.stdout.write('Usuário "admin" já existia.')

        client, client_created = User.objects.get_or_create(
            username='cliente',
            defaults={
                'full_name': 'Cliente Demo',
                'user_type': 'client',
                'email': 'cliente@techshop.com',
            },
        )
        if client_created:
            client.set_password('1234')
            client.save()
            self.stdout.write(self.style.SUCCESS('Usuário "cliente" criado (senha: 1234).'))
        else:
            self.stdout.write('Usuário "cliente" já existia.')
