# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-11)

## Corpus Check
- 46 files · ~14,762 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .ttf 2, .example 1)

## Summary
- 516 nodes · 1172 edges · 20 communities (14 shown, 6 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 144 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `64b787ae`
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
- app.py
- web.py
- Agent
- test_diagnose.py
- gemini.py

## God Nodes (most connected - your core abstractions)
1. `Store` - 44 edges
2. `Settings` - 30 edges
3. `Agent` - 28 edges
4. `Pill` - 26 edges
5. `make_agent()` - 26 edges
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

## Communities (20 total, 6 thin omitted)

### Community 0 - "Settings"
Cohesion: 0.10
Nodes (15): get_settings(), Settings, build_agent(), get_llm(), MissingAPIKey, annotate(), _database_status(), main() (+7 more)

### Community 1 - "feeds.py"
Cohesion: 0.09
Nodes (23): Category, category_of_the_day(), Source, Candidate, _clean(), _entry_image(), fetch_candidates(), fetch_source() (+15 more)

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.18
Nodes (10): Agente de nutrición de conocimiento, Automatización final (Render + cron-job.org), Ejecución por GitHub Actions (modo anterior, sin servidor), Estructura, Graphify, Modo tiempo real (webhook en Render + Supabase), Multimedia de la píldora, Puesta en marcha (+2 more)

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.33
Nodes (5): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío, Posturas de respuesta rápida (botones)

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.33
Nodes (5): Criterios de selección, Formato de la píldora, Investigar IA y negocios, Objetivo, Rigor de las fuentes (de más a menos peso)

### Community 5 - "Store"
Cohesion: 0.11
Nodes (10): Lesson, _migrate(), _now(), Store, diagnostics(), pill(), store(), test_import_from_sqlite_keeps_scores_and_skips_duplicates() (+2 more)

### Community 6 - "test_app.py"
Cohesion: 0.11
Nodes (30): InvalidTransition, LessonState, transition(), FakeLLM, make_agent(), news(), test_answer_is_evaluated_and_offers_next_button(), test_button_choice_gets_a_reaction_and_is_used_in_evaluation() (+22 more)

### Community 7 - "TelegramClient"
Cohesion: 0.09
Nodes (5): _keyboard(), TelegramClient, TelegramError, lifespan(), FakeMessenger

### Community 8 - "card.py"
Cohesion: 0.14
Nodes (17): _background(), build_card(), _ellipsize(), fetch_background(), _fit(), _font(), _gradient(), render_card() (+9 more)

### Community 13 - "Score"
Cohesion: 0.09
Nodes (19): _bar(), _days(), feedback(), pill_body(), pill_header(), profile_card(), progress_line(), reminder() (+11 more)

### Community 15 - "app.py"
Cohesion: 0.05
Nodes (19): Agente de nutrición de conocimiento, graphify, create_pill(), _PillDraft, _shorten(), load_skill(), evaluate(), Evaluation (+11 more)

### Community 16 - "web.py"
Cohesion: 0.06
Nodes (33): DatabaseConnectionError, create_app(), authorized(), cron_daily_pill(), diagnose(), telegram(), _describe(), __getattr__() (+25 more)

### Community 18 - "test_diagnose.py"
Cohesion: 0.16
Nodes (13): connection_summary(), database_url_problems(), explain_connection_error(), _sanitized(), test_common_mistakes_are_explained(), test_connection_summary_hides_password(), test_correct_session_pooler_uri_has_no_problems(), test_password_variable_fills_the_supabase_template() (+5 more)

### Community 19 - "gemini.py"
Cohesion: 0.10
Nodes (10): as_wav(), GeminiClient, FakeSpeaker, pill(), test_build_voice_sends_only_the_script_to_the_model(), test_raw_pcm_from_gemini_is_wrapped_as_wav(), test_script_reads_the_pill_without_urls(), test_script_without_category() (+2 more)

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 172 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Store` connect `Store` to `Settings`, `feeds.py`, `test_app.py`, `Score`, `app.py`, `web.py`, `Agent`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `Store` (e.g. with `Agent` and `Lesson`) actually correct?**
  _`Store` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Settings` be split into smaller, more focused modules?**
  _Cohesion score 0.09743589743589744 - nodes in this community are weakly interconnected._
- **Why does `Pill` connect `app.py` to `Store`, `card.py`, `Score`, `Agent`, `gemini.py`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Settings` (e.g. with `build_agent()` and `get_llm()`) actually correct?**
  _`Settings` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `feeds.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._