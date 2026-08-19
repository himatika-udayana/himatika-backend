from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from ..models import QuizSet, QuizQuestion, QuizAttempt, QuizAnswer, UserPoint


def mulai_attempt(user, quiz_set: QuizSet) -> QuizAttempt:
    return QuizAttempt.objects.create(user=user, quiz_set=quiz_set)


def submit_jawaban(attempt: QuizAttempt, question: QuizQuestion, jawaban: str) -> QuizAnswer:
    is_correct = question.cek_jawaban(jawaban)
    obj, _created = QuizAnswer.objects.update_or_create(
        attempt=attempt,
        question=question,
        defaults={"jawaban_dipilih": (jawaban or "").strip(), "is_correct": is_correct},
    )
    return obj


@transaction.atomic
def submit_dan_selesaikan(attempt: QuizAttempt, daftar_jawaban: list) -> QuizAttempt:
    """
    daftar_jawaban = [{"question_id": 1, "jawaban": "B"}, ...]
    Entry point utama dipakai view — submit SEMUA jawaban sekaligus di akhir,
    lalu langsung hitung skor & selesaikan attempt (sesuai keputusan: batch,
    bukan 1 API call per soal).
    """
    if attempt.status == QuizAttempt.Status.SELESAI:
        raise ValueError("Attempt ini sudah selesai, tidak bisa disubmit ulang.")

    soal_di_quiz_ini = {q.id: q for q in attempt.quiz_set.soal.all()}
    for item in daftar_jawaban:
        question = soal_di_quiz_ini.get(item["question_id"])
        if question is None:
            raise ValueError(f"Soal id={item['question_id']} bukan bagian dari quiz_set ini.")
        submit_jawaban(attempt, question, item.get("jawaban", ""))

    return selesaikan_attempt(attempt)


@transaction.atomic
def selesaikan_attempt(attempt: QuizAttempt) -> QuizAttempt:
    jawaban_qs = list(attempt.jawaban.select_related("question"))
    total_poin = sum(j.question.poin for j in jawaban_qs if j.is_correct)
    jumlah_benar = sum(1 for j in jawaban_qs if j.is_correct)
    total_soal = attempt.quiz_set.soal.count()
    skor = round((jumlah_benar / total_soal) * 100) if total_soal else 0

    attempt.skor = skor
    attempt.total_poin = total_poin
    attempt.status = QuizAttempt.Status.SELESAI
    attempt.waktu_selesai = timezone.now()
    attempt.save()

    update_user_point(attempt.user)
    return attempt


@transaction.atomic
def update_user_point(user) -> UserPoint:
    """
    Recompute PENUH dari QuizAttempt (bukan increment) supaya selalu akurat
    walau ada retry dengan skor lebih rendah dari attempt sebelumnya. Poin
    di-cap ke SKOR TERBAIK per quiz_set, baru dijumlah lintas quiz_set.
    """
    best_per_quiz = (
        QuizAttempt.objects.filter(user=user, status=QuizAttempt.Status.SELESAI)
        .values("quiz_set")
        .annotate(best_poin=Max("total_poin"))
    )

    total_poin = 0
    total_benar = 0
    total_quiz = 0

    for row in best_per_quiz:
        best_attempt = (
            QuizAttempt.objects.filter(
                user=user,
                quiz_set_id=row["quiz_set"],
                status=QuizAttempt.Status.SELESAI,
                total_poin=row["best_poin"],
            )
            .order_by("-waktu_selesai")
            .first()
        )
        total_poin += row["best_poin"]
        total_quiz += 1
        if best_attempt:
            total_benar += best_attempt.jawaban.filter(is_correct=True).count()

    user_point, _created = UserPoint.objects.get_or_create(user=user)
    user_point.total_poin = total_poin
    user_point.total_quiz = total_quiz
    user_point.total_benar = total_benar
    user_point.save()
    return user_point


def leaderboard(limit: int = 10):
    """
    UserPoint SELALU sinkron (di-recompute tiap attempt selesai), jadi
    leaderboard tinggal baca dari sana — cepat, dan menghindari bug ORM
    aggregate yang sebelumnya bikin query lama crash total.
    """
    return UserPoint.objects.select_related("user").order_by("-total_poin")[:limit]