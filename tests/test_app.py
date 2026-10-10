import pytest

from nutricion.agents.researcher import Candidate, _PillDraft
from nutricion.agents.tutor import Evaluation
from nutricion.app import NO_PENDING, OFFSET_KEY, Agent
from nutricion.domain.lesson import LessonState
from nutricion.memory.store import Store

CHAT = "111"


class FakeLLM:
    def __init__(self, fail_evaluation: bool = False) -> None:
        self.fail_evaluation = fail_evaluation

    def generate(self, system, prompt):
        return "hola"

    def generate_structured(self, system, prompt, schema):
        if schema is _PillDraft:
            return _PillDraft(
                candidate_number=2,
                headline="Titular",
                what_happened="Pasó algo.",
                why_it_matters="Importa.",
                challenge="¿Invertirías?",
            )
        if self.fail_evaluation:
            raise RuntimeError("API caída")
        return Evaluation(comprension=4, razonamiento=9, perspectiva_negocio=3, feedback="Bien.")


class FakeMessenger:
    def __init__(self) -> None:
        self.inbox: list[dict] = []
        self.sent: list[str] = []

    def receive(self, text: str, chat_id: str = CHAT) -> None:
        update_id = len(self.inbox) + 100
        self.inbox.append(
            {"update_id": update_id, "message": {"chat": {"id": int(chat_id)}, "text": text}}
        )

    def get_updates(self, offset):
        return [u for u in self.inbox if u["update_id"] >= offset]

    def send_message(self, chat_id, text):
        assert chat_id == CHAT
        self.sent.append(text)


def news(seen):
    return [Candidate("A", "https://a", ""), Candidate("B", "https://b", "")]


def make_agent(llm=None):
    store = Store(":memory:")
    messenger = FakeMessenger()
    agent = Agent(store, llm or FakeLLM(), messenger, CHAT, fetch_candidates=news)
    return agent, store, messenger


def test_daily_pill_is_sent_and_waits_for_answer():
    agent, store, messenger = make_agent()
    agent.tick(send_daily_pill=True)
    lesson = store.open_lesson()
    assert lesson.state is LessonState.AWAITING_ANSWER
    assert lesson.pill.source_url == "https://b"
    assert "¿Invertirías?" in messenger.sent[-1]


def test_answer_is_evaluated_and_lesson_completed():
    agent, store, messenger = make_agent()
    agent.tick(send_daily_pill=True)
    messenger.receive("Creo que sí porque reduce costos.")
    agent.tick(send_daily_pill=False)
    assert store.open_lesson() is None
    assert "Razonamiento 5/5" in messenger.sent[-1]  # la nota fuera de rango se acota
    assert store.get(OFFSET_KEY) == "101"


def test_next_pill_requires_answering_first():
    agent, store, messenger = make_agent()
    agent.tick(send_daily_pill=True)
    messenger.receive("/siguiente")
    agent.tick(send_daily_pill=False)
    assert messenger.sent[-1].startswith("Primero responde")


def test_daily_run_reminds_pending_challenge_instead_of_new_pill():
    agent, store, messenger = make_agent()
    agent.tick(send_daily_pill=True)
    agent.tick(send_daily_pill=True)
    assert messenger.sent[-1].startswith("⏳")
    assert len(store.seen_urls()) == 1


def test_messages_from_other_chats_are_ignored():
    agent, store, messenger = make_agent()
    messenger.receive("hola", chat_id="999")
    agent.tick(send_daily_pill=False)
    assert messenger.sent == []
    assert store.get(OFFSET_KEY) == "101"


def test_message_without_pending_challenge():
    agent, store, messenger = make_agent()
    messenger.receive("hola")
    agent.tick(send_daily_pill=False)
    assert messenger.sent == [NO_PENDING]


def test_failed_evaluation_is_retried_next_tick():
    agent, store, messenger = make_agent(FakeLLM(fail_evaluation=True))
    agent.tick(send_daily_pill=True)
    messenger.receive("Mi respuesta")
    with pytest.raises(RuntimeError):
        agent.tick(send_daily_pill=False)
    assert store.open_lesson().state is LessonState.AWAITING_ANSWER
    assert store.get(OFFSET_KEY) is None  # el mensaje se volverá a procesar

    agent.llm = FakeLLM()
    agent.tick(send_daily_pill=False)
    assert store.open_lesson() is None
