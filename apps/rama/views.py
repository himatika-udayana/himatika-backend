from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsVerifiedUser

from .models import (
    Semester,
    KategoriAspirasi,
    RamaSubmission,
)
from .serializers import (
    RamaFormSerializer,
    RamaSubmissionSerializer,
    RamaSubmissionDetailSerializer,
)


class RamaViewSet(viewsets.ViewSet):
    permission_classes = [IsVerifiedUser]

    @action(
        detail=False,
        methods=["get"],
        url_path="form",
    )
    def form(self, request):
        semester = Semester.objects.filter(
            aktif=True
        ).first()

        if semester is None:
            return Response(
                {"detail": "Belum ada semester aktif."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        submission = (
            RamaSubmission.objects.filter(
                user=request.user,
                semester=semester,
            )
            .prefetch_related("aspirasi__kategori")
            .first()
        )

        if submission:
            serializer = RamaFormSerializer({
                "sudah_submit": True,
                "submission": submission,
            })
        else:
            serializer = RamaFormSerializer({
                "sudah_submit": False,
                "semester": semester,
                "kategori": KategoriAspirasi.objects.order_by("urutan"),
            })

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="submit",
    )
    def submit(self, request):
        serializer = RamaSubmissionSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        submission = serializer.save()

        return Response(
            RamaSubmissionDetailSerializer(submission).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="hasil",
    )
    def hasil(self, request):
        submission = (
            RamaSubmission.objects.filter(
                user=request.user,
            )
            .prefetch_related("aspirasi__kategori")
            .select_related("semester")
            .order_by("-tanggal_submit")
            .first()
        )

        if submission is None:
            return Response(
                {"detail": "Belum pernah mengisi RAMA."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RamaSubmissionDetailSerializer(submission)
        return Response(serializer.data)


RamaAspirasiViewSet = RamaViewSet