# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-10)

## Corpus Check
- 41 files · ~11,050 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: .example 1, (none) 1)

## Summary
- 410 nodes · 907 edges · 18 communities (12 shown, 6 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 124 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `593ed1c1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Settings
- feeds.py
- Agente de nutrición de conocimiento
- Desafiar y evaluar
- Investigar IA y negocios
- test_diagnose.py
- test_app.py
- TelegramClient
- app.py
- Store
- nutricion
- Score
- session-start.sh
- formatting.py
- web.py
- Agent

## God Nodes (most connected - your core abstractions)
1. `Store` - 42 edges
2. `Settings` - 28 edges
3. `Agent` - 23 edges
4. `TelegramClient` - 22 edges
5. `create_app()` - 22 edges
6. `Score` - 21 edges
7. `make_agent()` - 20 edges
8. `LessonState` - 16 edges
9. `Pill` - 15 edges
10. `Lesson` - 15 edges

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

## Communities (18 total, 6 thin omitted)

### Community 0 - "Settings"
Cohesion: 0.07
Nodes (16): get_settings(), Settings, build_agent(), GeminiClient, get_llm(), MissingAPIKey, annotate(), _database_status() (+8 more)

### Community 1 - "feeds.py"
Cohesion: 0.08
Nodes (23): Category, category_of_the_day(), Source, Candidate, _clean(), _entry_image(), fetch_candidates(), fetch_source() (+15 more)

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.20
Nodes (9): Agente de nutrición de conocimiento, Automatización final (Render + cron-job.org), Ejecución por GitHub Actions (modo anterior, sin servidor), Estructura, Graphify, Modo tiempo real (webhook en Render + Supabase), Puesta en marcha, Sesiones en la nube (Claude Code) (+1 more)

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.33
Nodes (5): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío, Posturas de respuesta rápida (botones)

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.33
Nodes (5): Criterios de selección, Formato de la píldora, Investigar IA y negocios, Objetivo, Rigor de las fuentes (de más a menos peso)

### Community 5 - "test_diagnose.py"
Cohesion: 0.14
Nodes (12): connection_summary(), database_url_problems(), explain_connection_error(), _sanitized(), test_common_mistakes_are_explained(), test_connection_summary_hides_password(), test_correct_session_pooler_uri_has_no_problems(), test_password_variable_fills_the_supabase_template() (+4 more)

### Community 6 - "test_app.py"
Cohesion: 0.12
Nodes (18): FakeLLM, FakeMessenger, make_agent(), news(), test_answer_is_evaluated_and_offers_next_button(), test_button_choice_gets_a_reaction_and_is_used_in_evaluation(), test_button_from_finished_lesson_is_rejected(), test_daily_pill_is_sent_as_photo_with_option_buttons() (+10 more)

### Community 7 - "TelegramClient"
Cohesion: 0.15
Nodes (4): _keyboard(), TelegramClient, TelegramError, lifespan()

### Community 9 - "Store"
Cohesion: 0.09
Nodes (16): InvalidTransition, Lesson, LessonState, transition(), _migrate(), _now(), Store, _to_lesson() (+8 more)

### Community 13 - "Score"
Cohesion: 0.14
Nodes (10): build_profile(), _clamp(), Score, _streak(), at(), test_averages_streak_and_level(), test_empty_profile(), test_scores_are_clamped() (+2 more)

### Community 15 - "formatting.py"
Cohesion: 0.08
Nodes (20): Agente de nutrición de conocimiento, graphify, create_pill(), _PillDraft, load_skill(), evaluate(), Evaluation, react_to_choice() (+12 more)

### Community 16 - "web.py"
Cohesion: 0.07
Nodes (24): DatabaseConnectionError, create_app(), cron_daily_pill(), diagnose(), diagnostics(), telegram(), __getattr__(), process() (+16 more)

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 144 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Store` connect `Store` to `Settings`, `feeds.py`, `test_diagnose.py`, `test_app.py`, `app.py`, `Score`, `formatting.py`, `web.py`, `Agent`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `Store` (e.g. with `Agent` and `Lesson`) actually correct?**
  _`Store` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Settings` be split into smaller, more focused modules?**
  _Cohesion score 0.07111756168359942 - nodes in this community are weakly interconnected._
- **Why does `TelegramClient` connect `TelegramClient` to `Settings`, `web.py`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `Settings` (e.g. with `build_agent()` and `get_llm()`) actually correct?**
  _`Settings` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Should `feeds.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08163265306122448 - nodes in this community are weakly interconnected._