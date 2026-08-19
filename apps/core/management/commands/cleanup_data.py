from datetime import timedelta

from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.mathquiz.models import QuizAttempt
from apps.rama.models import RamaSubmission
from apps.users.models import EmailVerificationToken


class Command(BaseCommand):
    help = (
        "Membersihkan data lama "
        "(Email Token, Quiz Attempt, RAMA, Session)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Menampilkan data yang akan dihapus tanpa benar-benar menghapus.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        now = timezone.now()

        self.stdout.write("=" * 55)
        self.stdout.write("DATABASE CLEANUP")
        self.stdout.write("=" * 55)

        # =====================================================
        # EMAIL VERIFICATION TOKEN
        # =====================================================

        token_qs = (
            EmailVerificationToken.objects.filter(is_used=True)
            | EmailVerificationToken.objects.filter(expired_at__lt=now)
        ).distinct()

        token_deleted = token_qs.count()

        if not dry_run:
            token_qs.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Email Token    : {token_deleted} "
                f"{'will be deleted' if dry_run else 'deleted'}"
            )
        )

        # =====================================================
        # QUIZ ATTEMPT
        # Simpan Top Score + Attempt Terbaru
        # =====================================================

        attempt_deleted = 0

        pasangan = (
            QuizAttempt.objects.values_list(
                "user_id",
                "quiz_set_id",
            )
            .distinct()
        )

        for user_id, quiz_set_id in pasangan:

            attempts = (
                QuizAttempt.objects.filter(
                    user_id=user_id,
                    quiz_set_id=quiz_set_id,
                )
                .order_by("-waktu_mulai")
            )

            if attempts.count() <= 2:
                continue

            latest = attempts.first()

            top = (
                attempts.order_by(
                    "-skor",
                    "-waktu_mulai",
                )
                .first()
            )

            keep_ids = {
                latest.id,
                top.id,
            }

            old_attempts = attempts.exclude(
                id__in=keep_ids,
            )

            deleted = old_attempts.count()

            attempt_deleted += deleted

            if not dry_run:
                # QuizAnswer ikut terhapus karena CASCADE
                old_attempts.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Quiz Attempt  : {attempt_deleted} "
                f"{'will be deleted' if dry_run else 'deleted'}"
            )
        )

        # =====================================================
        # RAMA
        # =====================================================

        batas = now - timedelta(days=365 * 2)

        rama_qs = RamaSubmission.objects.filter(
            tanggal_submit__lt=batas,
            status=RamaSubmission.Status.TERKIRIM,
        )

        rama_deleted = rama_qs.count()

        if not dry_run:
            # RamaAspirasi ikut terhapus (CASCADE)
            rama_qs.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ RAMA          : {rama_deleted} "
                f"{'will be deleted' if dry_run else 'deleted'}"
            )
        )

        # =====================================================
        # DJANGO SESSION
        # =====================================================

        session_qs = Session.objects.filter(
            expire_date__lt=now,
        )

        session_deleted = session_qs.count()

        if not dry_run:
            session_qs.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Session       : {session_deleted} "
                f"{'will be deleted' if dry_run else 'deleted'}"
            )
        )

        # =====================================================
        # SUMMARY
        # =====================================================

        total = (
            token_deleted
            + attempt_deleted
            + rama_deleted
            + session_deleted
        )

        self.stdout.write("-" * 55)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN selesai. "
                    f"Total {total} data akan dihapus."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Cleanup selesai. "
                    f"Total {total} data berhasil dihapus."
                )
            )

        self.stdout.write("=" * 55)