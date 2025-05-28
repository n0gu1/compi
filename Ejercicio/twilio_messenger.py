# Ejercicio/twilio_messenger.py
from pathlib import Path
import json
import os
from typing import Dict, Optional, Union, List
from urllib.parse import urljoin

from django.conf import settings
from twilio.rest import Client


class TwilioMessenger:
    """
    Wrapper muy parecido al que mostraste en C#.
    Permite:
      •  send_sms()
      •  send_whatsapp_template()
    """

    def __init__(self) -> None:
        self._client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

        self._sms_from: str = settings.TWILIO_FROM_SMS  # +1xxx
        # Si NO pones el tuyo, Twilio sandbox: whatsapp:+14155238886
        self._wa_from: str = settings.TWILIO_FROM_WHATSAPP or "whatsapp:+14155238886"
        self._base_url: str = settings.APP_BASE_URL      # https://tusitio.com
        self._pdf_dir: Path = (
            Path(settings.BASE_DIR) / "static" / "PDFS"
        )
        self._pdf_dir.mkdir(parents=True, exist_ok=True)

    # ---------- helpers ----------
    @staticmethod
    def _wa(num_e164: str) -> str:
        if not num_e164.startswith("+"):
            num_e164 = "+" + num_e164
        return f"whatsapp:{num_e164}"

    # ---------- API -------------
    def send_sms(self, to_e164: str, body: str):
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
        pdf_prefix: str = "doc"
    ):
        media_url: Optional[List[str]] = None

        if pdf_bytes:
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
