"""
Comando personalizado para crear el superusuario adicional zyfalo.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Crea el superusuario adicional zyfalo'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'zyfalo'
        email = 'zyfalo@admin.com'
        password = 'admin123'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Superusuario "{username}" creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Superusuario "{username}" ya existe')
            )
