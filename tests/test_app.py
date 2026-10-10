import pytest

from nutricion.agents.researcher import _PillDraft
from nutricion.agents.tutor import Evaluation
from nutricion.app import NEXT, NO_PENDING, OFFSET_KEY, Agent
from nutricion.channels.telegram import TelegramError
from nutricion.domain.lesson import LessonState
from nutricion.memory.store import Store
from nutricion.sources.catalog import Category
from nutricion.sources.feeds import Candidate, NoNewsFound

CHAT = "111"


class FakeLLM:
    def __init__(self, fail_evaluation: bool = False) -> None:
        self.fail_evaluation = fail_evaluation
        self.prompts: list[str] = []

    def generate(self, system, prompt):
        self.prompts.append(prompt)
        return "Ojo con el riesgo regulatorio. ¿Por qué lo elegiste?"

    def generate_structured(self, system, prompt, schema):
        self.prompts.append(prompt)
        if schema is _PillDraft:
            return _PillDraft(
                candidate_number=2,
                headline="Titular <importante>",
                what_happened="Pasó algo.",
                why_it_matters="Importa.",
                challenge="¿Invertirías?",
                options=["Sí, de inmediato", "Esperaría", "No invertiría"],
            )
        if self.fail_evaluation:
            raise RuntimeError("API caída")
        return Evaluation(comprension=4, razonamiento=9, perspectiva_negocio=3, feedback="Bien.")


class FakeMessenger:
    def __init__(self, photo_fails: bool = False) -> None:
        self.photo_fails = photo_fails
        self.inbox: list[dict] = []
        self.sent: list[dict] = []
        self.answered: list[str] = []
        self.cleared: list[int] = []

    def receive(self, text: str, chat_id: str = CHAT) -> None:
        self._push({"message": {"chat": {"id": int(chat_id)}, "text": text}})

    def press(self, data: str, chat_id: str = CHAT) -> None:
        message = {"message_id": 55, "chat": {"id": int(chat_id)}}
        self._push({"callback_query": {"id": "cb1", "data": data, "message": message}})

    def _push(self, update: dict) -> None:
        self.inbox.append({"update_id": len(self.inbox) + 100, **update})

    def get_updates(self, offset):
        return [u for u in self.inbox if u["update_id"] >= offset]

    def send_message(self, chat_id, text, buttons=None):
        assert chat_id == CHAT
        self.sent.append({"kind": "text", "text": text, "buttons": buttons})

    def send_photo(self, chat_id, photo_url, caption, buttons=None):
        if self.photo_fails:
            raise TelegramError("wrong file identifier")
        self.sent.append({"kind": "photo", "url": photo_url, "text": caption, "buttons": buttons})

    def send_typing(self, chat_id):
        pass

    def answer_callback(self, callback_id, text=""):
        self.answered.append(callback_id)

    def remove_buttons(self, chat_id, message_id):
        self.cleared.append(message_id)


def news(seen):
    # Como el feed real: nunca devuelve noticias ya enviadas
    n = len(seen)
    return [
        Candidate("A", f"https://a/{n}", "", "Medio A", Category.NEGOCIOS),
        Candidate("B", f"https://b/{n}", "", "arXiv", Category.INVESTIGACION, "https://img/b.png"),
    ]


def make_agent(llm=None, messenger=None, image=""):
    store = Store(":memory:")
    messenger = messenger or FakeMessenger()
    agent = Agent(
        store, llm or FakeLLM(), messenger, CHAT, fetch_candidates=news, find_image=lambda u: image
    )
    return agent, store, messenger


def test_daily_pill_is_sent_as_photo_with_option_buttons():
    agent, store, messenger = make_agent()
    agent.tick(send_daily_pill=True)
    lesson = store.open_lesson()
    assert lesson.state is LessonState.AWAITING_ANSWER
    assert lesson.pill.source_name == "arXiv"
    last = messenger.sent[-1]
    assert last["kind"] == "photo" and last["url"] == "https://img/b.png"
    assert "Titular &lt;importante&gt;" in last["text"]  # el texto del LLM se escapa
    assert last["buttons"][1] == ("Esperaría", f"op:{lesson.id}:1")


def test_unreachable_image_falls_back_to_text():
    agent, store, messenger = make_agent(messenger=FakeMessenger(photo_fails=True))
    agent.tick(send_daily_pill=True)
    assert [m["kind"] for m in messenger.sent] == ["text", "text"]  # perfil + píldora
    assert messenger.sent[1]["buttons"]


def test_first_pill_prefers_the_first_category():
    llm = FakeLLM()
    agent, _, _ = make_agent(llm)
    agent.tick(send_daily_pill=True)
    assert "«Negocios»" in llm.prompts[0]


def test_button_choice_gets_a_reaction_and_is_used_in_evaluation():
    llm = FakeLLM()
    agent, store, messenger = make_agent(llm)
    agent.tick(send_daily_pill=True)
    lesson_id = store.open_lesson().id
    messenger.press(f"op:{lesson_id}:1")
    agent.tick(send_daily_pill=False)
    assert messenger.answered == ["cb1"] and messenger.cleared == [55]
    assert "Elegiste: <b>Esperaría</b>" in messenger.sent[-1]["text"]
    assert store.open_lesson().choice == "Esperaría"

    messenger.receive("Porque la regulación aún no está clara.")
    agent.tick(send_daily_pill=False)
    assert "«Esperaría»" in llm.prompts[-1]
    assert store.open_lesson() is None


def test_answer_is_evaluated_and_offers_next_button():
    agent, store, messenger = make_agent()
    agent.tick(send_daily_pill=True)
    messenger.receive("Creo que sí porque reduce costos.")
    agent.tick(send_daily_pill=False)
    assert store.open_lesson() is None
    assert "Razonamiento 5/5" in messenger.sent[-1]["text"]  # la nota fuera de rango se acota
    assert messenger.sent[-1]["buttons"] == [("➡️ Siguiente píldora", NEXT)]

    messenger.press(NEXT)
    agent.tick(send_daily_pill=False)
    assert store.open_lesson().state is LessonState.AWAITING_ANSWER


def test_button_from_finished_lesson_is_rejected():
    agent, store, messenger = make_agent()
    agent.tick(send_daily_pill=True)
    messenger.receive("respuesta")
    messenger.press("op:1:0")
    agent.tick(send_daily_pill=False)
    assert messenger.sent[-1]["text"].startswith("Ese desafío ya terminó")


def test_next_pill_requires_answering_first():
    agent, store, messenger = make_agent()
    agent.tick(send_daily_pill=True)
    messenger.receive("/siguiente")
    agent.tick(send_daily_pill=False)
    assert "pendiente" in messenger.sent[-1]["text"]
    assert len(store.seen_urls()) == 1


def test_messages_from_other_chats_are_ignored():
    agent, store, messenger = make_agent()
    messenger.receive("hola", chat_id="999")
    messenger.press(NEXT, chat_id="999")
    agent.tick(send_daily_pill=False)
    assert messenger.sent == []
    assert store.get(OFFSET_KEY) == "102"


def test_message_without_pending_challenge():
    agent, store, messenger = make_agent()
    messenger.receive("hola")
    agent.tick(send_daily_pill=False)
    assert messenger.sent[0]["text"] == NO_PENDING


def test_stats_command_shows_profile_after_lessons():
    agent, store, messenger = make_agent()
    messenger.receive("/stats")
    agent.tick(send_daily_pill=False)
    assert "Aún no has completado" in messenger.sent[-1]["text"]

    agent.tick(send_daily_pill=True)
    messenger.receive("Mi análisis")
    messenger.receive("/stats")
    agent.tick(send_daily_pill=False)
    card = messenger.sent[-1]["text"]
    assert "Píldoras completadas: <b>1</b>" in card
    assert "Racha: <b>1 día</b>" in card
    assert "Promedio general: <b>4.0/5</b>" in card  # (4 + 5 + 3) / 3
    assert "Punto a reforzar: <b>Negocio</b>" in card


def test_daily_pill_starts_with_profile_card():
    agent, store, messenger = make_agent()
    agent.tick(send_daily_pill=True)
    assert messenger.sent[0]["text"].startswith("👤 <b>Tu perfil</b>")


def test_same_story_from_another_source_is_not_repeated():
    llm = FakeLLM()
    store = Store(":memory:")
    messenger = FakeMessenger()

    def same_story(seen):
        n = len(seen)
        return [
            Candidate("Nvidia compra X - Bloomberg", f"https://bbg/{n}", "", "Bloomberg"),
            Candidate("Nvidia compra X - Reuters", f"https://reu/{n}", "", "Reuters"),
        ]

    agent = Agent(store, llm, messenger, CHAT, fetch_candidates=same_story, find_image=lambda u: "")
    agent.tick(send_daily_pill=True)
    messenger.receive("respuesta")
    agent.tick(send_daily_pill=False)
    with pytest.raises(NoNewsFound):
        agent.daily_pill()


def test_repeated_update_is_ignored():
    agent, store, messenger = make_agent()
    agent.tick(send_daily_pill=True)
    messenger.receive("respuesta")
    update = messenger.inbox[-1]
    agent.handle_update(update)
    sent = len(messenger.sent)
    agent.handle_update(update)  # Telegram reenvía la misma actualización
    assert len(messenger.sent) == sent


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


def test_daily_pill_is_sent_only_once_per_day():
    agent, store, messenger = make_agent()
    assert agent.daily_pill_if_due() is True
    sent = len(messenger.sent)
    assert agent.daily_pill_if_due() is False  # el cron repetido no envía nada
    assert len(messenger.sent) == sent
    assert agent.daily_pill_if_due(force=True) is True
