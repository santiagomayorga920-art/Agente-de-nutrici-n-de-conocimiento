"""Cliente mínimo de la Bot API de Telegram (sondeo con getUpdates, sin servidor)."""

import httpx

_MAX_LEN = 4096


class TelegramClient:
    def __init__(self, token: str, http: httpx.Client | None = None) -> None:
        self._base = f"https://api.telegram.org/bot{token}"
        self._http = http or httpx.Client(timeout=30)

    def get_updates(self, offset: int) -> list[dict]:
        response = self._http.get(
            f"{self._base}/getUpdates",
            params={"offset": offset, "timeout": 0, "allowed_updates": '["message"]'},
        )
        response.raise_for_status()
        return response.json()["result"]

    def send_message(self, chat_id: str, text: str) -> None:
        for start in range(0, len(text), _MAX_LEN):
            response = self._http.post(
                f"{self._base}/sendMessage",
                json={"chat_id": chat_id, "text": text[start : start + _MAX_LEN]},
            )
            response.raise_for_status()
