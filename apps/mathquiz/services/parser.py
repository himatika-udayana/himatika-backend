import re


class ParserError(Exception):
    """Error saat parsing file quiz."""


QUESTION_PATTERN = re.compile(r"^(\d+)\.\s*(.+)$")


def parse_lines(lines: list[str]) -> list[dict]:
    """
    Mengubah daftar baris menjadi list dictionary soal.

    Return:
    [
        {
            "urutan": 1,
            "tipe": "pg",
            "teks_soal": "...",
            "pilihan_a": "...",
            ...
        }
    ]
    """

    questions = []

    i = 0

    while i < len(lines):

        line = lines[i].strip()

        if not line:
            i += 1
            continue

        if line == "Pilihan_Ganda":
            question, i = _parse_pg(lines, i + 1)
            questions.append(question)
            continue

        if line == "Isian_Singkat":
            question, i = _parse_isian(lines, i + 1)
            questions.append(question)
            continue

        raise ParserError(
            f"Tipe soal tidak dikenali: '{line}'"
        )

    return questions


def _parse_pg(lines, index):

    while not lines[index].strip():
        index += 1

    nomor, soal = _parse_nomor(lines[index])
    index += 1

    pilihan = {}

    while index < len(lines):

        text = lines[index].strip()

        if not text:
            index += 1
            continue

        if text.lower().startswith("ans:"):
            break

        huruf = text[0].lower()

        if huruf not in ["a", "b", "c", "d", "e"]:
            raise ParserError(
                f"Pilihan tidak valid pada soal {nomor}"
            )

        pilihan[huruf] = text[2:].strip()

        index += 1

    if set(pilihan.keys()) != {"a", "b", "c", "d", "e"}:
        raise ParserError(
            f"Soal {nomor} belum memiliki pilihan lengkap A-E."
        )

    if index >= len(lines):
        raise ParserError(
            f"Soal {nomor} tidak memiliki ans:"
        )

    jawaban = lines[index].split(":", 1)[1].strip().upper()

    if jawaban not in ["A", "B", "C", "D", "E"]:
        raise ParserError(
            f"Jawaban soal {nomor} tidak valid."
        )

    index += 1

    return (
        {
            "urutan": nomor,
            "tipe": "pg",
            "teks_soal": soal,
            "pilihan_a": pilihan["a"],
            "pilihan_b": pilihan["b"],
            "pilihan_c": pilihan["c"],
            "pilihan_d": pilihan["d"],
            "pilihan_e": pilihan["e"],
            "jawaban_benar_pg": jawaban,
        },
        index,
    )


def _parse_isian(lines, index):

    while not lines[index].strip():
        index += 1

    nomor, soal = _parse_nomor(lines[index])
    index += 1

    while not lines[index].strip():
        index += 1

    if not lines[index].lower().startswith("ans:"):
        raise ParserError(
            f"Soal isian {nomor} tidak memiliki ans:"
        )

    jawaban = lines[index].split(":", 1)[1].strip()

    index += 1

    return (
        {
            "urutan": nomor,
            "tipe": "isian",
            "teks_soal": soal,
            "jawaban_benar_isian": jawaban,
        },
        index,
    )


def _parse_nomor(line):

    match = QUESTION_PATTERN.match(line)

    if not match:
        raise ParserError(
            f"Format nomor soal salah: '{line}'"
        )

    return (
        int(match.group(1)),
        match.group(2),
    )