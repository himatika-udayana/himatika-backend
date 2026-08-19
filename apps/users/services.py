"""
Service pengiriman email verifikasi (link), dan helper generate link-nya.
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from html import escape
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)

SUBJECT_MAP = {
    "register": "Verifikasi Akun HIMATIKA",
    "reset_password": "Reset Password HIMATIKA",
    "change_password": "Verifikasi Ganti Password HIMATIKA",
}


def build_verification_link(user, raw_token: str, purpose: str = "register") -> str:
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    if purpose == "reset_password":
        base_url = getattr(
            settings,
            "RESET_PASSWORD_BASE_URL",
            "http://localhost:5173/reset-password",
        )
    else:
        base_url = getattr(
            settings,
            "EMAIL_VERIFICATION_BASE_URL",
            "http://localhost:8000/api/auth/verify-email/",
        )
    return f"{base_url}?uid={uidb64}&token={raw_token}&purpose={purpose}"


def decode_uid(uidb64: str):
    """Return user pk (str) dari uidb64, atau None kalau gagal decode."""
    try:
        return force_str(urlsafe_base64_decode(uidb64))
    except (TypeError, ValueError, OverflowError):
        return None


def send_verification_email(user, link: str, purpose: str = "register"):
    subject = SUBJECT_MAP.get(purpose, "Verifikasi Akun HIMATIKA")
    nama = user.nama_lengkap or user.email
    is_reset = purpose == "reset_password"
    heading = "Ubah Password" if is_reset else "Verifikasi Email"
    intro = (
        "Klik tombol berikut untuk membuat password baru akun HIMATIKA Anda."
        if is_reset
        else "Terima kasih telah melakukan registrasi. Silakan verifikasi akun Anda melalui tombol berikut."
    )
    cta_label = "UBAH PASSWORD" if is_reset else "VERIFIKASI"
    expiry_text = (
        "Link ini berlaku selama 1 jam dan hanya dapat digunakan satu kali."
        if is_reset
        else "Link ini berlaku selama 24 jam dan hanya dapat digunakan satu kali."
    )

    message = (
        f"Halo {nama},\n\n"
        f"{intro}\n\n"
        f"{link}\n\n"
        f"{expiry_text}\n"
        f"Jika link sudah kedaluwarsa, silakan meminta link baru.\n\n"
        f"Kalau kamu tidak merasa melakukan permintaan ini, abaikan email ini."
    )

    safe_name = escape(nama)
    safe_link = escape(link, quote=True)
    html_message = f"""
<!doctype html>
<html lang="id">
    <body style="margin:0;background:#eef1f7;color:#e5e7eb;font-family:Arial,Helvetica,sans-serif;">
        <div style="padding:24px 12px;">
            <div style="max-width:640px;margin:0 auto;background:#0f172a;border:1px solid #1e293b;">
                <div style="padding:30px 28px 18px;border-bottom:1px solid #1e293b;">
                    <div style="font-size:18px;font-weight:700;letter-spacing:3px;color:#22d3ee;">HIMATIKA</div>
                    <h1 style="margin:28px 0 10px;color:#38bdf8;font-size:30px;line-height:1.2;">{heading}</h1>
                    <div style="height:1px;background:#1e293b;"></div>
                </div>
                <div style="padding:28px;">
                    <p style="margin:0 0 14px;font-size:16px;line-height:1.6;color:#f3f4f6;">Yth. {safe_name},</p>
                    <p style="margin:0 0 26px;font-size:14px;line-height:1.65;color:#b8bbc4;">{intro}</p>
                    <div style="text-align:center;margin:30px 0 32px;">
                        <a href="{safe_link}" style="display:inline-block;padding:16px 28px;border:1px solid #2563eb;border-radius:12px;background:#132038;color:#22d3ee;font-size:20px;font-weight:700;letter-spacing:5px;text-decoration:none;">{cta_label}</a>
                    </div>
                    <p style="margin:0 0 12px;font-size:13px;line-height:1.6;color:#9ca3af;">{expiry_text}</p>
                    <p style="margin:24px 0 0;font-size:13px;line-height:1.6;color:#9ca3af;">Jika Anda tidak merasa melakukan permintaan ini, abaikan email ini.</p>
                </div>
                <div style="padding:24px 28px;border-top:1px solid #1e293b;text-align:center;">
                    <p style="margin:0;color:#22d3ee;font-size:14px;font-weight:700;">HIMATIKA</p>
                    <p style="margin:8px 0 0;color:#8f93a0;font-size:12px;">Universitas Udayana</p>
                </div>
                <div style="height:8px;background:#2563eb;background:linear-gradient(90deg,#2563eb,#22d3ee);"></div>
            </div>
        </div>
    </body>
</html>
"""

    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)