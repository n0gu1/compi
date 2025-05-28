# Ejercicio/twilio_messenger.py

from pathlib import Path
import json
import os
from typing import Dict, Optional, List
from urllib.parse import urljoin

from django.conf import settings
from twilio.rest import Client


class TwilioMessenger:
    """
    Wrapper para Twilio que permite enviar SMS y plantillas de WhatsApp,
    con opción de adjuntar un PDF ya subido a Cloudinary o desde bytes.
    """

    def __init__(self) -> None:
        # Cliente Twilio
        self._client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

        # Remitentes
        self._sms_from = settings.TWILIO_FROM_SMS
        self._wa_from  = settings.TWILIO_FROM_WHATSAPP or "whatsapp:+14155238886"

        # Para construir URLs a archivos estáticos si usamos el fallback
        self._base_url = settings.APP_BASE_URL
        self._pdf_dir  = Path(settings.BASE_DIR) / "static" / "PDFS"
        self._pdf_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _wa(num_e164: str) -> str:
        """Formatea un número E.164 como destino de WhatsApp."""
        if not num_e164.startswith("+"):
            num_e164 = "+" + num_e164
        return f"whatsapp:{num_e164}"

    def send_sms(self, to_e164: str, body: str):
        """Envía un SMS simple."""
        return self._client.messages.create(
            body=body,
            from_=self._sms_from,
            to=to_e164
        )

    def send_whatsapp_template(
        self,
        to_e164: str,
        content_sid: str,
        vars: Dict[str, str],
        pdf_bytes: Optional[bytes] = None,
        pdf_prefix: str = "doc",
        override_media_url: Optional[str] = None
    ):
        """
        Envía una plantilla de WhatsApp (content_sid) con variables vars.
        Si override_media_url está dado, lo usa como media_url.
        De lo contrario, si pdf_bytes no es None, guarda el PDF en disco
        y lo sirve desde /static/PDFS.
        """
        media_url: Optional[List[str]] = None

        if override_media_url:
            media_url = [override_media_url]
        elif pdf_bytes is not None:
            # Fallback: guardar en disco y servir como estático
            file_name = f"{pdf_prefix}_{os.urandom(5).hex()}.pdf"
            file_path = self._pdf_dir / file_name
            file_path.write_bytes(pdf_bytes)
            media_url = [urljoin(self._base_url, f"/static/PDFS/{file_name}")]

        return self._client.messages.create(
            from_=self._wa_from,
            to=self._wa(to_e164),
            content_sid=content_sid,
            content_variables=json.dumps(vars),
            media_url=media_url
        )
