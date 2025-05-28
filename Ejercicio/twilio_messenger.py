import json, uuid
from pathlib import Path
from typing import Dict, Optional, List
from urllib.parse import urljoin

import cloudinary.uploader           # ← sigue pudiendo subir si quieres
from django.conf import settings
from twilio.rest import Client, ApiException


class TwilioMessenger:
    """
    Envoltura mínima para:
      • send_sms()
      • send_whatsapp_template()  (con PDF adjunto opcional *o* URL externa)
    """

    def __init__(self) -> None:
        self._cli  = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self._sms  = settings.TWILIO_FROM_SMS
        self._wa   = settings.TWILIO_FROM_WHATSAPP or "whatsapp:+14155238886"
        self._base = settings.APP_BASE_URL.rstrip("/") + "/"

        # carpeta local de respaldo (solo si quisieras seguir guardando)
        self._pdf_dir: Path = Path(settings.BASE_DIR, "static", "PDFS")
        self._pdf_dir.mkdir(parents=True, exist_ok=True)

    # ---------- helpers ----------
    @staticmethod
    def _wa_fmt(e164: str) -> str:
        if not e164.startswith("+"):
            e164 = "+" + e164
        return f"whatsapp:{e164}"

    # ---------- API ----------
    def send_sms(self, to_e164: str, body: str):
        return self._cli.messages.create(body=body, from_=self._sms, to=to_e164)

    def send_whatsapp_template(
        self,
        *,
        to_e164: str,
        content_sid: str,
        vars: Dict[str, str],
        pdf_bytes: Optional[bytes] = None,      # → sube a Cloudinary
        pdf_prefix: str = "doc",
        override_media_url: Optional[str] = None   # → usa URL externa tal cual
    ):
        """
        • Si `override_media_url` viene ⇒ se usa directamente (no se sube nada).
        • Si NO viene y hay `pdf_bytes` ⇒ se sube a Cloudinary (/raw).
        • Si ninguno ⇒ se envía sin media.
        """
        media_url: Optional[List[str]] = None

        # --- caso 1: URL ya lista ---
        if override_media_url:
            media_url = [override_media_url]

        # --- caso 2: bytes a Cloudinary ---
        elif pdf_bytes:
            public_id = f"{pdf_prefix}_{uuid.uuid4().hex[:8]}.pdf"
            up = cloudinary.uploader.upload(
                pdf_bytes,
                resource_type="raw",
                folder=settings.CLOUDINARY_FOLDER,
                public_id=public_id,
                overwrite=True
            )
            media_url = [up["secure_url"]]

        # --- armar mensaje ---
        try:
            return self._cli.messages.create(
                from_=self._wa,
                to=self._wa_fmt(to_e164),
                content_sid=content_sid,
                content_variables=json.dumps(vars),
                media_url=media_url
            )
        except ApiException as e:
            # loggea o relanza según tu gusto
            print("⚠️ Twilio error:", e)
            raise
