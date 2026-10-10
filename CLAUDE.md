# Agente de nutrición de conocimiento

Sistema en Python que envía píldoras diarias de IA y negocios por Telegram, plantea un desafío
de juicio crítico, espera la respuesta del usuario y la evalúa.

- Código en `src/nutricion/`; el dominio (`domain/`) no depende de APIs externas.
- Instrucciones de los agentes en tiempo de ejecución: `skills/*/SKILL.md`.
- Comprobaciones antes de commitear: `ruff check . && ruff format --check . && pytest`.
- Idioma de la documentación y los mensajes al usuario: español.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
