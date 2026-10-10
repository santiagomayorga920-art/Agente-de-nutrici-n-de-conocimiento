from starlette.testclient import TestClient

from nutricion.config import Settings
from nutricion.web import create_app, process

SECRET = "s3cr3t"


class FakeStore:
    def __init__(self):
        self.kv = {}
        self.closed = False

    def set(self, key, value):
        self.kv[key] = value

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

    def handle_update(self, update):
        if self.fail:
            raise RuntimeError("Gemini 503")
        self.handled.append(update)


def settings() -> Settings:
    return Settings(_env_file=None, telegram_webhook_secret=SECRET, telegram_chat_id="1")


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
        headers={"X-Telegram-Bot-Api-Secret-Token": SECRET},
    )
    assert response.status_code == 200
    assert agent.handled == [{"update_id": 7}]
    assert agent.store.closed


def test_health_check():
    assert TestClient(create_app(settings(), lambda s: FakeAgent())).get("/").text == "ok"


def test_failed_update_warns_user_and_is_not_retried_forever():
    agent = FakeAgent(fail=True)
    process({"update_id": 9}, settings(), lambda s: agent)
    assert agent.store.kv["telegram_offset"] == "10"
    assert "Vuelve a enviarlo" in agent.messenger.sent[0]
