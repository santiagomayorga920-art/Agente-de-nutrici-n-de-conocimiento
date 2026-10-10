# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-10)

## Corpus Check
- 27 files · ~3,760 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .example 1)

## Summary
- 174 nodes · 312 edges · 14 communities (8 shown, 6 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cbca93b5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- llm/__init__.py
- Agente de nutrición de conocimiento
- Desafiar y evaluar
- Investigar IA y negocios
- Store
- test_app.py
- app.py
- nutricion
- researcher.py
- session-start.sh

## God Nodes (most connected - your core abstractions)
1. `Store` - 18 edges
2. `Agent` - 14 edges
3. `LessonState` - 14 edges
4. `make_agent()` - 13 edges
5. `Lesson` - 12 edges
6. `Pill` - 11 edges
7. `LLMClient` - 11 edges
8. `Settings` - 10 edges
9. `get_llm()` - 10 edges
10. `transition()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Agente de nutrición de conocimiento` --references--> `LLMClient`  [INFERRED]
  CLAUDE.md → src/nutricion/llm/__init__.py
- `news()` --uses--> `Candidate`  [INFERRED]
  tests/test_app.py → src/nutricion/agents/researcher.py
- `FakeLLM` --uses--> `Evaluation`  [INFERRED]
  tests/test_app.py → src/nutricion/agents/tutor.py
- `make_agent()` --uses--> `Agent`  [INFERRED]
  tests/test_app.py → src/nutricion/app.py
- `test_daily_pill_is_sent_and_waits_for_answer()` --uses--> `LessonState`  [INFERRED]
  tests/test_app.py → src/nutricion/domain/lesson.py

## Import Cycles
- None detected.

## Communities (14 total, 6 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.12
Nodes (9): TelegramClient, get_settings(), Settings, get_llm(), main(), _require(), _run_tick(), test_gemini_is_selected_when_key_present() (+1 more)

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.29
Nodes (6): Agente de nutrición de conocimiento, Ejecución automática (GitHub Actions), Estructura, Graphify, Puesta en marcha, Sesiones en la nube (Claude Code)

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.40
Nodes (4): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.40
Nodes (4): Criterios de selección, Formato de la píldora, Investigar IA y negocios, Objetivo

### Community 5 - "Store"
Cohesion: 0.12
Nodes (10): InvalidTransition, Lesson, LessonState, Pill, transition(), Store, _to_lesson(), test_cannot_skip_waiting_for_answer() (+2 more)

### Community 6 - "test_app.py"
Cohesion: 0.18
Nodes (11): FakeLLM, FakeMessenger, make_agent(), news(), test_answer_is_evaluated_and_lesson_completed(), test_daily_pill_is_sent_and_waits_for_answer(), test_daily_run_reminds_pending_challenge_instead_of_new_pill(), test_failed_evaluation_is_retried_next_tick() (+3 more)

### Community 8 - "app.py"
Cohesion: 0.18
Nodes (3): Agent, _format_pill(), Messenger

### Community 13 - "researcher.py"
Cohesion: 0.09
Nodes (12): Agente de nutrición de conocimiento, graphify, Candidate, create_pill(), fetch_candidates(), NoNewsFound, _PillDraft, load_skill() (+4 more)

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 80 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Store` connect `Store` to `app.py`, `main.py`, `test_app.py`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Store` (e.g. with `Agent` and `Lesson`) actually correct?**
  _`Store` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11576354679802955 - nodes in this community are weakly interconnected._
- **Why does `LLMClient` connect `researcher.py` to `app.py`, `llm/__init__.py`, `main.py`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Agent` (e.g. with `Lesson` and `LessonState`) actually correct?**
  _`Agent` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `Store` be split into smaller, more focused modules?**
  _Cohesion score 0.12473118279569892 - nodes in this community are weakly interconnected._