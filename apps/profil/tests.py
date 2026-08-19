from django.test import TestCase

from .models import FilosofiLogo, Profil


class ProfilFilosofiTests(TestCase):
    def test_filosofi_logo_can_be_linked_to_a_profile(self):
        profil = Profil.objects.create()
        filosofi = FilosofiLogo.objects.create(
            profil=profil,
            nama="Logo HIMATIKA",
            deskripsi="Simbol organisasi",
        )

        self.assertEqual(filosofi.profil, profil)
        self.assertEqual(profil.filosofi.count(), 1)
