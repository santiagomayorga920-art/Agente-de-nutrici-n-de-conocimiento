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
nutricion stats             # tu perfil (nivel, racha, promedios)
nutricion tick --enviar-pildora   # procesa mensajes y envía una píldora
pytest                      # ejecuta las pruebas
```

## Estructura

```
src/nutricion/
  config.py        configuración desde .env
  domain/          modelo puro: estados de la lección y gamificación (nivel, racha)
  llm/             cerebro intercambiable (hoy: Gemini, capa gratuita)
  sources/         catálogo de fuentes (prensa, finanzas, arXiv, universidades) e imágenes
  agents/          investigador (elige y redacta) y tutor (reacciona y evalúa)
  app.py           orquestador: un "tick" procesa tus mensajes y envía la píldora
  channels/        Telegram: HTML, fotos y botones (inline keyboards)
  memory/          persistencia: SQLite (local/caché) o Postgres (Supabase)
  web.py           servidor del webhook de Telegram (Render)
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
dependencias, genera `.env` desde `.env.example` y actualiza el grafo. Las claves se configuran como variables del entorno de la
nube (no en el chat): `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

## Automatización final (Render + cron-job.org)

- **Mensajes y botones:** llegan al instante por webhook al servidor de Render.
- **Píldora diaria:** cron-job.org llama a `https://<servidor>/cron/pildora?clave=<CRON_SECRET>`
  a la hora elegida. Se envía como mucho una vez al día aunque la llamada se repita
  (`&forzar=1` envía otra igualmente).
- **Mantener despierto:** cron-job.org llama a `https://<servidor>/` cada 10 minutos.
- GitHub Actions queda como respaldo manual (Run workflow).

## Ejecución por GitHub Actions (modo anterior, sin servidor)

`.github/workflows/agente.yml` corre en GitHub, sin ningún ordenador encendido:

- **Cada día a las 12:00 UTC** envía la píldora con su desafío (o te recuerda el pendiente).
- **Cada 10 minutos** revisa tus respuestas y los botones que pulsaste, te evalúa y responde.
- Botones: elige una postura y el tutor reacciona; luego justifica por escrito para la nota.
  Tras el feedback, el botón «Siguiente píldora» (o `/siguiente`) trae una nueva.

Para cambiar la hora, edita las dos apariciones de `"0 12 * * *"` en el workflow
(formato `minuto hora * * *`, en UTC). Ejemplo: `"30 23 * * *"` = 23:30 UTC.

Las claves se guardan como *Secrets* del repositorio: `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`,
`TELEGRAM_CHAT_ID` (Settings → Secrets and variables → Actions).

## Modo tiempo real (webhook en Render + Supabase)

Sin servidor, el bot responde en la siguiente revisión (cada ~10 min). Con el webhook responde al
instante. Todo es gratuito:

| Pieza | Servicio | Para qué |
|---|---|---|
| Servidor del webhook | Render (plan free) | Recibe mensajes y botones al instante |
| Base de datos | Supabase (Postgres free) | Progreso compartido entre Render y Actions |
| Píldora diaria | GitHub Actions | Tarea programada a la hora elegida |

Cuando el webhook está activo, el workflow cada 10 min lo detecta y no sondea Telegram.
El primer arranque copia el historial de la caché de Actions a Supabase (`nutricion migrar`).

Render duerme el servicio tras 15 min sin uso: el primer mensaje tras una pausa tarda ~1 min
en despertarlo; después todo es inmediato.

### Si algo falla

- **Telegram:** escribe `/reportar <qué pasó>` o pulsa «🛠 Reportar problema». Se guarda con el
  estado del bot y los últimos errores; aparece en `/diagnostico` (`eventos_recientes`).

- **GitHub Actions:** si `DATABASE_URL` está mal, el resumen de la ejecución muestra un aviso con
  el motivo en español y el bot sigue funcionando con SQLite.
- **Render:** abre `https://<tu-servicio>.onrender.com/diagnostico?clave=<CRON_SECRET>` para ver
  qué variables faltan y si la base de datos conecta (protegido; nunca muestra claves).
