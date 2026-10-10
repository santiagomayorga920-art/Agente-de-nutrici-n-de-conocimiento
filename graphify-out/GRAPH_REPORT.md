# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-10)

## Corpus Check
- 33 files · ~6,261 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: .example 1, (none) 1)

## Summary
- 252 nodes · 498 edges · 15 communities (10 shown, 5 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 50 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `73676c21`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- feeds.py
- Agente de nutrición de conocimiento
- Desafiar y evaluar
- Investigar IA y negocios
- store.py
- test_app.py
- TelegramClient
- app.py
- Store
- nutricion
- session-start.sh
- researcher.py

## God Nodes (most connected - your core abstractions)
1. `Store` - 22 edges
2. `Agent` - 19 edges
3. `make_agent()` - 16 edges
4. `LessonState` - 15 edges
5. `Lesson` - 15 edges
6. `Pill` - 14 edges
7. `fetch_source()` - 13 edges
8. `FakeMessenger` - 13 edges
9. `LLMClient` - 12 edges
10. `Category` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Agente de nutrición de conocimiento` --references--> `LLMClient`  [INFERRED]
  CLAUDE.md → src/nutricion/llm/__init__.py
- `test_old_database_is_migrated()` --uses--> `Store`  [INFERRED]
  tests/test_sources.py → src/nutricion/memory/store.py
- `FakeLLM` --uses--> `Evaluation`  [INFERRED]
  tests/test_app.py → src/nutricion/agents/tutor.py
- `make_agent()` --uses--> `Agent`  [INFERRED]
  tests/test_app.py → src/nutricion/app.py
- `FakeMessenger` --uses--> `TelegramError`  [INFERRED]
  tests/test_app.py → src/nutricion/channels/telegram.py

## Import Cycles
- None detected.

## Communities (15 total, 5 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.09
Nodes (11): get_settings(), Settings, GeminiClient, get_llm(), MissingAPIKey, main(), _require(), _run_tick() (+3 more)

### Community 1 - "feeds.py"
Cohesion: 0.09
Nodes (20): Category, category_of_the_day(), Source, Candidate, _clean(), _entry_image(), fetch_candidates(), fetch_source() (+12 more)

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.29
Nodes (6): Agente de nutrición de conocimiento, Ejecución automática (GitHub Actions), Estructura, Graphify, Puesta en marcha, Sesiones en la nube (Claude Code)

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.33
Nodes (5): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío, Posturas de respuesta rápida (botones)

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.33
Nodes (5): Criterios de selección, Formato de la píldora, Investigar IA y negocios, Objetivo, Rigor de las fuentes (de más a menos peso)

### Community 5 - "store.py"
Cohesion: 0.19
Nodes (7): InvalidTransition, LessonState, transition(), _to_lesson(), test_cannot_skip_waiting_for_answer(), test_failed_evaluation_returns_to_waiting(), test_happy_path()

### Community 6 - "test_app.py"
Cohesion: 0.14
Nodes (14): FakeLLM, FakeMessenger, make_agent(), news(), test_answer_is_evaluated_and_offers_next_button(), test_button_choice_gets_a_reaction_and_is_used_in_evaluation(), test_button_from_finished_lesson_is_rejected(), test_daily_pill_is_sent_as_photo_with_option_buttons() (+6 more)

### Community 7 - "TelegramClient"
Cohesion: 0.21
Nodes (3): _keyboard(), TelegramClient, TelegramError

### Community 9 - "Store"
Cohesion: 0.15
Nodes (3): Agent, Lesson, Store

### Community 15 - "researcher.py"
Cohesion: 0.08
Nodes (14): Agente de nutrición de conocimiento, graphify, create_pill(), _PillDraft, load_skill(), evaluate(), Evaluation, react_to_choice() (+6 more)

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 99 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Store` connect `Store` to `main.py`, `feeds.py`, `store.py`, `test_app.py`, `app.py`, `researcher.py`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Store` (e.g. with `Agent` and `Lesson`) actually correct?**
  _`Store` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0931174089068826 - nodes in this community are weakly interconnected._
- **Why does `Agent` connect `Store` to `main.py`, `store.py`, `test_app.py`, `TelegramClient`, `app.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Agent` (e.g. with `TelegramError` and `Lesson`) actually correct?**
  _`Agent` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `feeds.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08888888888888889 - nodes in this community are weakly interconnected._