# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-10)

## Corpus Check
- 33 files · ~6,128 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .example 1)

## Summary
- 248 nodes · 487 edges · 15 communities (9 shown, 6 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `69003f47`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- feeds.py
- Agente de nutrición de conocimiento
- Desafiar y evaluar
- Investigar IA y negocios
- Store
- test_app.py
- TelegramClient
- app.py
- Agent
- nutricion
- researcher.py
- session-start.sh

## God Nodes (most connected - your core abstractions)
1. `Store` - 22 edges
2. `Agent` - 19 edges
3. `make_agent()` - 16 edges
4. `LessonState` - 15 edges
5. `Lesson` - 15 edges
6. `Pill` - 14 edges
7. `FakeMessenger` - 13 edges
8. `LLMClient` - 12 edges
9. `fetch_source()` - 11 edges
10. `TelegramClient` - 10 edges

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

## Communities (15 total, 6 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.11
Nodes (10): get_settings(), Settings, GeminiClient, get_llm(), MissingAPIKey, main(), _require(), _run_tick() (+2 more)

### Community 1 - "feeds.py"
Cohesion: 0.09
Nodes (19): Category, category_of_the_day(), Source, Candidate, _clean(), _entry_image(), fetch_candidates(), fetch_source() (+11 more)

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.29
Nodes (6): Agente de nutrición de conocimiento, Ejecución automática (GitHub Actions), Estructura, Graphify, Puesta en marcha, Sesiones en la nube (Claude Code)

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.33
Nodes (5): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío, Posturas de respuesta rápida (botones)

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.33
Nodes (5): Criterios de selección, Formato de la píldora, Investigar IA y negocios, Objetivo, Rigor de las fuentes (de más a menos peso)

### Community 5 - "Store"
Cohesion: 0.09
Nodes (13): pill_body(), pill_header(), reminder(), InvalidTransition, Lesson, LessonState, Pill, transition() (+5 more)

### Community 6 - "test_app.py"
Cohesion: 0.14
Nodes (14): FakeLLM, FakeMessenger, make_agent(), news(), test_answer_is_evaluated_and_offers_next_button(), test_button_choice_gets_a_reaction_and_is_used_in_evaluation(), test_button_from_finished_lesson_is_rejected(), test_daily_pill_is_sent_as_photo_with_option_buttons() (+6 more)

### Community 7 - "TelegramClient"
Cohesion: 0.21
Nodes (3): _keyboard(), TelegramClient, TelegramError

### Community 13 - "researcher.py"
Cohesion: 0.08
Nodes (10): Agente de nutrición de conocimiento, graphify, create_pill(), _PillDraft, load_skill(), evaluate(), Evaluation, react_to_choice() (+2 more)

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 99 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Store` connect `Store` to `main.py`, `feeds.py`, `test_app.py`, `app.py`, `Agent`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Store` (e.g. with `Agent` and `Lesson`) actually correct?**
  _`Store` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11494252873563218 - nodes in this community are weakly interconnected._
- **Why does `Agent` connect `Agent` to `main.py`, `Store`, `test_app.py`, `TelegramClient`, `app.py`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Agent` (e.g. with `TelegramError` and `Lesson`) actually correct?**
  _`Agent` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `feeds.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09080841638981174 - nodes in this community are weakly interconnected._