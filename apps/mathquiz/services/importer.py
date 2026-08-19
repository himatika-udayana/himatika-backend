from docx import Document

from django.db import transaction

from ..models import QuizQuestion
from .parser import parse_lines
from .validator import validate_questions


@transaction.atomic
def import_quiz_docx(quiz_set, document):
    """
    Mengimpor seluruh soal dari file DOCX ke QuizSet.

    Flow:
        DOCX
            ↓
        Parse paragraph
            ↓
        parse_lines()
            ↓
        validate_questions()
            ↓
        Hapus soal lama
            ↓
        Bulk create
    """

    doc = Document(document)

    lines = [
        paragraph.text.strip()
        for paragraph in doc.paragraphs
        if paragraph.text.strip()
    ]

    questions = parse_lines(lines)

    validate_questions(questions)

    quiz_set.soal.all().delete()

    QuizQuestion.objects.bulk_create(
        [
            QuizQuestion(
                quiz_set=quiz_set,
                urutan=item["urutan"],
                tipe=item["tipe"],
                teks_soal=item["teks_soal"],
                poin=item.get("poin", 10),
                pilihan_a=item.get("pilihan_a", ""),
                pilihan_b=item.get("pilihan_b", ""),
                pilihan_c=item.get("pilihan_c", ""),
                pilihan_d=item.get("pilihan_d", ""),
                pilihan_e=item.get("pilihan_e", ""),
                jawaban_benar_pg=item.get(
                    "jawaban_benar_pg",
                    "",
                ),
                jawaban_benar_isian=item.get(
                    "jawaban_benar_isian",
                    "",
                ),
            )
            for item in questions
        ]
    )

    return len(questions)