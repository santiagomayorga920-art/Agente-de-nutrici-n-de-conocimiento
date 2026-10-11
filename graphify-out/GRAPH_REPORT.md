# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-11)

## Corpus Check
- 47 files · ~16,515 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .ttf 2, .example 1)

## Summary
- 553 nodes · 1260 edges · 21 communities (15 shown, 6 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 154 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `08881c38`
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
- Messenger
- nutricion
- Score
- session-start.sh
- Pill
- create_app
- Agent
- test_diagnose.py
- voice.py
- app.py

## God Nodes (most connected - your core abstractions)
1. `Store` - 45 edges
2. `Pill` - 31 edges
3. `Settings` - 30 edges
4. `Agent` - 28 edges
5. `make_agent()` - 28 edges
6. `TelegramClient` - 24 edges
7. `create_app()` - 24 edges
8. `Score` - 21 edges
9. `FakeMessenger` - 18 edges
10. `LessonState` - 17 edges

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

## Communities (21 total, 6 thin omitted)

### Community 0 - "Settings"
Cohesion: 0.07
Nodes (19): get_settings(), Settings, build_agent(), GeminiClient, get_llm(), MissingAPIKey, annotate(), _database_status() (+11 more)

### Community 1 - "feeds.py"
Cohesion: 0.09
Nodes (22): Category, category_of_the_day(), Source, Candidate, _clean(), _entry_image(), fetch_candidates(), fetch_source() (+14 more)

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.17
Nodes (11): Agente de nutrición de conocimiento, Automatización final (Render + cron-job.org), Contenido de la píldora, Ejecución por GitHub Actions (modo anterior, sin servidor), Estructura, Graphify, Modo tiempo real (webhook en Render + Supabase), Multimedia de la píldora (+3 more)

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.33
Nodes (5): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío, Posturas de respuesta rápida (botones)

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.25
Nodes (7): Criterios de selección, Formato de la píldora, Glosario rápido, Investigar IA y negocios, Objetivo, Rigor de las fuentes (de más a menos peso), Variedad temática (obligatoria)

### Community 5 - "Store"
Cohesion: 0.08
Nodes (17): InvalidTransition, Lesson, LessonState, transition(), _migrate(), _now(), Store, _to_lesson() (+9 more)

### Community 6 - "test_app.py"
Cohesion: 0.09
Nodes (26): FakeLLM, FakeMessenger, make_agent(), news(), test_answer_is_evaluated_and_offers_next_button(), test_button_choice_gets_a_reaction_and_is_used_in_evaluation(), test_button_from_finished_lesson_is_rejected(), test_daily_pill_is_sent_as_photo_with_option_buttons() (+18 more)

### Community 7 - "TelegramClient"
Cohesion: 0.14
Nodes (4): _keyboard(), TelegramClient, TelegramError, lifespan()

### Community 8 - "card.py"
Cohesion: 0.14
Nodes (17): _background(), build_card(), _ellipsize(), fetch_background(), _fit(), _font(), _gradient(), render_card() (+9 more)

### Community 13 - "Score"
Cohesion: 0.09
Nodes (20): _bar(), _days(), feedback(), glossary(), pill_body(), pill_header(), profile_card(), progress_line() (+12 more)

### Community 15 - "Pill"
Cohesion: 0.07
Nodes (28): Agente de nutrición de conocimiento, graphify, create_pill(), diversify(), _GlossaryEntry, _history(), keyword_angle(), _PillDraft (+20 more)

### Community 16 - "create_app"
Cohesion: 0.10
Nodes (25): DatabaseConnectionError, create_app(), authorized(), cron_daily_pill(), diagnose(), telegram(), _describe(), process() (+17 more)

### Community 18 - "test_diagnose.py"
Cohesion: 0.13
Nodes (14): connection_summary(), database_url_problems(), explain_connection_error(), _sanitized(), test_common_mistakes_are_explained(), test_connection_summary_hides_password(), test_correct_session_pooler_uri_has_no_problems(), test_password_variable_fills_the_supabase_template() (+6 more)

### Community 19 - "voice.py"
Cohesion: 0.08
Nodes (16): as_wav(), retry_delay(), build_voice(), script(), _sentence(), to_mp3(), Voice, normalize_title() (+8 more)

### Community 20 - "app.py"
Cohesion: 0.07
Nodes (8): __getattr__(), _now(), job(), _record_error(), run_daily_pill(), _run_locked(), _trace(), _warn()

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 183 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Store` connect `Store` to `Settings`, `feeds.py`, `test_app.py`, `Score`, `Pill`, `create_app`, `Agent`, `test_diagnose.py`, `app.py`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `Store` (e.g. with `Agent` and `Lesson`) actually correct?**
  _`Store` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Settings` be split into smaller, more focused modules?**
  _Cohesion score 0.06753246753246753 - nodes in this community are weakly interconnected._
- **Why does `Pill` connect `Pill` to `Store`, `card.py`, `Score`, `Agent`, `voice.py`, `app.py`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `Pill` (e.g. with `diversify()` and `_history()`) actually correct?**
  _`Pill` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Should `feeds.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08792270531400966 - nodes in this community are weakly interconnected._