# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-10)

## Corpus Check
- 19 files · ~1,457 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: .example 1, (none) 1)

## Summary
- 81 nodes · 102 edges · 15 communities (5 shown, 10 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `df0cce15`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- config.py
- llm/__init__.py
- Agente de nutrición de conocimiento
- Desafiar y evaluar
- Investigar IA y negocios
- lesson.py
- get_llm
- Agente de nutrición de conocimiento
- nutricion
- LLMClient
- session-start.sh

## God Nodes (most connected - your core abstractions)
1. `get_llm()` - 9 edges
2. `Settings` - 7 edges
3. `GeminiClient` - 7 edges
4. `LessonState` - 6 edges
5. `transition()` - 6 edges
6. `LLMClient` - 5 edges
7. `test_cannot_skip_waiting_for_answer()` - 5 edges
8. `get_settings()` - 4 edges
9. `InvalidTransition` - 4 edges
10. `test_missing_key_is_reported()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `test_gemini_is_selected_when_key_present()` --uses--> `GeminiClient`  [INFERRED]
  tests/test_llm.py → src/nutricion/llm/gemini.py
- `test_gemini_is_selected_when_key_present()` --uses--> `Settings`  [INFERRED]
  tests/test_llm.py → src/nutricion/config.py
- `test_missing_key_is_reported()` --uses--> `Settings`  [INFERRED]
  tests/test_llm.py → src/nutricion/config.py
- `test_cannot_skip_waiting_for_answer()` --uses--> `LessonState`  [INFERRED]
  tests/test_lesson.py → src/nutricion/domain/lesson.py
- `test_failed_evaluation_returns_to_waiting()` --uses--> `LessonState`  [INFERRED]
  tests/test_lesson.py → src/nutricion/domain/lesson.py

## Import Cycles
- None detected.

## Communities (15 total, 10 thin omitted)

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.40
Nodes (4): Agente de nutrición de conocimiento, Estructura, Graphify, Puesta en marcha

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.40
Nodes (4): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.40
Nodes (4): Criterios de selección, Formato de la píldora, Investigar IA y negocios, Objetivo

### Community 5 - "lesson.py"
Cohesion: 0.30
Nodes (6): InvalidTransition, LessonState, transition(), test_cannot_skip_waiting_for_answer(), test_failed_evaluation_returns_to_waiting(), test_happy_path()

### Community 6 - "get_llm"
Cohesion: 0.33
Nodes (5): Settings, get_llm(), MissingAPIKey, test_gemini_is_selected_when_key_present(), test_missing_key_is_reported()

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 48 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMClient` connect `LLMClient` to `llm/__init__.py`, `get_llm`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Settings` (e.g. with `get_llm()` and `test_gemini_is_selected_when_key_present()`) actually correct?**
  _`Settings` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `get_llm()` connect `get_llm` to `config.py`, `llm/__init__.py`, `LLMClient`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `LessonState` (e.g. with `test_cannot_skip_waiting_for_answer()` and `test_failed_evaluation_returns_to_waiting()`) actually correct?**
  _`LessonState` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Why does `test_cannot_skip_waiting_for_answer()` connect `lesson.py` to `get_llm`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._