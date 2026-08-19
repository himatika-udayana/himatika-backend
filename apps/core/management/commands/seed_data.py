from django.core.management.base import BaseCommand
from django.db import transaction

from apps.profil.models import PengaturanWebsite, Profil, Timeline, Misi, FilosofiLogo
from apps.rama.models import (
    KategoriAspirasi,
    Semester,
)


class Command(BaseCommand):
    help = "Mengisi data awal aplikasi HIMATIKA."

    def add_arguments(self, parser):

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulasi tanpa menyimpan perubahan.",
        )

        parser.add_argument(
            "--reset",
            action="store_true",
            help="Hapus data seed sebelum membuat ulang.",
        )

        parser.add_argument(
            "--tahun-ajaran",
            default="2025/2026",
            help="Tahun ajaran semester.",
        )

        parser.add_argument(
            "--jenis-semester",
            default="ganjil",
            choices=[
                "ganjil",
                "genap",
            ],
            help="Jenis semester.",
        )

    @transaction.atomic
    def handle(self, *args, **options):

        dry_run = options["dry_run"]
        reset = options["reset"]

        tahun = options["tahun_ajaran"]
        jenis = options["jenis_semester"]

        self.stdout.write("=" * 60)
        self.stdout.write("SEED DATA HIMATIKA")
        self.stdout.write("=" * 60)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("MODE DRY RUN - Tidak ada perubahan database")
            )

        if reset:
            self.reset_data(dry_run)

        self.seed_semester(
            tahun,
            jenis,
            dry_run,
        )

        self.seed_kategori(
            dry_run,
        )

        self.seed_profil(
            dry_run,
        )

        self.seed_pengaturan(
            dry_run,
        )

        self.stdout.write("-" * 60)

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run selesai."))
        else:
            self.stdout.write(self.style.SUCCESS("Seed data selesai."))

        self.stdout.write("=" * 60)

    # =====================================================
    # RESET
    # =====================================================

    def reset_data(self, dry_run):

        jumlah_kategori = KategoriAspirasi.objects.count()

        if not dry_run:
            KategoriAspirasi.objects.all().delete()

        self.stdout.write(self.style.WARNING(f"Reset kategori RAMA: {jumlah_kategori}"))

    # =====================================================
    # SEMESTER
    # =====================================================

    def seed_semester(
        self,
        tahun,
        jenis,
        dry_run,
    ):

        self.stdout.write(f"Semester {jenis} {tahun}")

        if dry_run:
            return

        Semester.objects.update_or_create(
            tahun_ajaran=tahun,
            jenis=jenis,
            defaults={
                "aktif": True,
            },
        )

        # nonaktifkan semester lain
        Semester.objects.exclude(
            tahun_ajaran=tahun,
            jenis=jenis,
        ).update(aktif=False)

        self.stdout.write(self.style.SUCCESS("✓ Semester"))

    # =====================================================
    # KATEGORI RAMA
    # =====================================================

    def seed_kategori(
        self,
        dry_run,
    ):

        data = [
            (
                1,
                "Akademik",
                "Sampaikan aspirasi, masukan, kritik, maupun saran terkait proses pembelajaran, kurikulum, metode pengajaran, jadwal perkuliahan, kualitas dosen, kegiatan akademik, serta hal-hal lain yang berhubungan dengan peningkatan mutu pendidikan dan pengalaman belajar mahasiswa.",
            ),
            (
                2,
                "Kemahasiswaan",
                "Sampaikan aspirasi, masukan, kritik, maupun saran terkait kegiatan kemahasiswaan, organisasi mahasiswa, fasilitas kampus, layanan administrasi, kegiatan ekstrakurikuler, serta hal-hal lain yang berhubungan dengan kehidupan mahasiswa di kampus.",
            ),
            (
                3,
                "Administrasi",
                "Sampaikan aspirasi, masukan, kritik, maupun saran terkait layanan administrasi, prosedur pendaftaran, pengelolaan data mahasiswa, dan hal-hal lain yang berhubungan dengan operasional organisasi.",
            ),
            (
                4,
                "Fasilitas dan Pelayanan",
                "Sampaikan aspirasi, masukan, kritik, maupun saran terkait fasilitas kampus, ruang kelas, laboratorium, perpustakaan, area publik, dan fasilitas lainnya yang mendukung kegiatan akademik dan kesejahteraan mahasiswa.",
            ),
            (
                5,
                "Penyebaran Informasi",
                "Sampaikan aspirasi, masukan, kritik, maupun saran terkait penyebaran informasi, komunikasi internal, transparansi organisasi, media sosial, dan hal-hal lain yang berhubungan dengan aliran informasi di lingkungan kampus.",
            ),
        ]

        for urutan, nama, deskripsi in data:

            if not dry_run:
                KategoriAspirasi.objects.update_or_create(
                    urutan=urutan,
                    defaults={
                        "nama_kategori": nama,
                        "deskripsi": deskripsi,
                    },
                )

        self.stdout.write(self.style.SUCCESS("✓ Kategori RAMA"))

    # =====================================================
    # PROFIL
    # =====================================================

    def seed_profil(
        self,
        dry_run,
    ):

        if not dry_run:

            profil, _ = Profil.objects.update_or_create(
                pk=1,
                defaults={
                    "sejarah": "Program Studi Matematika FMIPA Universitas Udayana resmi memperoleh izin penyelenggaraan melalui SK Dirjen Dikti Nomor 2843/D/T/2001 pada 31 Agustus 2001 dan mulai menerima mahasiswa angkatan pertama pada tahun akademik 2001/2002. Sejak berdiri, program studi ini telah melalui berbagai proses evaluasi, perpanjangan izin, dan akreditasi untuk meningkatkan mutu pendidikan. Akreditasi pertama diperoleh pada tahun 2008 dengan peringkat B, yang kemudian diperpanjang pada tahun 2013 dan 2018. Selanjutnya, berdasarkan keputusan LAMSAMA Nomor 079/SK/LAMSAMA/Akred/S/VII/2023, Program Studi Matematika Universitas Udayana memperoleh akreditasi Baik Sekali yang berlaku mulai 31 Juli 2023 hingga 31 Juli 2028.",
                    "visi": "Mewujudkan Himpunan Mahasiswa Matematika Universitas Udayana yang solid, berdaya guna, dan berperan aktif dalam menciptakan lingkungan akademik yang harmonis, kolaboratif, serta berdampak positif bagi civitas akademika dan masyarakat.",
                    "periode_kepengurusan": "2026",
                },
            )

            # Seed Timeline
            timeline_data = [
                (2001, "Berdirinya HIMATIKA", "HIMATIKA didirikan sebagai wadah resmi mahasiswa Program Studi Matematika Universitas Udayana."),
                (2010, "Perluasan Program Kerja", "Program kerja diperluas mencakup bidang keilmuan, minat bakat, dan pengabdian masyarakat."),
                (2018, "Digitalisasi Layanan", "HIMATIKA mulai memanfaatkan platform digital untuk publikasi dan layanan informasi anggota."),
                (2026, "Peluncuran Portal Web Terpadu", "Peluncuran website resmi HIMATIKA yang mengintegrasikan seluruh layanan organisasi."),
            ]
            
            for tahun, judul, deskripsi in timeline_data:
                Timeline.objects.update_or_create(
                    profil=profil,
                    tahun=tahun,
                    defaults={
                        "judul": judul,
                        "deskripsi": deskripsi,
                    },
                )

            # Seed Misi
            misi_data = [
                (1, "Membangun budaya keilmuan matematika yang aktif dan kolaboratif."),
                (2, "Mewadahi kreativitas dan pengembangan minat bakat mahasiswa."),
                (3, "Menumbuhkan kepedulian sosial melalui program pengabdian masyarakat."),
                (4, "Memperkuat kolaborasi antar anggota, alumni, dan mitra organisasi."),
                (5, "Mengelola organisasi secara transparan, profesional, dan akuntabel."),
            ]
            
            for urutan, deskripsi in misi_data:
                Misi.objects.update_or_create(
                    profil=profil,
                    urutan=urutan,
                    defaults={
                        "deskripsi": deskripsi,
                    },
                )

            # Seed Filosofi Logo
            filosofi_data = [
                ("Simbol Sigma (Σ)", "Melambangkan penjumlahan dan kekuatan kolektif seluruh anggota HIMATIKA."),
                ("Warna Biru", "Merepresentasikan intelektualitas, ketenangan, dan profesionalisme organisasi."),
                ("Bentuk Lingkaran", "Menggambarkan kesatuan dan kekeluargaan yang tidak terputus antar anggota."),
                ("Garis Tegas", "Mencerminkan ketepatan dan logika berpikir khas ilmu matematika."),
            ]
            
            for nama, deskripsi in filosofi_data:
                FilosofiLogo.objects.update_or_create(
                    profil=profil,
                    nama=nama,
                    defaults={
                        "deskripsi": deskripsi,
                    },
                )

        self.stdout.write(self.style.SUCCESS("✓ Profil HIMATIKA"))

    # =====================================================
    # PENGATURAN
    # =====================================================

    def seed_pengaturan(
        self,
        dry_run,
    ):

        if not dry_run:

            PengaturanWebsite.objects.update_or_create(
                pk=1,
                defaults={
                    "nama_website": "HIMATIKA Universitas Udayana",
                    "alamat": "Jl. Raya Kampus Unud, Jimbaran, Kuta Selatan, Kabupaten Badung, Bali 80361",
                    "email_kontak": "himatikasandya2024@gmail.com",
                    "no_hp": "+62 812-3456-7890",
                    "whatsapp_pj_koperasi": "+62 812-3456-7890",
                },
            )

        self.stdout.write(self.style.SUCCESS("✓ Pengaturan Website"))
