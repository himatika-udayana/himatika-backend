# Backend HIMATIKA

Backend untuk website resmi HIMATIKA berbasis Django dan Django REST Framework. Proyek ini menyediakan API untuk manajemen konten, autentikasi pengguna, kuis, arsip, profil organisasi, pengaturan website, koperasi, dan fitur RAMA aspirasi.

## Ringkasan Proyek

Backend ini digunakan oleh frontend untuk mengakses data dan menjalankan fitur-fitur berikut:

- Autentikasi pengguna dan verifikasi email
- Manajemen konten publik seperti post dan FAQ
- Arsip dokumen dan materi
- Produk koperasi
- Kuis Mathquiz dengan attempt dan leaderboard
- Profil organisasi, pengurus, program kerja, dan misi
- Pengaturan website
- Form dan submission aspirasi RAMA

## Teknologi yang Digunakan

- Python 3.11+
- Django 5.1.4
- Django REST Framework
- Simple JWT untuk autentikasi
- Cloudinary untuk media storage
- SMTP Gmail untuk pengiriman email verifikasi/reset password
- SQLite untuk development, PostgreSQL/Database URL untuk production

## Struktur Direktori

```text
backend/
├── apps/
│   ├── arsip/
│   ├── core/
│   ├── konten/
│   ├── koperasi/
│   ├── mathquiz/
│   ├── pengaturan/
│   ├── profil/
│   ├── rama/
│   └── users/
├── config/
├── credentials/
├── db.sqlite3
├── manage.py
├── requirements.txt
├── API_ENDPOINTS.md
├── openapi.yaml
└── README.md
```

## Persiapan Lingkungan

1. Masuk ke direktori project:

```bash
cd /path/to/backend
```

2. Buat virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependency:

```bash
pip install -r requirements.txt
```

4. Buat file environment variables yang diperlukan. Contoh variabel yang dipakai oleh project:

```env
SECRET_KEY=your-secret-key
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-cloud-api-key
CLOUDINARY_API_SECRET=your-cloud-api-secret
GOOGLE_SHEET_ID=your-google-sheet-id
EMAIL_VERIFICATION_BASE_URL=http://localhost:8000/api/auth/verify-email/
```

> Jika Anda menggunakan production environment, pastikan nilai variabel di atas disimpan aman dan tidak di-commit ke repository.

## Migrasi Database

```bash
python manage.py migrate
```

## Menjalankan Server

```bash
python manage.py runserver
```

Server akan berjalan di:

```text
http://localhost:8000
```

## Membuat Superuser

```bash
python manage.py createsuperuser
```

## Dokumentasi API

Dokumentasi API yang tersedia:

- [openapi.yaml](openapi.yaml) — dokumentasi OpenAPI/Swagger siap pakai
- [.env.example](.env.example) — contoh konfigurasi environment


## Base URL API

```text
http://localhost:8000/api
```

## Autentikasi

Beberapa endpoint memerlukan token JWT. Login di endpoint:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"anggota@example.com","password":"Password123!"}'
```

Gunakan token yang diterima dari response sebagai header berikut:

```http
Authorization: Bearer <access_token>
```

## Testing

Untuk menjalankan test:

```bash
python manage.py test
```

## Catatan Pengembangan

- Semua endpoint API berada di prefix `/api`.
- Endpoint publik tidak memerlukan token.
- Endpoint terproteksi memerlukan akun yang sudah terverifikasi email.
- Untuk integrasi frontend, gunakan dokumentasi API di [API_ENDPOINTS.md](API_ENDPOINTS.md) atau [openapi.yaml](openapi.yaml).

## Deployment Production di Render

File [render.yaml](render.yaml) sudah berisi definisi PostgreSQL dan web service. Cara paling mudah adalah menggunakan **Render Blueprint**:

1. Push repository ke GitHub dan pastikan `render.yaml` berada di root repository backend.
2. Di Render, pilih **New > Blueprint**, hubungkan repository, lalu pilih branch production (biasanya `main`).
3. Review resource `himatika-db` dan `himatika-backend`, lalu klik **Apply**.
4. Isi semua environment variable yang bertanda `sync: false` pada service web.
5. Deploy. Render akan menjalankan:
  - `pip install -r requirements-runtime.txt`
  - `python manage.py collectstatic --noinput`
  - `python manage.py migrate`
  - `gunicorn config.wsgi:application`

### Environment variable Render

Blueprint otomatis membuat `SECRET_KEY`, `DATABASE_URL`, dan pengaturan HTTPS dasar. Isi nilai berikut di **Web Service > Environment**:

| Variable | Nilai production |
| --- | --- |
| `ALLOWED_HOSTS` | `.onrender.com` dan domain API custom bila ada, dipisahkan koma |
| `CORS_ALLOWED_ORIGINS` | URL frontend HTTPS, tanpa trailing slash |
| `CSRF_TRUSTED_ORIGINS` | URL frontend HTTPS dan domain backend bila diperlukan |
| `EMAIL_VERIFICATION_BASE_URL` | `https://domain-api/api/auth/verify-email/` |
| `RESET_PASSWORD_BASE_URL` | URL halaman reset password frontend |
| `GMAIL_ADDRESS` | Akun Gmail pengirim |
| `GMAIL_APP_PASSWORD` | App Password Gmail, bukan password akun |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `GOOGLE_SHEET_ID` | ID spreadsheet RAMA |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Isi JSON service account satu baris atau format JSON valid |

Untuk `GOOGLE_SERVICE_ACCOUNT_JSON`, buat service account di Google Cloud, aktifkan Google Sheets API, lalu bagikan spreadsheet kepada email service account sebagai Editor. Jangan upload file `credentials/google-service-account.json` ke repository; service production membaca kredensial dari environment.

### Setelah deploy

1. Buka `https://domain-api/healthz/`; response yang benar adalah `ok`.
2. Buka `https://domain-api/admin/` dan buat akun admin dari **Render > Shell**:

```bash
python manage.py createsuperuser
```

3. Uji endpoint login dan endpoint publik dari frontend.
4. Periksa **Logs** Render bila migrasi, email, Cloudinary, atau Google Sheets gagal.

### Deploy manual dan rollback

Setiap push ke branch yang terhubung akan memicu deploy otomatis. Deploy manual dapat dilakukan melalui **Manual Deploy > Deploy latest commit**. Untuk rollback, pilih deploy sebelumnya pada halaman service dan gunakan **Rollback**.

### Operasi rutin

- Migration baru cukup di-commit; `migrate` berjalan otomatis pada saat start service.
- File upload menggunakan Cloudinary karena filesystem Render bersifat ephemeral.
- Database PostgreSQL Render Free cocok untuk awal/testing; aktifkan backup dan instance berbayar sebelum penggunaan kritis.
- Jangan menyalin nilai secret ke log, issue, atau repository.

## Langkah Seeding Data Awal

Untuk mengisi data awal (contoh: profil organisasi, pengaturan website, kategori RAMA, atau data publik), jalankan perintah management command jika tersedia.

Contoh:

```bash
python manage.py shell
```

Atau jika terdapat custom command:

```bash
python manage.py <command_name>
```

Jika belum ada seeder khusus, Anda dapat membuat fixture atau custom management command untuk data awal.

## Panduan Contributor Workflow

### Alur kerja yang disarankan

1. Buat branch baru dari `main` atau `develop`.
2. Lakukan perubahan di branch tersebut.
3. Jalankan test sebelum membuat pull request.
4. Pastikan dokumentasi diperbarui jika ada perubahan endpoint atau flow bisnis.
5. Buat pull request dengan deskripsi yang jelas.

### Naming Branch

Gunakan convention berikut:

- `feature/<nama-fitur>` untuk fitur baru
- `bugfix/<nama-bug>` untuk perbaikan bug
- `chore/<nama-tugas>` untuk perubahan non-fitur seperti dokumentasi atau maintenance
- `hotfix/<nama-issue>` untuk perbaikan cepat di production

Contoh:

```text
feature/auth-refresh-token
bugfix/login-validation
chore/update-api-docs
hotfix/reset-password-email
```

### Checklist sebelum PR

- [ ] Code sudah diuji
- [ ] Migrasi sudah dicek jika ada perubahan model
- [ ] Dokumentasi diperbarui jika ada perubahan API
- [ ] Tidak ada secret/key sensitif yang di-commit
# himatika-backend
# himatika-backend
