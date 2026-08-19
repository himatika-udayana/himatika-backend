from rest_framework import serializers

from .models import (
    QuizAttempt,
    QuizQuestion,
    QuizSet,
    UserPoint,
)


class QuizQuestionSerializer(serializers.ModelSerializer):
    """
    Soal yang dikirim ke frontend.

    Jawaban benar tidak pernah dikirim.
    """

    class Meta:
        model = QuizQuestion
        fields = (
            "id",
            "urutan",
            "tipe",
            "teks_soal",
            "poin",
            "pilihan_a",
            "pilihan_b",
            "pilihan_c",
            "pilihan_d",
            "pilihan_e",
        )


class QuizSetListSerializer(serializers.ModelSerializer):
    """
    Serializer untuk halaman daftar quiz.
    """

    jumlah_soal = serializers.IntegerField(
        read_only=True,
    )

    total_poin_maksimal = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = QuizSet
        fields = (
            "id",
            "judul",
            "topik",
            "level_kesulitan",
            "jumlah_soal",
            "total_poin_maksimal",
        )


class QuizSetDetailSerializer(serializers.ModelSerializer):
    """
    Detail quiz beserta seluruh soal.
    """

    soal = QuizQuestionSerializer(
        many=True,
        read_only=True,
    )

    dibuat_oleh_nama = serializers.CharField(
        source="dibuat_oleh.username",
        read_only=True,
        default=None,
    )

    jumlah_soal = serializers.IntegerField(
        read_only=True,
    )

    total_poin_maksimal = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = QuizSet
        fields = (
            "id",
            "judul",
            "deskripsi",
            "topik",
            "level_kesulitan",
            "jumlah_soal",
            "total_poin_maksimal",
            "dibuat_oleh_nama",
            "soal",
        )


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_judul = serializers.CharField(
        source="quiz_set.judul",
        read_only=True,
    )

    class Meta:
        model = QuizAttempt
        fields = (
            "id",
            "quiz_set",
            "quiz_judul",
            "skor",
            "total_poin",
            "status",
            "waktu_mulai",
            "waktu_selesai",
        )

        read_only_fields = fields


class MulaiAttemptSerializer(serializers.Serializer):
    quiz_set = serializers.PrimaryKeyRelatedField(
        queryset=QuizSet.objects.all(),
    )


class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(
        min_value=1,
    )

    jawaban = serializers.CharField(
        trim_whitespace=True,
        allow_blank=True,
    )


class SubmitQuizSerializer(serializers.Serializer):
    """
    Submit seluruh jawaban sekaligus.
    """

    answers = SubmitAnswerSerializer(
        many=True,
        allow_empty=False,
    )


class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = UserPoint
        fields = (
            "username",
            "total_poin",
            "total_quiz",
            "total_benar",
        )