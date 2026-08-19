from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ProdukKoperasi
from .serializers import ProdukKoperasiSerializer
from apps.core.pagination import paginated_response


class ProdukKoperasiViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return ProdukKoperasi.objects.all()

    @action(detail=False, methods=['get'], url_path='list')
    def produk_list(self, request):
        queryset = self.get_queryset()
        return paginated_response(request, queryset, ProdukKoperasiSerializer)

    @action(detail=True, methods=['get'], url_path='detail')
    def produk_detail(self, request, pk=None):
        produk = self.get_queryset().filter(pk=pk).first()
        if not produk:
            return Response(status=404)

        serializer = ProdukKoperasiSerializer(produk)
        return Response(serializer.data)
