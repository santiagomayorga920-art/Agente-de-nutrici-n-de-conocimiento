# Graph Report - Agente-de-nutrici-n-de-conocimiento  (2026-10-10)

## Corpus Check
- 15 files · ~1,039 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: .example 1, (none) 1)

## Summary
- 51 nodes · 53 edges · 13 communities (5 shown, 8 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- config.py
- lesson.py
- Agente de nutrición de conocimiento
- Desafiar y evaluar
- Investigar IA y negocios
- LessonState
- test_lesson.py
- CLAUDE.md
- nutricion

## God Nodes (most connected - your core abstractions)
1. `LessonState` - 6 edges
2. `transition()` - 6 edges
3. `test_cannot_skip_waiting_for_answer()` - 5 edges
4. `get_settings()` - 4 edges
5. `InvalidTransition` - 4 edges
6. `Agente de nutrición de conocimiento` - 4 edges
7. `Desafiar y evaluar` - 4 edges
8. `Investigar IA y negocios` - 4 edges
9. `Settings` - 3 edges
10. `test_happy_path()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `test_cannot_skip_waiting_for_answer()` --uses--> `LessonState`  [INFERRED]
  tests/test_lesson.py → src/nutricion/domain/lesson.py
- `test_cannot_skip_waiting_for_answer()` --uses--> `InvalidTransition`  [INFERRED]
  tests/test_lesson.py → src/nutricion/domain/lesson.py
- `test_failed_evaluation_returns_to_waiting()` --uses--> `LessonState`  [INFERRED]
  tests/test_lesson.py → src/nutricion/domain/lesson.py
- `test_happy_path()` --uses--> `LessonState`  [INFERRED]
  tests/test_lesson.py → src/nutricion/domain/lesson.py
- `test_cannot_skip_waiting_for_answer()` --calls--> `transition()`  [EXTRACTED]
  tests/test_lesson.py → src/nutricion/domain/lesson.py

## Import Cycles
- None detected.

## Communities (13 total, 8 thin omitted)

### Community 0 - "config.py"
Cohesion: 0.21
Nodes (3): get_settings(), Settings, main()

### Community 2 - "Agente de nutrición de conocimiento"
Cohesion: 0.40
Nodes (4): Agente de nutrición de conocimiento, Estructura, Graphify, Puesta en marcha

### Community 3 - "Desafiar y evaluar"
Cohesion: 0.40
Nodes (4): Desafiar y evaluar, Evaluar la respuesta, Feedback, Formular el desafío

### Community 4 - "Investigar IA y negocios"
Cohesion: 0.40
Nodes (4): Criterios de selección, Formato de la píldora, Investigar IA y negocios, Objetivo

### Community 5 - "LessonState"
Cohesion: 0.60
Nodes (4): LessonState, transition(), test_failed_evaluation_returns_to_waiting(), test_happy_path()

## Knowledge Gaps
- **1 isolated node(s):** `nutricion`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 33 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LessonState` connect `LessonState` to `lesson.py`, `test_lesson.py`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `LessonState` (e.g. with `test_cannot_skip_waiting_for_answer()` and `test_failed_evaluation_returns_to_waiting()`) actually correct?**
  _`LessonState` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `nutricion` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `InvalidTransition` connect `lesson.py` to `LessonState`, `test_lesson.py`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `test_cannot_skip_waiting_for_answer()` (e.g. with `InvalidTransition` and `LessonState`) actually correct?**
  _`test_cannot_skip_waiting_for_answer()` has 2 INFERRED edges - model-reasoned connections that need verification._