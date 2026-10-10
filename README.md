# Agente de nutrición de conocimiento

Cada día, el sistema busca noticias de IA aplicada a negocios e inversión, te envía una
**píldora** por Telegram, te plantea un **desafío de juicio crítico**, espera tu respuesta,
la **evalúa** y pasa a la siguiente.

## Puesta en marcha

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env        # rellena tus claves
nutricion                   # verifica la configuración
nutricion ping              # prueba real contra Gemini
nutricion fuentes           # cuántas noticias devuelve cada fuente
nutricion tick --enviar-pildora   # procesa mensajes y envía una píldora
pytest                      # ejecuta las pruebas
```

## Estructura

```
src/nutricion/
  config.py        configuración desde .env
  domain/          modelo puro: máquina de estados de la lección
  llm/             cerebro intercambiable (hoy: Gemini, capa gratuita)
  sources/         catálogo de fuentes (prensa, finanzas, arXiv, universidades) e imágenes
  agents/          investigador (elige y redacta) y tutor (reacciona y evalúa)
  app.py           orquestador: un "tick" procesa tus mensajes y envía la píldora
  channels/        Telegram: HTML, fotos y botones (inline keyboards)
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

## Sesiones en la nube (Claude Code)

`.claude/hooks/session-start.sh` se ejecuta al abrir cada sesión: crea el entorno, instala
dependencias, genera `.env` desde `.env.example`, actualiza el grafo e instala los hooks de git
que lo regeneran tras cada commit. Las claves se configuran como variables del entorno de la
nube (no en el chat): `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

## Ejecución automática (GitHub Actions)

`.github/workflows/agente.yml` corre en GitHub, sin ningún ordenador encendido:

- **Cada día a las 12:00 UTC** envía la píldora con su desafío (o te recuerda el pendiente).
- **Cada 10 minutos** revisa tus respuestas y los botones que pulsaste, te evalúa y responde.
- Botones: elige una postura y el tutor reacciona; luego justifica por escrito para la nota.
  Tras el feedback, el botón «Siguiente píldora» (o `/siguiente`) trae una nueva.

Para cambiar la hora, edita las dos apariciones de `"0 12 * * *"` en el workflow
(formato `minuto hora * * *`, en UTC). Ejemplo: `"30 23 * * *"` = 23:30 UTC.

Las claves se guardan como *Secrets* del repositorio: `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`,
`TELEGRAM_CHAT_ID` (Settings → Secrets and variables → Actions).
