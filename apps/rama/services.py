"""
Logic RAMA:
- Semester aktif
- Validasi boleh submit
- Sinkronisasi ke Google Spreadsheet
"""

import json
import logging

import gspread
from django.conf import settings
from google.oauth2.service_account import Credentials

from .models import RamaSubmission, Semester

logger = logging.getLogger(__name__)


class GoogleSheetService:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    HEADER = [
        "Kode Respon",
        "Semester",
        "Tanggal Submit",
        "Kategori",
        "Kepuasan",
        "Aspirasi",
    ]

    @classmethod
    def get_client(cls):
        if settings.GOOGLE_SERVICE_ACCOUNT_JSON_ENV:
            credentials = Credentials.from_service_account_info(
                json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON_ENV),
                scopes=cls.SCOPES,
            )
        else:
            credentials = Credentials.from_service_account_file(
                str(settings.GOOGLE_SERVICE_ACCOUNT_FILE),
                scopes=cls.SCOPES,
            )
        return gspread.authorize(credentials)

    @classmethod
    def get_spreadsheet(cls):
        client = cls.get_client()
        return client.open_by_key(settings.GOOGLE_SHEET_ID)

    @classmethod
    def get_or_create_worksheet(cls, semester):
        """
        Satu worksheet untuk satu semester.
        Contoh:
        - Ganjil 2025/2026
        - Genap 2025/2026
        """
        spreadsheet = cls.get_spreadsheet()

        worksheet_name = str(semester)

        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=worksheet_name,
                rows=1000,
                cols=10,
            )

            worksheet.append_row(
                cls.HEADER,
                value_input_option="USER_ENTERED",
            )

        return worksheet

    @classmethod
    def simpan_submission(cls, submission: RamaSubmission):
        """
        Mengirim seluruh aspirasi ke Google Spreadsheet.

        1 aspirasi = 1 baris.

        Identitas mahasiswa TIDAK dikirim.
        Hanya kode respon anonim.
        """

        worksheet = cls.get_or_create_worksheet(
            submission.semester
        )

        aspirasi = (
            submission.aspirasi
            .select_related("kategori")
            .order_by("kategori__urutan")
        )

        rows = []

        for item in aspirasi:
            rows.append([
                submission.kode_respon,
                str(submission.semester),
                submission.tanggal_submit.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                item.kategori.nama_kategori,
                item.get_kepuasan_display(),
                item.isi_aspirasi,
            ])

        try:
            worksheet.append_rows(
                rows,
                value_input_option="USER_ENTERED",
            )

            submission.status = RamaSubmission.Status.TERKIRIM
            submission.save(update_fields=["status"])

            return True

        except Exception as exc:
            logger.exception(exc)

            submission.status = RamaSubmission.Status.GAGAL
            submission.save(update_fields=["status"])

            return False


def get_semester_aktif():
    return Semester.objects.filter(
        aktif=True,
    ).first()


def cek_boleh_submit(user) -> tuple[bool, str | None]:
    """
    User hanya boleh melakukan satu kali pengisian
    pada semester yang sedang aktif.
    """

    semester = get_semester_aktif()

    if semester is None:
        return (
            False,
            "Belum ada semester yang sedang aktif.",
        )

    sudah_submit = RamaSubmission.objects.filter(
        user=user,
        semester=semester,
    ).exists()

    if sudah_submit:
        return (
            False,
            f"Kamu sudah mengisi RAMA untuk semester {semester}.",
        )

    return True, None