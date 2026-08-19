from django import forms

from .models import QuizSet


class QuizSetForm(forms.ModelForm):
    """
    Form admin untuk membuat QuizSet sekaligus mengunggah
    file DOCX yang akan diparsing menjadi QuizQuestion.
    """

    document = forms.FileField(
        required=False,
        label="Dokumen Soal (.docx)",
        help_text=(
            "Upload file .docx sesuai template. "
            "Soal akan dibuat otomatis setelah QuizSet disimpan."
        ),
    )

    class Meta:
        model = QuizSet
        fields = "__all__"

    def clean_document(self):
        document = self.cleaned_data.get("document")

        if not document:
            return document

        if not document.name.lower().endswith(".docx"):
            raise forms.ValidationError(
                "File harus berformat .docx."
            )

        allowed_content_types = {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        if getattr(document, "content_type", None) not in allowed_content_types:
            raise forms.ValidationError(
                "Format file tidak valid."
            )

        return document