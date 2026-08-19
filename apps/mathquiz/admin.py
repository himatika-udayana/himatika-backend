from django.contrib import admin, messages

from .forms import QuizSetForm
from .models import (
    QuizSet,
    QuizQuestion,
)
from .services.exceptions import ImportQuizError
from .services.importer import import_quiz_docx


class QuizQuestionInline(admin.TabularInline):
    """
    Soal hanya dapat dibuat melalui import DOCX.
    Inline digunakan untuk melihat hasil import.
    """

    model = QuizQuestion
    extra = 0
    can_delete = False
    show_change_link = True

    fields = (
        "urutan",
        "tipe",
        "teks_soal",
        "poin",
    )

    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuizSet)
class QuizSetAdmin(admin.ModelAdmin):
    form = QuizSetForm

    list_display = (
        "judul",
        "topik",
        "level_kesulitan",
        "jumlah_soal",
        "total_poin_maksimal",
        "dibuat_oleh",
    )

    list_filter = (
        "level_kesulitan",
        "topik",
    )

    search_fields = (
        "judul",
        "topik",
    )

    readonly_fields = (
        "jumlah_soal",
        "total_poin_maksimal",
        "dibuat_oleh",
    )

    inlines = (
        QuizQuestionInline,
    )

    def save_model(self, request, obj, form, change):
        if not obj.dibuat_oleh_id:
            obj.dibuat_oleh = request.user

        super().save_model(request, obj, form, change)

        document = form.cleaned_data.get("document")

        if document is None:
            return

        try:
            jumlah = import_quiz_docx(
                quiz_set=obj,
                document=document,
            )

            self.message_user(
                request,
                f"Berhasil mengimpor {jumlah} soal.",
                level=messages.SUCCESS,
            )

        except ImportQuizError as exc:
            self.message_user(
                request,
                str(exc),
                level=messages.ERROR,
            )

    def has_delete_permission(self, request, obj=None):
        return True