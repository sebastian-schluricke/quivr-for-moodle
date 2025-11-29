# Quivr for Moodle - RAG Backend für Schulen

Ein Fork von [QuivrHQ/quivr](https://github.com/QuivrHQ/quivr), optimiert für die Integration mit Moodle-Lernplattformen. Ermöglicht Schulen, KI-gestützte Wissensdatenbanken (Brains) zu erstellen und diese in Moodle-Kursen bereitzustellen.

## Übersicht

Quivr ist eine RAG-Plattform (Retrieval-Augmented Generation), die es ermöglicht, Dokumente hochzuladen und einen KI-Chatbot zu erstellen, der Fragen basierend auf diesen Dokumenten beantwortet. Dieser Fork erweitert Quivr um spezielle Features für den Schulbetrieb:

- **Scoped Token System**: Sichere, zeitlich begrenzte Tokens für Moodle-Integration
- **Moodle-Sync**: Synchronisation von Moodle-Kursmaterialien als Knowledge Base
- **Vereinfachte API**: Optimierte Endpunkte für das Moodle-Plugin
- **Konfigurierbare Prompts**: Anpassbare Systemanweisungen für pädagogische Kontexte

**Zusammenspiel mit Moodle:**
```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Moodle Plugin  │◄───────►│  Quivr Backend  │◄───────►│  LLM Provider   │
│  (Frontend)     │  Token  │  (Dieses Repo)  │  API    │  (OpenAI etc.)  │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

## Features

### Original Quivr Features
- **Dokumentenverarbeitung**: PDF, Word, Excel, PowerPoint, Markdown, Text, Audio, Video
- **RAG-Pipeline**: Retrieval-Augmented Generation mit Vektordatenbank
- **Multi-LLM Support**: OpenAI, Anthropic, Mistral, Groq, Ollama (lokal)
- **Brains**: Getrennte Wissensdatenbanken für verschiedene Themenbereiche
- **Streaming Responses**: Echtzeit-Antworten während der Generierung

### Fork-Erweiterungen für Moodle
- **`/chat/token` Endpoint**: Erstellt brain-spezifische, zeitlich begrenzte JWT-Tokens
- **Moodle OAuth Sync**: Automatische Synchronisation von Kursmaterialien
- **Vereinfachte Benutzerführung**: Optimiert für Lehrkräfte ohne technisches Vorwissen
- **Deutsche Lokalisierung**: Prompts und UI-Texte auf Deutsch
- **AsciiMath Support**: Mathematische Formeln in Antworten

## Voraussetzungen

- **Docker & Docker Compose**
- **Supabase CLI** ([Installation](https://supabase.com/docs/guides/cli/getting-started))
- **LLM API Key** (OpenAI, Anthropic, oder lokales Ollama)
- **8 GB RAM** (minimum für lokale Entwicklung)
- **Ubuntu 20.04+** oder **Windows mit WSL2**

## Schnellstart

### 1. Repository klonen

```bash
git clone https://github.com/sebastian-schluricke/quivr-for-moodle.git
cd quivr-for-moodle
git checkout develop
```

### 2. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
```

Bearbeite `.env` und setze mindestens:

```bash
# LLM Provider (mindestens einer erforderlich)
OPENAI_API_KEY=sk-...

# Oder für lokales Ollama:
# OLLAMA_API_BASE_URL=http://host.docker.internal:11434

# JWT Secret (wichtig für Produktivbetrieb!)
JWT_SECRET_KEY=ein-sehr-langes-zufaelliges-geheimnis-mindestens-32-zeichen
```

### 3. Supabase starten

```bash
cd backend
supabase start
```

Notiere die Ausgabe mit den Supabase-URLs und Keys.

### 4. Anwendung starten

**Mit Docker (empfohlen für Produktion):**
```bash
docker compose pull
docker compose up -d
```

**Für Entwicklung (ohne Docker):**
```bash
cd backend/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
python -m uvicorn quivr_api.main:app --host 0.0.0.0 --port 5050 --reload
```

### 5. Zugriff

- **API**: http://localhost:5050
- **API Docs (Swagger)**: http://localhost:5050/docs
- **Supabase Studio**: http://localhost:54323
- **Frontend** (optional): http://localhost:3000

### 6. Ersten Benutzer anlegen

```bash
# Im Supabase Studio (http://localhost:54323)
# → Authentication → Users → Add user
# Email: admin@ihre-schule.de
# Password: (sicheres Passwort)
```

Oder per SQL in Supabase Studio → SQL Editor:
```sql
INSERT INTO auth.users (email, encrypted_password, email_confirmed_at, role)
VALUES ('admin@ihre-schule.de', crypt('IhrPasswort', gen_salt('bf')), now(), 'authenticated');
```

## Konfiguration

### Wichtige Umgebungsvariablen

| Variable | Beschreibung | Beispiel |
|----------|--------------|----------|
| `OPENAI_API_KEY` | OpenAI API Key | `sk-...` |
| `JWT_SECRET_KEY` | Secret für JWT Token | Min. 32 Zeichen |
| `SUPABASE_URL` | Supabase URL | `http://localhost:54321` |
| `SUPABASE_SERVICE_KEY` | Supabase Service Key | Von `supabase start` |
| `BACKEND_URL` | Öffentliche Backend URL | `https://quivr.ihre-schule.de` |
| `AUTHENTICATE` | Authentifizierung aktiv | `true` |

### LLM-Modell konfigurieren

Bearbeite `backend/api/config/chat_llm_config.yaml`:

```yaml
model: gpt-4o-mini          # oder gpt-4o, claude-3-sonnet, etc.
max_tokens: 2000
temperature: 0.7
```

### Prompts anpassen

Bearbeite `backend/core/quivr_core/prompts.py` für schulspezifische Anweisungen:

```python
SYSTEM_PROMPT = """Du bist ein hilfreicher Lernassistent für Schüler.
Antworte immer auf Deutsch und in einer für Schüler verständlichen Sprache.
Verwende Markdown für Formatierung und LaTeX für mathematische Formeln."""
```

## API-Endpunkte für Moodle

### POST /chat/token
Erstellt einen zeitlich begrenzten, brain-spezifischen Token.

**Request:**
```bash
curl -X POST https://quivr.ihre-schule.de/chat/token \
  -H "Authorization: Bearer MASTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"brain_id": "uuid-des-brains", "ttl_minutes": 10}'
```

**Response:**
```json
{
  "token": "eyJ...",
  "expires_at": "2024-01-15T10:30:00Z"
}
```

### GET /brains/
Listet alle verfügbaren Brains.

### POST /chat
Erstellt eine neue Chat-Session.

### POST /chat/{chat_id}/question/stream
Sendet eine Frage und erhält Streaming-Antwort.

## Deployment für Produktion

### Mit Docker Compose

```bash
# .env für Produktion anpassen
vim .env

# SSL/TLS mit Traefik oder nginx-proxy empfohlen
docker compose -f docker-compose.yml up -d
```

### Empfohlene Infrastruktur

```
┌─────────────────┐
│   Nginx/Traefik │ ← SSL Termination
│   (Reverse Proxy)│
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌───▼───┐
│ Quivr │ │Quivr  │
│Backend│ │Worker │
└───┬───┘ └───┬───┘
    │         │
┌───▼─────────▼───┐
│    Supabase     │
│  (PostgreSQL +  │
│   Vector Store) │
└─────────────────┘
```

### Sicherheitshinweise

1. **JWT_SECRET_KEY**: Verwende ein langes, zufälliges Secret (mindestens 32 Zeichen)
2. **HTTPS**: Immer SSL/TLS in Produktion verwenden
3. **Firewall**: Nur Port 443 (HTTPS) nach außen öffnen
4. **Supabase**: Nicht direkt erreichbar machen
5. **API Keys**: Niemals in Git committen

## Entwicklung

### Projektstruktur

```
quivr-for-moodle/
├── backend/
│   ├── api/                    # FastAPI Backend
│   │   └── quivr_api/
│   │       ├── modules/
│   │       │   ├── brain/      # Brain Management
│   │       │   ├── chat/       # Chat Sessions
│   │       │   ├── chat_token/ # Moodle Token System (Fork)
│   │       │   ├── knowledge/  # Document Management
│   │       │   └── sync/       # Moodle Sync (Fork)
│   │       └── main.py
│   ├── core/                   # RAG Core Library
│   │   └── quivr_core/
│   │       ├── prompts.py      # System Prompts
│   │       └── quivr_rag.py    # RAG Pipeline
│   └── worker/                 # Celery Worker
├── frontend/                   # Next.js Frontend (optional)
├── supabase/                   # Database Migrations
├── docker-compose.yml
└── .env.example
```

### Lokale Entwicklung ohne Docker

```bash
# Backend
cd backend/api
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
uvicorn quivr_api.main:app --reload --port 5050

# Worker (separates Terminal)
cd backend/worker
celery -A quivr_worker worker -l info
```

### Tests ausführen

```bash
cd backend
pytest api/tests/ -v
pytest core/tests/ -v
```

## Fehlerbehebung

### Supabase startet nicht
```bash
supabase stop
supabase start
```

### Docker Speicherprobleme
```bash
docker system prune -a
# Mehr RAM für Docker in Docker Desktop zuweisen
```

### API Key funktioniert nicht
- Prüfe ob der Key in Supabase → api_keys Tabelle existiert
- Prüfe ob der User dem Brain zugeordnet ist

### Chat-Token abgelaufen
- Moodle-Plugin holt automatisch neuen Token
- TTL in `get_token.php` anpassen (Standard: 10 Minuten)

## Updates vom Original-Quivr

```bash
# Upstream hinzufügen (einmalig)
git remote add upstream https://github.com/QuivrHQ/quivr.git

# Updates holen
git fetch upstream
git checkout develop
git merge upstream/main  # Achtung: Manuelle Konfliktlösung nötig
```

## Lizenz

Apache License 2.0 - siehe [LICENSE](LICENSE)

## Mitwirken

1. Fork erstellen
2. Feature-Branch: `git checkout -b feature/meine-funktion`
3. Änderungen committen
4. Push: `git push origin feature/meine-funktion`
5. Pull Request erstellen

## Verwandte Projekte

- [quivr-moodle-plugin](https://github.com/sebastian-schluricke/quivr-moodle-plugin) - Moodle Activity Plugin
- [QuivrHQ/quivr](https://github.com/QuivrHQ/quivr) - Original Quivr Projekt

## Support

- [GitHub Issues](https://github.com/sebastian-schluricke/quivr-for-moodle/issues)
