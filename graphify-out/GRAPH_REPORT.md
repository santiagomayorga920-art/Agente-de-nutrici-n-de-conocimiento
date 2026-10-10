# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-10)

## Corpus Check
- 41 files · ~10,197 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: .example 1, (none) 1)

## Summary
- 391 nodes · 859 edges · 19 communities (14 shown, 5 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 117 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `32e7fa91`
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
- researcher.py
- web.py
- Agent
- test_diagnose.py

## God Nodes (most connected - your core abstractions)
1. `Store` - 42 edges
2. `Settings` - 24 edges
3. `Agent` - 22 edges
4. `Score` - 21 edges
5. `TelegramClient` - 20 edges
6. `make_agent()` - 19 edges
7. `create_app()` - 18 edges
8. `LessonState` - 16 edges
9. `Pill` - 15 edges
10. `Lesson` - 15 edges

## Surprising Connections (you probably didn't know these)
- `test_secret_sent_to_telegram_uses_only_allowed_characters()` --uses--> `Settings`  [INFERRED]
  tests/test_web.py → src/nutricion/config.py
- `Agente de nutrición de conocimiento` --references--> `LLMClient`  [INFERRED]
  CLAUDE.md → src/nutricion/llm/__init__.py
- `test_old_database_is_migrated()` --uses--> `Store`  [INFERRED]
  tests/test_sources.py → src/nutricion/memory/store.py
- `FakeLLM` --uses--> `Evaluation`  [INFERRED]
  tests/test_app.py → src/nutricion/agents/tutor.py
- `make_agent()` --uses--> `Agent`  [INFERRED]
  tests/test_app.py → src/nutricion/app.py

## Import Cycles
- None detected.

## Communities (19 total, 5 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.07
Nodes (16): get_settings(), Settings, build_agent(), GeminiClient, get_llm(), MissingAPIKey, annotate(), _database_status() (+8 more)

### Community 1 - "feeds.py"
Cohesion: 0.09
Nodes (22): Category, category_of_the_day(), Source, Candidate, _clean(), _entry_image(), fetch_candidates(), fetch_source() (+14 more)

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.22
Nodes (8): Agente de nutrición de conocimiento, Ejecución automática (GitHub Actions), Estructura, Graphify, Modo tiempo real (webhook en Render + Supabase), Puesta en marcha, Sesiones en la nube (Claude Code), Si algo falla

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.33
Nodes (5): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío, Posturas de respuesta rápida (botones)

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.33
Nodes (5): Criterios de selección, Formato de la píldora, Investigar IA y negocios, Objetivo, Rigor de las fuentes (de más a menos peso)

### Community 5 - "app.py"
Cohesion: 0.13
Nodes (7): InvalidTransition, LessonState, transition(), _to_lesson(), test_cannot_skip_waiting_for_answer(), test_failed_evaluation_returns_to_waiting(), test_happy_path()

### Community 6 - "test_app.py"
Cohesion: 0.12
Nodes (17): FakeLLM, FakeMessenger, make_agent(), news(), test_answer_is_evaluated_and_offers_next_button(), test_button_choice_gets_a_reaction_and_is_used_in_evaluation(), test_button_from_finished_lesson_is_rejected(), test_daily_pill_is_sent_as_photo_with_option_buttons() (+9 more)

### Community 7 - "TelegramClient"
Cohesion: 0.16
Nodes (4): _keyboard(), TelegramClient, TelegramError, lifespan()

### Community 9 - "Store"
Cohesion: 0.12
Nodes (8): Lesson, _now(), Store, pill(), store(), test_import_from_sqlite_keeps_scores_and_skips_duplicates(), test_lesson_lifecycle_and_scores(), test_old_database_scores_are_backfilled()

### Community 13 - "Score"
Cohesion: 0.10
Nodes (19): _bar(), _days(), feedback(), pill_body(), pill_header(), profile_card(), progress_line(), reminder() (+11 more)

### Community 15 - "researcher.py"
Cohesion: 0.10
Nodes (11): Agente de nutrición de conocimiento, graphify, create_pill(), _PillDraft, load_skill(), evaluate(), Evaluation, react_to_choice() (+3 more)

### Community 16 - "web.py"
Cohesion: 0.08
Nodes (20): DatabaseConnectionError, create_app(), diagnose(), diagnostics(), telegram(), __getattr__(), process(), FakeAgent (+12 more)

### Community 17 - "Agent"
Cohesion: 0.31
Nodes (3): Agent, test_same_story_from_another_source_is_not_repeated(), same_story()

### Community 18 - "test_diagnose.py"
Cohesion: 0.21
Nodes (6): database_url_problems(), explain_connection_error(), test_common_mistakes_are_explained(), test_correct_session_pooler_uri_has_no_problems(), test_unreachable_postgres_raises_a_readable_error(), test_wrong_password_is_explained_without_leaking_it()

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 141 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Store` connect `Store` to `main.py`, `feeds.py`, `app.py`, `test_app.py`, `Score`, `researcher.py`, `web.py`, `Agent`, `test_diagnose.py`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `Store` (e.g. with `Agent` and `Lesson`) actually correct?**
  _`Store` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07390648567119155 - nodes in this community are weakly interconnected._
- **Why does `TelegramClient` connect `TelegramClient` to `main.py`, `web.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Settings` (e.g. with `build_agent()` and `get_llm()`) actually correct?**
  _`Settings` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `feeds.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08603145235892692 - nodes in this community are weakly interconnected._