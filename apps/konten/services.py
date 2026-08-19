import mammoth
import logging

from .models import Post

logger = logging.getLogger(__name__)


class PostService:
    @staticmethod
    def get_published_posts():
        return (
            Post.objects
            .filter(status=Post.Status.PUBLISHED)
            .select_related("publisher")
            .prefetch_related("tags", "images")
            .order_by("-tanggal_publish")
        )

    @staticmethod
    def get_draft_posts():
        return (
            Post.objects
            .filter(status=Post.Status.DRAFT)
            .select_related("publisher")
            .prefetch_related("tags", "images")
            .order_by("-tanggal_dibuat")
        )

    @staticmethod
    def get_posts_by_tipe(tipe):
        return (
            Post.objects
            .filter(
                tipe=tipe,
                status=Post.Status.PUBLISHED,
            )
            .select_related("publisher")
            .prefetch_related("tags", "images")
            .order_by("-tanggal_publish")
        )


class MammothService:
    @staticmethod
    def convert_docx_to_html(docx_file):
        try:
            with docx_file.open("rb") as docx:
                result = mammoth.convert_to_html(docx)
                return result.value
        except Exception:
            logger.exception("Gagal mengonversi DOCX ke HTML")
            return None