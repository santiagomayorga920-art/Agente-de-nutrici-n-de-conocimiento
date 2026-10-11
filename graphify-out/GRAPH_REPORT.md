# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-11)

## Corpus Check
- 44 files · ~13,729 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .ttf 2, .example 1)

## Summary
- 477 nodes · 1071 edges · 19 communities (15 shown, 4 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 136 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `24cdc661`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Settings
- feeds.py
- Agente de nutrición de conocimiento
- Desafiar y evaluar
- Investigar IA y negocios
- Store
- test_app.py
- TelegramClient
- card.py
- web.py
- nutricion
- Score
- session-start.sh
- Pill
- create_app
- Agent
- store.py

## God Nodes (most connected - your core abstractions)
1. `Store` - 44 edges
2. `Settings` - 30 edges
3. `Agent` - 25 edges
4. `create_app()` - 24 edges
5. `make_agent()` - 24 edges
6. `TelegramClient` - 23 edges
7. `Pill` - 21 edges
8. `Score` - 21 edges
9. `FakeMessenger` - 17 edges
10. `LessonState` - 16 edges

## Surprising Connections (you probably didn't know these)
- `test_url_without_template_is_left_alone()` --uses--> `Settings`  [INFERRED]
  tests/test_diagnose.py → src/nutricion/config.py
- `test_secret_sent_to_telegram_uses_only_allowed_characters()` --uses--> `Settings`  [INFERRED]
  tests/test_web.py → src/nutricion/config.py
- `Agente de nutrición de conocimiento` --references--> `LLMClient`  [INFERRED]
  CLAUDE.md → src/nutricion/llm/__init__.py
- `test_old_database_is_migrated()` --uses--> `Store`  [INFERRED]
  tests/test_sources.py → src/nutricion/memory/store.py
- `FakeLLM` --uses--> `Evaluation`  [INFERRED]
  tests/test_app.py → src/nutricion/agents/tutor.py

## Import Cycles
- None detected.

## Communities (19 total, 4 thin omitted)

### Community 0 - "Settings"
Cohesion: 0.07
Nodes (16): get_settings(), Settings, build_agent(), GeminiClient, get_llm(), MissingAPIKey, annotate(), _database_status() (+8 more)

### Community 1 - "feeds.py"
Cohesion: 0.08
Nodes (22): Category, category_of_the_day(), Source, Candidate, _clean(), _entry_image(), fetch_candidates(), fetch_source() (+14 more)

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.20
Nodes (9): Agente de nutrición de conocimiento, Automatización final (Render + cron-job.org), Ejecución por GitHub Actions (modo anterior, sin servidor), Estructura, Graphify, Modo tiempo real (webhook en Render + Supabase), Puesta en marcha, Sesiones en la nube (Claude Code) (+1 more)

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.33
Nodes (5): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío, Posturas de respuesta rápida (botones)

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.33
Nodes (5): Criterios de selección, Formato de la píldora, Investigar IA y negocios, Objetivo, Rigor de las fuentes (de más a menos peso)

### Community 5 - "Store"
Cohesion: 0.14
Nodes (9): Lesson, _migrate(), _now(), Store, _to_lesson(), diagnostics(), store(), test_import_from_sqlite_keeps_scores_and_skips_duplicates() (+1 more)

### Community 6 - "test_app.py"
Cohesion: 0.10
Nodes (23): TelegramError, FakeLLM, FakeMessenger, make_agent(), news(), test_answer_is_evaluated_and_offers_next_button(), test_button_choice_gets_a_reaction_and_is_used_in_evaluation(), test_button_from_finished_lesson_is_rejected() (+15 more)

### Community 7 - "TelegramClient"
Cohesion: 0.19
Nodes (3): _keyboard(), TelegramClient, lifespan()

### Community 8 - "card.py"
Cohesion: 0.14
Nodes (17): _background(), build_card(), _ellipsize(), fetch_background(), _fit(), _font(), _gradient(), render_card() (+9 more)

### Community 9 - "web.py"
Cohesion: 0.05
Nodes (9): Messenger, __getattr__(), _now(), job(), _record_error(), run_daily_pill(), _run_locked(), _trace() (+1 more)

### Community 13 - "Score"
Cohesion: 0.10
Nodes (19): _bar(), _days(), feedback(), pill_body(), pill_header(), profile_card(), progress_line(), reminder() (+11 more)

### Community 15 - "Pill"
Cohesion: 0.09
Nodes (13): Agente de nutrición de conocimiento, graphify, create_pill(), _PillDraft, _shorten(), load_skill(), evaluate(), Evaluation (+5 more)

### Community 16 - "create_app"
Cohesion: 0.10
Nodes (25): DatabaseConnectionError, create_app(), authorized(), cron_daily_pill(), diagnose(), telegram(), _describe(), process() (+17 more)

### Community 17 - "Agent"
Cohesion: 0.24
Nodes (3): Agent, test_same_story_from_another_source_is_not_repeated(), same_story()

### Community 18 - "store.py"
Cohesion: 0.08
Nodes (22): InvalidTransition, LessonState, transition(), connection_summary(), database_url_problems(), explain_connection_error(), _sanitized(), test_common_mistakes_are_explained() (+14 more)

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 161 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Store` connect `Store` to `Settings`, `feeds.py`, `test_app.py`, `web.py`, `Score`, `Pill`, `create_app`, `Agent`, `store.py`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `Store` (e.g. with `Agent` and `Lesson`) actually correct?**
  _`Store` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Settings` be split into smaller, more focused modules?**
  _Cohesion score 0.07039187227866474 - nodes in this community are weakly interconnected._
- **Why does `Agent` connect `Agent` to `Settings`, `Store`, `test_app.py`, `web.py`, `Score`, `Pill`, `store.py`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Settings` (e.g. with `build_agent()` and `get_llm()`) actually correct?**
  _`Settings` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `feeds.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08421985815602837 - nodes in this community are weakly interconnected._