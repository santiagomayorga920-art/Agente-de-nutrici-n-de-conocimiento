# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-10)

## Corpus Check
- 19 files · ~1,547 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .example 1)

## Summary
- 82 nodes · 104 edges · 14 communities (6 shown, 8 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `df0cce15`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- llm/__init__.py
- gemini.py
- Agente de nutrición de conocimiento
- Desafiar y evaluar
- Investigar IA y negocios
- lesson.py
- nutricion
- LLMClient
- session-start.sh

## God Nodes (most connected - your core abstractions)
1. `get_llm()` - 9 edges
2. `Settings` - 7 edges
3. `GeminiClient` - 7 edges
4. `LessonState` - 6 edges
5. `transition()` - 6 edges
6. `LLMClient` - 6 edges
7. `test_cannot_skip_waiting_for_answer()` - 5 edges
8. `Agente de nutrición de conocimiento` - 5 edges
9. `get_settings()` - 4 edges
10. `InvalidTransition` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Agente de nutrición de conocimiento` --references--> `LLMClient`  [INFERRED]
  CLAUDE.md → src/nutricion/llm/__init__.py
- `test_gemini_is_selected_when_key_present()` --uses--> `GeminiClient`  [INFERRED]
  tests/test_llm.py → src/nutricion/llm/gemini.py
- `test_gemini_is_selected_when_key_present()` --uses--> `Settings`  [INFERRED]
  tests/test_llm.py → src/nutricion/config.py
- `test_missing_key_is_reported()` --uses--> `Settings`  [INFERRED]
  tests/test_llm.py → src/nutricion/config.py
- `test_cannot_skip_waiting_for_answer()` --uses--> `LessonState`  [INFERRED]
  tests/test_lesson.py → src/nutricion/domain/lesson.py

## Import Cycles
- None detected.

## Communities (14 total, 8 thin omitted)

### Community 0 - "llm/__init__.py"
Cohesion: 0.19
Nodes (7): get_settings(), Settings, get_llm(), MissingAPIKey, main(), test_gemini_is_selected_when_key_present(), test_missing_key_is_reported()

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.33
Nodes (5): Agente de nutrición de conocimiento, Estructura, Graphify, Puesta en marcha, Sesiones en la nube (Claude Code)

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.40
Nodes (4): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.40
Nodes (4): Criterios de selección, Formato de la píldora, Investigar IA y negocios, Objetivo

### Community 5 - "lesson.py"
Cohesion: 0.28
Nodes (6): InvalidTransition, LessonState, transition(), test_cannot_skip_waiting_for_answer(), test_failed_evaluation_returns_to_waiting(), test_happy_path()

### Community 13 - "LLMClient"
Cohesion: 0.20
Nodes (3): Agente de nutrición de conocimiento, graphify, LLMClient

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 49 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMClient` connect `LLMClient` to `llm/__init__.py`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Settings` (e.g. with `get_llm()` and `test_gemini_is_selected_when_key_present()`) actually correct?**
  _`Settings` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `get_llm()` connect `llm/__init__.py` to `gemini.py`, `LLMClient`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `LessonState` (e.g. with `test_cannot_skip_waiting_for_answer()` and `test_failed_evaluation_returns_to_waiting()`) actually correct?**
  _`LessonState` has 3 INFERRED edges - model-reasoned connections that need verification._