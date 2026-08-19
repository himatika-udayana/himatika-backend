from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsVerifiedUser
from .models import Arsip
from .serializers import ArsipSerializer
from apps.core.pagination import paginated_response


class ArsipViewSet(viewsets.ViewSet):
    permission_classes = [IsVerifiedUser]

    def get_queryset(self):
        return (
            Arsip.objects
            .select_related("diunggah_oleh")
            .order_by("-tahun", "-tanggal_upload")
        )

    @action(detail=False, methods=['get'], url_path='')
    def arsip_list(self, request):
        queryset = self.get_queryset()
        return paginated_response(request, queryset, ArsipSerializer)

    @action(detail=True, methods=['get'], url_path='')
    def arsip_detail(self, request, pk=None):
        arsip = self.get_queryset().filter(pk=pk).first()
        if not arsip:
            return Response(status=404)
        serializer = ArsipSerializer(arsip)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        arsip = self.get_queryset().filter(pk=pk).first()
        if not arsip:
            return Response(status=404)

        # existing storage backend handles generating file response URL/path
        return Response({"download_url": arsip.file.url})
