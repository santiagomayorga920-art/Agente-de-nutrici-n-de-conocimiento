"""Cliente mínimo de la Bot API de Telegram (sondeo con getUpdates, sin servidor)."""

import json

import httpx

MAX_TEXT = 4096
MAX_CAPTION = 1024

# Una fila por botón: [(texto, callback_data), ...]
Buttons = list[tuple[str, str]]


class TelegramError(Exception):
    pass


class TelegramClient:
    def __init__(self, token: str, http: httpx.Client | None = None) -> None:
        self._base = f"https://api.telegram.org/bot{token}"
        self._http = http or httpx.Client(timeout=30)

    def get_updates(self, offset: int) -> list[dict]:
        return self._call(
            "getUpdates",
            {"offset": offset, "timeout": 0, "allowed_updates": ["message", "callback_query"]},
        )

    def send_message(self, chat_id: str, text: str, buttons: Buttons | None = None) -> None:
        self._call(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text[:MAX_TEXT],
                "parse_mode": "HTML",
                "link_preview_options": {"is_disabled": True},
                **_keyboard(buttons),
            },
        )

    def send_photo(
        self, chat_id: str, photo_url: str, caption: str, buttons: Buttons | None = None
    ) -> None:
        self._call(
            "sendPhoto",
            {
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": caption[:MAX_CAPTION],
                "parse_mode": "HTML",
                **_keyboard(buttons),
            },
        )

    def send_photo_file(
        self, chat_id: str, image: bytes, caption: str, buttons: Buttons | None = None
    ) -> None:
        """Sube una imagen generada (la tarjeta visual) en vez de pasar una URL."""
        data = {"chat_id": chat_id, "caption": caption[:MAX_CAPTION], "parse_mode": "HTML"}
        markup = _keyboard(buttons).get("reply_markup")
        if markup:
            data["reply_markup"] = json.dumps(markup, ensure_ascii=False)
        response = self._http.post(
            f"{self._base}/sendPhoto",
            data=data,
            files={"photo": ("tarjeta.png", image, "image/png")},
        )
        result = response.json()
        if not result.get("ok"):
            raise TelegramError(f"sendPhoto: {result.get('description', response.status_code)}")

    def send_voice(self, chat_id: str, audio: bytes, duration: int, caption: str = "") -> None:
        """Nota de voz en MP3 (Telegram la muestra con su reproductor de voz)."""
        data = {"chat_id": chat_id, "duration": str(duration), "caption": caption[:MAX_CAPTION]}
        response = self._http.post(
            f"{self._base}/sendVoice",
            data=data,
            files={"voice": ("pildora.mp3", audio, "audio/mpeg")},
        )
        result = response.json()
        if not result.get("ok"):
            raise TelegramError(f"sendVoice: {result.get('description', response.status_code)}")

    def send_typing(self, chat_id: str, action: str = "typing") -> None:
        """Muestra "escribiendo…" mientras Gemini trabaja (solo se nota en modo webhook)."""
        try:
            self._call("sendChatAction", {"chat_id": chat_id, "action": action})
        except TelegramError:
            pass

    def webhook_info(self) -> dict:
        return self._call("getWebhookInfo", {})

    def webhook_url(self) -> str:
        return self.webhook_info().get("url", "")

    def set_webhook(self, url: str, secret: str) -> None:
        self._call(
            "setWebhook",
            {
                "url": url,
                "secret_token": secret,
                "allowed_updates": ["message", "callback_query"],
                "drop_pending_updates": False,
            },
        )

    def set_commands(self, commands: list[tuple[str, str]]) -> None:
        self._call(
            "setMyCommands",
            {"commands": [{"command": c, "description": d} for c, d in commands]},
        )

    def answer_callback(self, callback_id: str, text: str = "") -> None:
        try:
            self._call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text})
        except TelegramError:
            pass  # pasado un rato Telegram da el botón por caducado; no es un error real

    def remove_buttons(self, chat_id: str, message_id: int) -> None:
        try:
            self._call(
                "editMessageReplyMarkup",
                {
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "reply_markup": {"inline_keyboard": []},
                },
            )
        except TelegramError:
            pass  # el mensaje ya no tenía botones

    def _call(self, method: str, payload: dict):
        response = self._http.post(f"{self._base}/{method}", json=payload)
        data = response.json()
        if not data.get("ok"):
            raise TelegramError(f"{method}: {data.get('description', response.status_code)}")
        return data["result"]


def _keyboard(buttons: Buttons | None) -> dict:
    if not buttons:
        return {}
    rows = [[{"text": text, "callback_data": data}] for text, data in buttons]
    return {"reply_markup": {"inline_keyboard": rows}}
