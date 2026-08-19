from django.urls import path

from .views import ProfilViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', ProfilViewSet, basename='profil')

urlpatterns = router.urls