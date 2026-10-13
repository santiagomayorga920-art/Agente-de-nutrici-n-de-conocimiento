from starlette.testclient import TestClient

from nutricion.config import Settings
from nutricion.web import create_app, process

SECRET = "s3cr3t"


class FakeStore:
    def __init__(self):
        self.kv = {}
        self.events = []
        self.closed = False

    def set(self, key, value):
        self.kv[key] = value

    def get(self, key):
        return self.kv.get(key)

    def log_event(self, kind, message, detail=""):
        self.events.append((kind, message, detail))

    def close(self):
        self.closed = True


class FakeMessenger:
    def __init__(self):
        self.sent = []

    def send_message(self, chat_id, text, buttons=None):
        self.sent.append(text)


class FakeAgent:
    def __init__(self, fail=False):
        self.fail = fail
        self.store = FakeStore()
        self.messenger = FakeMessenger()
        self.handled = []
        self.pills = []

    def daily_pill_if_due(self, force=False):
        self.pills.append(force)
        return True

    def handle_update(self, update):
        if self.fail:
            raise RuntimeError("Gemini 503")
        self.handled.append(update)


def settings() -> Settings:
    return Settings(
        _env_file=None, telegram_webhook_secret=SECRET, telegram_chat_id="1", cron_secret="Cron123"
    )


def test_webhook_rejects_requests_without_the_secret():
    agent = FakeAgent()
    client = TestClient(create_app(settings(), lambda s: agent))
    response = client.post("/telegram", json={"update_id": 1})
    assert response.status_code == 401
    assert agent.handled == []


def test_webhook_processes_update_with_valid_secret():
    agent = FakeAgent()
    client = TestClient(create_app(settings(), lambda s: agent))
    response = client.post(
        "/telegram",
        json={"update_id": 7},
        headers={"X-Telegram-Bot-Api-Secret-Token": settings().telegram_secret_token},
    )
    assert response.status_code == 200
    assert agent.handled == [{"update_id": 7}]
    assert agent.store.closed
    assert agent.store.events[0][0] == "traza" and "ok en" in agent.store.events[0][1]


def test_health_check():
    assert TestClient(create_app(settings(), lambda s: FakeAgent())).get("/").text == "ok"


def test_failed_update_is_logged_warns_user_and_is_not_retried(monkeypatch):
    sent = []
    monkeypatch.setattr(
        "nutricion.web.TelegramClient.send_message",
        lambda self, chat, text, buttons=None: sent.append((text, buttons)),
    )
    agent = FakeAgent(fail=True)
    process({"update_id": 9}, settings(), lambda s: agent)
    assert agent.store.kv["telegram_offset"] == "10"
    assert agent.store.kv["procesando"] == ""  # ya no está ocupado
    kind, message, detail = agent.store.events[0]
    assert kind == "error" and "Gemini 503" in message and "Traceback" in detail
    assert "Reportar problema" in sent[0][0] and sent[0][1][0][1] == "report"


def test_stuck_previous_job_warns_instead_of_waiting_forever(monkeypatch):
    import nutricion.web as web

    sent = []
    monkeypatch.setattr(
        "nutricion.web.TelegramClient.send_message",
        lambda self, chat, text, buttons=None: sent.append(text),
    )
    monkeypatch.setattr(web, "LOCK_TIMEOUT_S", 0.05)
    agent = FakeAgent()
    web._lock.acquire()  # simula una tarea anterior colgada
    try:
        process({"update_id": 1}, settings(), lambda s: agent)
    finally:
        web._lock.release()
    assert agent.handled == [] and "ocupado" in sent[0]


def test_diagnostics_reports_configuration_without_secrets():
    client = TestClient(create_app(settings(), lambda s: FakeAgent()))
    assert client.get("/diagnostico").status_code == 401
    data = client.get("/diagnostico?clave=Cron123").json()
    assert data["version"] == "desconocida" and data["nota_de_voz"] is True
    assert data["telegram_webhook_secret"] is True
    assert data["gemini_api_key"] is False
    assert SECRET not in str(data)


def test_unreachable_database_warns_user(monkeypatch):
    from nutricion.memory.store import DatabaseConnectionError

    sent = []
    monkeypatch.setattr(
        "nutricion.web.TelegramClient.send_message",
        lambda self, chat, text, buttons=None: sent.append(text),
    )

    def broken_factory(s):
        raise DatabaseConnectionError("mal")

    process({"update_id": 1}, settings(), broken_factory)
    assert "base de datos" in sent[0]


def test_secret_sent_to_telegram_uses_only_allowed_characters():
    import re

    base64_secret = "aB+c/d=="  # como los que genera Render
    token = Settings(_env_file=None, telegram_webhook_secret=base64_secret).telegram_secret_token
    assert re.fullmatch(r"[A-Za-z0-9_-]{1,256}", token)


def test_raw_secret_is_not_accepted_as_header():
    agent = FakeAgent()
    client = TestClient(create_app(settings(), lambda s: agent))
    response = client.post(
        "/telegram", json={"update_id": 1}, headers={"X-Telegram-Bot-Api-Secret-Token": SECRET}
    )
    assert response.status_code == 401


def test_cron_endpoint_requires_the_key():
    agent = FakeAgent()
    client = TestClient(create_app(settings(), lambda s: agent))
    assert client.get("/cron/pildora").status_code == 401
    assert client.get("/cron/pildora?clave=otra").status_code == 401
    assert agent.pills == []


def test_cron_endpoint_sends_daily_pill():
    agent = FakeAgent()
    client = TestClient(create_app(settings(), lambda s: agent))
    assert client.get("/cron/pildora?clave=Cron123").json()["ok"] is True
    assert client.post("/cron/pildora", headers={"X-Cron-Secret": "Cron123"}).status_code == 200
    assert client.get("/cron/pildora?clave=Cron123&forzar=1").status_code == 200
    assert agent.pills == [False, False, True]
    assert agent.store.closed


def test_diagnostics_requires_the_cron_key():
    client = TestClient(create_app(settings(), lambda s: FakeAgent()))
    assert client.get("/diagnostico?clave=mal").status_code == 401
    assert client.get("/diagnostico", headers={"X-Cron-Secret": "Cron123"}).status_code == 200
    assert client.get("/").text == "ok"  # el ping de cron-job.org sigue siendo público


class FlakyAgent(FakeAgent):
    """Falla las primeras `failures` píldoras diarias (Gemini saturado) y luego funciona."""

    def __init__(self, failures):
        super().__init__()
        self.failures = failures

    def daily_pill_if_due(self, force=False):
        self.pills.append(force)
        if len(self.pills) <= self.failures:
            raise RuntimeError("503 UNAVAILABLE")
        return True


def _run_with_fake_timer(agent, monkeypatch):
    from nutricion.web import run_daily_pill

    sent, delays = [], []
    monkeypatch.setattr(
        "nutricion.web.TelegramClient.send_message",
        lambda self, chat, text, buttons=None: sent.append(text),
    )

    def schedule(delay, action):
        delays.append(delay)
        action()  # sin esperar de verdad

    run_daily_pill(settings(), False, lambda s: agent, schedule=schedule)
    return sent, delays


def test_failed_daily_pill_is_retried_automatically(monkeypatch):
    agent = FlakyAgent(failures=2)
    sent, delays = _run_with_fake_timer(agent, monkeypatch)
    assert len(agent.pills) == 3 and delays == [600, 600]
    assert all("La reintentaré sola en 10 minutos" in t for t in sent) and len(sent) == 2


def test_daily_pill_gives_up_after_the_retries(monkeypatch):
    agent = FlakyAgent(failures=10)
    sent, delays = _run_with_fake_timer(agent, monkeypatch)
    assert len(agent.pills) == 4 and len(delays) == 3
    assert "/siguiente" in sent[-1]
