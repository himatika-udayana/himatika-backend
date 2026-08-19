class ImportQuizError(Exception):
    """
    Exception untuk seluruh proses import Quiz dari file DOCX.

    Digunakan oleh:
    - parser.py
    - validator.py
    - importer.py

    Sehingga admin cukup menangkap satu jenis exception.
    """

    pass