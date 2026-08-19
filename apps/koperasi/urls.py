from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProdukKoperasiViewSet

router = DefaultRouter()
router.register(r'', ProdukKoperasiViewSet, basename='koperasi')

urlpatterns = router.urls
