from django.db import models


class SingletonModel(models.Model):
    """
    Abstract base class untuk model yang hanya boleh punya 1 row,
    misalnya Profil dan PengaturanWebsite.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        kwargs.pop('force_insert', None)  # supaya UPDATE, bukan selalu INSERT
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # cegah penghapusan singleton

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj
