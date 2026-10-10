# Agente de nutrición de conocimiento

Cada día, el sistema busca noticias de IA aplicada a negocios e inversión, te envía una
**píldora** por Telegram, te plantea un **desafío de juicio crítico**, espera tu respuesta,
la **evalúa** y pasa a la siguiente.

## Puesta en marcha

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,telegram]"
cp .env.example .env        # rellena tus claves
nutricion                   # verifica la configuración
pytest                      # ejecuta las pruebas
```

## Estructura

```
src/nutricion/
  config.py        configuración desde .env
  domain/          modelo puro: máquina de estados de la lección
  agents/          investigador y tutor (llamadas a Claude)
  channels/        Telegram (y luego WhatsApp)
  memory/          persistencia SQLite del progreso
skills/            instrucciones .md que usan los agentes en tiempo de ejecución
.claude/           configuración de Claude Code para desarrollar (hooks de Graphify)
graphify-out/      grafo de conocimiento del código (graph.json, GRAPH_REPORT.md)
```

## Graphify

El grafo del código se regenera sin LLM:

```bash
graphify update .
```

Tras cada `git pull`, ejecuta `graphify update .` para mantenerlo sincronizado.
