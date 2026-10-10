# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-10)

## Corpus Check
- 38 files · ~9,196 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: .example 1, (none) 1)

## Summary
- 357 nodes · 769 edges · 18 communities (13 shown, 5 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 98 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `19974751`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- feeds.py
- Agente de nutrición de conocimiento
- Desafiar y evaluar
- Investigar IA y negocios
- app.py
- test_app.py
- TelegramClient
- Messenger
- Store
- nutricion
- Score
- session-start.sh
- tutor.py
- web.py
- Agent

## God Nodes (most connected - your core abstractions)
1. `Store` - 36 edges
2. `Agent` - 22 edges
3. `Score` - 21 edges
4. `Settings` - 19 edges
5. `make_agent()` - 19 edges
6. `TelegramClient` - 18 edges
7. `LessonState` - 16 edges
8. `Pill` - 15 edges
9. `Lesson` - 15 edges
10. `build_profile()` - 15 edges

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

## Communities (18 total, 5 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.09
Nodes (13): get_settings(), Settings, GeminiClient, get_llm(), MissingAPIKey, main(), _migrate(), _print_stats() (+5 more)

### Community 1 - "feeds.py"
Cohesion: 0.08
Nodes (23): create_pill(), Category, category_of_the_day(), Source, Candidate, _clean(), _entry_image(), fetch_candidates() (+15 more)

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.25
Nodes (7): Agente de nutrición de conocimiento, Ejecución automática (GitHub Actions), Estructura, Graphify, Modo tiempo real (webhook en Render + Supabase), Puesta en marcha, Sesiones en la nube (Claude Code)

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.33
Nodes (5): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío, Posturas de respuesta rápida (botones)

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.33
Nodes (5): Criterios de selección, Formato de la píldora, Investigar IA y negocios, Objetivo, Rigor de las fuentes (de más a menos peso)

### Community 5 - "app.py"
Cohesion: 0.11
Nodes (11): InvalidTransition, LessonState, Pill, transition(), _to_lesson(), test_cannot_skip_waiting_for_answer(), test_failed_evaluation_returns_to_waiting(), test_happy_path() (+3 more)

### Community 6 - "test_app.py"
Cohesion: 0.12
Nodes (17): FakeLLM, FakeMessenger, make_agent(), news(), test_answer_is_evaluated_and_offers_next_button(), test_button_choice_gets_a_reaction_and_is_used_in_evaluation(), test_button_from_finished_lesson_is_rejected(), test_daily_pill_is_sent_as_photo_with_option_buttons() (+9 more)

### Community 7 - "TelegramClient"
Cohesion: 0.16
Nodes (4): _keyboard(), TelegramClient, TelegramError, lifespan()

### Community 9 - "Store"
Cohesion: 0.16
Nodes (5): Lesson, _now(), Store, store(), test_import_from_sqlite_keeps_scores_and_skips_duplicates()

### Community 13 - "Score"
Cohesion: 0.10
Nodes (19): _bar(), _days(), feedback(), pill_body(), pill_header(), profile_card(), progress_line(), reminder() (+11 more)

### Community 15 - "tutor.py"
Cohesion: 0.10
Nodes (9): Agente de nutrición de conocimiento, graphify, _PillDraft, load_skill(), evaluate(), Evaluation, react_to_choice(), LLMClient (+1 more)

### Community 16 - "web.py"
Cohesion: 0.09
Nodes (12): create_app(), telegram(), __getattr__(), process(), FakeAgent, FakeMessenger, FakeStore, settings() (+4 more)

### Community 17 - "Agent"
Cohesion: 0.31
Nodes (3): Agent, test_same_story_from_another_source_is_not_repeated(), same_story()

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 130 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Store` connect `Store` to `main.py`, `feeds.py`, `app.py`, `test_app.py`, `Score`, `web.py`, `Agent`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `Store` (e.g. with `Agent` and `Lesson`) actually correct?**
  _`Store` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08748615725359911 - nodes in this community are weakly interconnected._
- **Why does `Agent` connect `Agent` to `main.py`, `app.py`, `test_app.py`, `TelegramClient`, `Store`, `Score`, `web.py`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Agent` (e.g. with `TelegramError` and `Lesson`) actually correct?**
  _`Agent` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `feeds.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07767722473604827 - nodes in this community are weakly interconnected._