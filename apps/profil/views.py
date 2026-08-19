from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import FilosofiLogo, Misi, Pengurus, Profil, ProgramKerja, PengaturanWebsite, Timeline
from .serializers import (
    FilosofiSerializer,
    MisiSerializer,
    PengurusSerializer,
    ProgramKerjaSerializer,
    ProfilSerializer,
    PengaturanWebsiteSerializer,
    TimelineSerializer,
)


class ProfilViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Profil.objects.all()

    def list(self, request):
        obj = self.get_queryset().first()
        if not obj:
            return Response(status=404)

        serializer = ProfilSerializer(obj)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="detail")
    def profil(self, request):
        obj = self.get_queryset().first()
        if not obj:
            return Response(status=404)

        serializer = ProfilSerializer(obj)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="misi")
    def misi(self, request):
        queryset = Misi.objects.all()
        serializer = MisiSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="timeline")
    def timeline(self, request):
        queryset = Timeline.objects.all()
        serializer = TimelineSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="pengurus")
    def pengurus(self, request):
        queryset = Pengurus.objects.all()
        serializer = PengurusSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="proker")
    def proker(self, request):
        queryset = ProgramKerja.objects.all()
        serializer = ProgramKerjaSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="filosofi")
    def filosofi(self, request):
        queryset = FilosofiLogo.objects.all()
        serializer = FilosofiSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="kontak")
    def kontak(self, request):
        obj = PengaturanWebsite.objects.first()
        if not obj:
            return Response(status=404)

        serializer = PengaturanWebsiteSerializer(obj)
        return Response(serializer.data)
