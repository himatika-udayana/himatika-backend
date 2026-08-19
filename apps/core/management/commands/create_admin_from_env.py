from decouple import config
from django.core.management.base import BaseCommand, CommandError

from apps.users.models import User


class Command(BaseCommand):
    help = "Create or configure the production superuser from environment variables."

    def handle(self, *args, **options):
        email = config("DJANGO_SUPERUSER_EMAIL", default="").strip()
        password = config("DJANGO_SUPERUSER_PASSWORD", default="")

        if not email or not password:
            raise CommandError(
                "DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD are required."
            )

        user, created = User.objects.get_or_create(
            email=User.objects.normalize_email(email),
            defaults={
                "is_staff": True,
                "is_superuser": True,
                "is_verified": True,
            },
        )

        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS(f"Superuser created: {user.email}"))
            return

        changed = []
        if not user.is_staff:
            user.is_staff = True
            changed.append("is_staff")
        if not user.is_superuser:
            user.is_superuser = True
            changed.append("is_superuser")
        if not user.is_verified:
            user.is_verified = True
            changed.append("is_verified")

        if changed:
            user.save(update_fields=changed)

        self.stdout.write(
            self.style.SUCCESS(f"Superuser ready: {user.email}")
        )