import re

from .parser import ParserError


VALID_PG_ANSWER = {"A", "B", "C", "D", "E"}

QUESTION_PATTERN = re.compile(r"^\d+\.")


def validate_questions(questions: list[dict]) -> None:
    """
    Memvalidasi hasil parsing sebelum disimpan ke database.

    Akan me-raise ParserError apabila terdapat data yang tidak valid.
    """

    if not questions:
        raise ParserError(
            "Tidak ada soal yang ditemukan."
        )

    validate_nomor(questions)
    validate_duplicate_nomor(questions)

    for question in questions:

        if question["tipe"] == "pg":
            validate_pg(question)
        elif question["tipe"] == "isian":
            validate_isian(question)
        else:
            raise ParserError(
                f"Tipe soal '{question['tipe']}' tidak dikenali."
            )


def validate_nomor(questions: list[dict]) -> None:
    """
    Nomor harus berurutan:
    1,2,3,4,...
    """

    for expected, question in enumerate(questions, start=1):

        if question["urutan"] != expected:
            raise ParserError(
                f"Nomor soal tidak berurutan. "
                f"Ditemukan {question['urutan']}, seharusnya {expected}."
            )


def validate_duplicate_nomor(questions: list[dict]) -> None:

    nomor = [q["urutan"] for q in questions]

    if len(nomor) != len(set(nomor)):
        raise ParserError(
            "Terdapat nomor soal yang duplikat."
        )


def validate_pg(question: dict) -> None:

    required = [
        "pilihan_a",
        "pilihan_b",
        "pilihan_c",
        "pilihan_d",
        "pilihan_e",
    ]

    for field in required:

        if not question.get(field):
            raise ParserError(
                f"Soal nomor {question['urutan']} "
                f"belum memiliki {field}."
            )

    answer = question.get(
        "jawaban_benar_pg",
        "",
    ).upper()

    if answer not in VALID_PG_ANSWER:
        raise ParserError(
            f"Jawaban soal nomor "
            f"{question['urutan']} harus A-E."
        )


def validate_isian(question: dict) -> None:

    answer = (
        question.get(
            "jawaban_benar_isian",
            "",
        ).strip()
    )

    if not answer:
        raise ParserError(
            f"Soal nomor "
            f"{question['urutan']} "
            f"belum memiliki jawaban."
        )