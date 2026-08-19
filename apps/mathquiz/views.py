from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsVerifiedUser

from .models import (
    QuizAttempt,
    QuizSet,
)
from .serializers import (
    LeaderboardSerializer,
    MulaiAttemptSerializer,
    QuizAttemptSerializer,
    QuizSetDetailSerializer,
    QuizSetListSerializer,
    SubmitQuizSerializer,
)
from .services import quiz


class QuizViewSet(viewsets.ViewSet):
    permission_classes = [
        IsVerifiedUser,
    ]

    def get_quiz_queryset(self):
        return (
            QuizSet.objects
            .select_related("dibuat_oleh")
            .prefetch_related("soal")
            .order_by("judul")
        )

    def get_attempt_queryset(self):
        return (
            QuizAttempt.objects
            .filter(user=self.request.user)
            .select_related("quiz_set")
            .prefetch_related("jawaban__question")
            .order_by("-waktu_mulai")
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="quiz-sets",
    )
    def quiz_sets(self, request):
        queryset = self.get_quiz_queryset()

        topik = request.query_params.get("topik")
        level = request.query_params.get("level_kesulitan")

        if topik:
            queryset = queryset.filter(topik=topik)

        if level:
            queryset = queryset.filter(
                level_kesulitan=level,
            )

        serializer = QuizSetListSerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path="detail",
    )
    def detail(self, request, pk=None):
        quiz_set = get_object_or_404(
            self.get_quiz_queryset(),
            pk=pk,
        )

        serializer = QuizSetDetailSerializer(
            quiz_set,
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="attempts",
    )
    def attempts(self, request):
        serializer = QuizAttemptSerializer(
            self.get_attempt_queryset(),
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="mulai",
    )
    def mulai(self, request):
        serializer = MulaiAttemptSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        attempt = quiz.mulai_attempt(
            request.user,
            serializer.validated_data["quiz_set"],
        )

        return Response(
            QuizAttemptSerializer(attempt).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="submit",
    )
    def submit(self, request, pk=None):
        attempt = get_object_or_404(
            self.get_attempt_queryset(),
            pk=pk,
        )

        if attempt.status == QuizAttempt.Status.SELESAI:
            return Response(
                {
                    "detail": (
                        "Attempt ini sudah selesai."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SubmitQuizSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            attempt = quiz.submit_dan_selesaikan(
                attempt,
                serializer.validated_data["answers"],
            )

        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            QuizAttemptSerializer(attempt).data,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="leaderboard",
    )
    def leaderboard(self, request):
        try:
            limit = int(
                request.query_params.get(
                    "limit",
                    10,
                )
            )
        except ValueError:
            limit = 10

        limit = max(
            1,
            min(limit, 100),
        )

        serializer = LeaderboardSerializer(
            quiz.leaderboard(limit),
            many=True,
        )

        return Response(serializer.data)