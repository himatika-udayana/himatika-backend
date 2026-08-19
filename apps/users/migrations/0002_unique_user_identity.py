from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                condition=~Q(nama_lengkap=""),
                fields=("nama_lengkap",),
                name="unique_user_nama_lengkap",
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                condition=~Q(nim=""),
                fields=("nim",),
                name="unique_user_nim",
            ),
        ),
    ]