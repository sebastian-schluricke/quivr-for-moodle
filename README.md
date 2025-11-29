# Quivr for Moodle - RAG Backend für Schulen

Ein Fork von [QuivrHQ/quivr](https://github.com/QuivrHQ/quivr), optimiert für die Integration mit Moodle-Lernplattformen. Ermöglicht Schulen, KI-gestützte Wissensdatenbanken (Brains) zu erstellen und diese in Moodle-Kursen bereitzustellen.

## Übersicht

Quivr ist eine RAG-Plattform (Retrieval-Augmented Generation), die es ermöglicht, Dokumente hochzuladen und einen KI-Chatbot zu erstellen, der Fragen basierend auf diesen Dokumenten beantwortet. Dieser Fork erweitert Quivr um spezielle Features für den Schulbetrieb:

- **Scoped Token System**: Sichere, zeitlich begrenzte Tokens für Moodle-Integration
- **Moodle-Sync**: Synchronisation von Moodle-Kursmaterialien als Knowledge Base
- **Vereinfachte API**: Optimierte Endpunkte für das Moodle-Plugin

**Zusammenspiel mit Moodle:**
```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Moodle Plugin  │◄───────►│  Quivr Backend  │◄───────►│  LLM Provider   │
│  (Frontend)     │  Token  │  (Dieses Repo)  │  API    │  (OpenAI)       │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

## Architektur

Das System besteht aus drei Docker Compose Stacks:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Server                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                                               │
│  │   Traefik    │ ← SSL/HTTPS Termination (Let's Encrypt)       │
│  │  (Port 443)  │                                               │
│  └──────┬───────┘                                               │
│         │                                                       │
│    ┌────┴────────────────────┬───────────────────────┐          │
│    │                         │                       │          │
│    ▼                         ▼                       ▼          │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │  Supabase   │    │  Quivr Backend  │    │  Quivr Worker   │  │
│  │  (Kong API) │    │  (FastAPI)      │    │  (Celery)       │  │
│  │supabase.esfl│    │   quivr.esfl    │    │                 │  │
│  └──────┬──────┘    └────────┬────────┘    └─────────┬───────┘  │
│         │                    │                       │          │
│         └────────────────────┼───────────────────────┘          │
│                              │                                  │
│                    ┌─────────▼─────────┐                        │
│                    │   PostgreSQL      │                        │
│                    │   (Supabase DB)   │                        │
│                    │   + pgvector      │                        │
│                    └───────────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Unterstützte LLM-Modelle

Das System unterstützt folgende OpenAI-Modelle:

| Modell | Beschreibung | Empfohlen |
|--------|--------------|-----------|
| `gpt-4o-mini` | Schnell, kostengünstig | ✓ Standard |
| `gpt-4o` | Leistungsstark | Für komplexe Aufgaben |
| `gpt-4-turbo` | GPT-4 mit großem Context | - |
| `gpt-3.5-turbo` | Schnell, sehr günstig | Budget-Option |

## Voraussetzungen

- **Linux Server** (Ubuntu 22.04 empfohlen)
- **Docker & Docker Compose** v2.x
- **Domain mit DNS** (z.B. `quivr.ihre-schule.de`, `supabase.ihre-schule.de`)
- **OpenAI API Key**
- **Mindestens 8 GB RAM**, 50 GB Speicher

## Installation

Die Installation erfolgt in drei Schritten:

### 1. Traefik (Reverse Proxy mit SSL)

```bash
mkdir -p ~/traefik && cd ~/traefik

# Docker Network erstellen
docker network create supabase_network_secondbrain

# docker-compose.yml erstellen
cat > docker-compose.yml << 'EOF'
services:
  traefik:
    image: "traefik:v2.11"
    container_name: "traefik"
    restart: unless-stopped
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=admin@ihre-schule.de"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"
    networks:
      - supabase_network_secondbrain

networks:
  supabase_network_secondbrain:
    external: true
EOF

docker compose up -d
```

### 2. Supabase (Datenbank & Auth)

```bash
mkdir -p ~/supabase && cd ~/supabase
git clone https://github.com/supabase/supabase.git --depth 1
cd supabase/docker
cp .env.example .env
```

**.env anpassen:**
```bash
# Sichere Passwörter generieren
POSTGRES_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 48)

# Keys generieren (siehe Supabase Docs)
# https://supabase.com/docs/guides/self-hosting/docker

# Domain anpassen
SUPABASE_PUBLIC_URL=https://supabase.ihre-schule.de
API_EXTERNAL_URL=https://supabase.ihre-schule.de
```

**docker-compose.yml anpassen:**
- Kong Service: Traefik Labels hinzufügen
- Network `supabase_network_secondbrain` hinzufügen
- Ports entfernen (Traefik übernimmt)

```bash
docker compose up -d
```

### 3. Quivr Backend

```bash
mkdir -p ~/quivr && cd ~/quivr
git clone https://github.com/sebastian-schluricke/quivr-for-moodle.git .
git checkout develop
cp .env.example .env
```

**.env anpassen:**
```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Supabase Verbindung (aus Supabase .env)
SUPABASE_URL=https://supabase.ihre-schule.de
SUPABASE_SERVICE_KEY=<SERVICE_ROLE_KEY>
JWT_SECRET_KEY=<JWT_SECRET>
PG_DATABASE_URL=postgresql://postgres:<POSTGRES_PASSWORD>@supabase-db:5432/postgres

# Backend URL
BACKEND_URL=https://quivr.ihre-schule.de
```

**Datenbank-Migrationen ausführen:**
```bash
# In Supabase-Container oder via psql
docker exec -it supabase-db psql -U postgres -d postgres

# SQL-Migrationen aus backend/supabase/migrations/ ausführen
```

**Quivr starten:**
```bash
docker compose up -d
```

## Umgebungsvariablen

### Erforderliche Variablen (.bashrc oder .env)

```bash
# Supabase Credentials
export POSTGRES_PASSWORD="<sicheres-passwort>"
export JWT_SECRET="<jwt-secret-min-32-zeichen>"
export ANON_KEY="<supabase-anon-key>"
export SERVICE_ROLE_KEY="<supabase-service-role-key>"
export SUPABASE_URL="https://supabase.ihre-schule.de"

# Datenbank URLs
export PG_DATABASE_URL="postgresql://postgres:${POSTGRES_PASSWORD}@supabase-db:5432/postgres"
export PG_DATABASE_ASYNC_URL="postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@supabase-db:5432/postgres"

# JWT für Quivr
export JWT_SECRET_KEY="${JWT_SECRET}"
export SUPABASE_SERVICE_KEY="${SERVICE_ROLE_KEY}"
export NEXT_PUBLIC_SUPABASE_ANON_KEY="${ANON_KEY}"
```

### Supabase Keys generieren

Die Anon und Service Role Keys müssen aus dem JWT Secret generiert werden:

```bash
# Online Generator: https://supabase.com/docs/guides/self-hosting/docker#generate-api-keys
# Oder manuell mit jwt.io
```

## API-Endpunkte für Moodle

### POST /chat/token
Erstellt einen zeitlich begrenzten, brain-spezifischen Token.

```bash
curl -X POST https://quivr.ihre-schule.de/chat/token \
  -H "Authorization: Bearer MASTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"brain_id": "uuid-des-brains", "ttl_minutes": 10}'
```

### GET /brains/
Listet alle verfügbaren Brains.

### POST /chat
Erstellt eine neue Chat-Session.

### POST /chat/{chat_id}/question/stream
Sendet eine Frage und erhält Streaming-Antwort.

## Wartung

### Logs prüfen

```bash
# Quivr Backend
docker logs -f quivr-backend

# Supabase
docker logs -f supabase-kong
docker logs -f supabase-db
```

### Datenbank Backup

```bash
docker exec supabase-db pg_dump -U postgres postgres > backup_$(date +%Y%m%d).sql
```

### Updates einspielen

```bash
cd ~/quivr
git pull origin develop
docker compose down
docker compose build
docker compose up -d
```

## Sicherheitshinweise

1. **Keine Secrets in Git**: `.env` Dateien nie committen
2. **Starke Passwörter**: Mindestens 32 Zeichen für JWT_SECRET und POSTGRES_PASSWORD
3. **HTTPS Only**: Traefik erzwingt SSL
4. **Firewall**: Nur Port 80/443 nach außen öffnen
5. **Supabase nicht direkt erreichbar**: Nur über Kong/Traefik

## Fehlerbehebung

### Supabase startet nicht
```bash
docker compose down -v
docker compose up -d
```

### Quivr kann Supabase nicht erreichen
- Prüfen ob beide im gleichen Docker Network sind
- DNS-Auflösung testen: `docker exec quivr-backend ping supabase-db`

### Chat-Token funktioniert nicht
- API Key in Supabase `api_keys` Tabelle prüfen
- Brain-Zuordnung zum User prüfen

## Projektstruktur

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
├── supabase/                   # Database Migrations
├── docker-compose.yml
└── .env.example
```

## Lizenz

Apache License 2.0 - siehe [LICENSE](LICENSE)

## Verwandte Projekte

- [quivr-moodle-plugin](https://github.com/sebastian-schluricke/quivr-moodle-plugin) - Moodle Activity Plugin
- [QuivrHQ/quivr](https://github.com/QuivrHQ/quivr) - Original Quivr Projekt

## Support

- [GitHub Issues](https://github.com/sebastian-schluricke/quivr-for-moodle/issues)
