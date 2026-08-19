from django import forms
from .models import Post


from django import forms

from .models import Post


class PostAdminForm(forms.ModelForm):
    document = forms.FileField(
        required=False,
        label="Dokumen (.docx)",
        help_text="Upload file .docx untuk dikonversi menjadi HTML.",
    )

    class Meta:
        model = Post
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_document(self):
        document = self.cleaned_data.get("document")

        if document:
            if not document.name.lower().endswith(".docx"):
                raise forms.ValidationError(
                    "Hanya file .docx yang diperbolehkan."
                )

        return document