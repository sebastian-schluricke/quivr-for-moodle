# Local Development Setup

Diese Anleitung beschreibt, wie du das Quivr-Projekt lokal in PyCharm ohne Docker ausführen kannst.

## Voraussetzungen

- Python 3.11 oder 3.12
- Node.js 18+ und npm
- Supabase CLI
- Docker (nur für Supabase)
- PyCharm Professional (empfohlen)

## Setup-Schritte

### 1. Supabase starten

Supabase läuft noch in Docker-Containern und stellt die Datenbank und Auth-Services bereit:

```bash
cd backend
supabase start
```

Wichtige URLs nach dem Start:
- **API URL**: http://127.0.0.1:54321
- **Database URL**: postgresql://postgres:postgres@127.0.0.1:54322/postgres
- **Studio URL**: http://127.0.0.1:54323

### 2. Backend-Setup

#### 2.1 Virtual Environment erstellen

```bash
cd backend/api
python3 -m venv venv
source venv/bin/activate  # Auf Windows: venv\Scripts\activate
```

#### 2.2 Dependencies installieren

```bash
# Zuerst quivr-core installieren
pip install --upgrade pip
pip install -e ../core

# Dann quivr-api installieren
pip install -e .
```

#### 2.3 Environment-Variablen

Die `.env` Datei im Root-Verzeichnis ist bereits konfiguriert. Wichtige Variablen:

```env
# API Keys
OPENAI_API_KEY=your-openai-api-key
COHERE_API_KEY=your-cohere-api-key

# Supabase (local)
SUPABASE_URL=http://host.docker.internal:54321
PG_DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:54322/postgres
```

#### 2.4 Backend in PyCharm starten

Option 1: Run Configuration nutzen (empfohlen)
- In PyCharm: Run > Edit Configurations
- Wähle "Backend API" aus
- Klicke auf den grünen Play-Button

Option 2: Manuell via Terminal
```bash
cd backend/api
source venv/bin/activate
python -m uvicorn quivr_api.main:app --host 0.0.0.0 --port 5050 --reload --log-level info
```

Das Backend läuft dann auf: http://localhost:5050

API-Dokumentation: http://localhost:5050/docs

### 3. Frontend-Setup

#### 3.1 Dependencies installieren

```bash
cd frontend
npm install
```

#### 3.2 Environment-Variablen

Kopiere `.env.example` zu `.env`:

```bash
cp .env.example .env
```

Wichtige Variablen in `frontend/.env`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:5050
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
```

#### 3.3 Frontend in PyCharm starten

Option 1: Run Configuration nutzen (empfohlen)
- In PyCharm: Run > Edit Configurations
- Wähle "Frontend Dev" aus
- Klicke auf den grünen Play-Button

Option 2: Manuell via Terminal
```bash
cd frontend
npm run dev
```

Das Frontend läuft dann auf: http://localhost:3000

### 4. Login-Daten

Standard-Login für die lokale Entwicklung:
- **Email**: admin@quivr.app
- **Passwort**: admin

## PyCharm Run Configurations

Die folgenden Run Configurations wurden automatisch erstellt:

### Backend API
- **Type**: Python
- **Module**: uvicorn
- **Parameters**: `quivr_api.main:app --host 0.0.0.0 --port 5050 --reload --log-level info`
- **Working Directory**: `backend/api`
- **Python Interpreter**: `backend/api/venv`

### Frontend Dev
- **Type**: npm
- **Package.json**: `frontend/package.json`
- **Command**: `run dev`

## Troubleshooting

### Python Version Konflikt

Das Projekt benötigt Python < 3.12. Wenn du Python 3.12 installiert hast, können einige Dependencies Probleme machen. In diesem Fall:

1. Installiere Python 3.11:
   ```bash
   # Ubuntu/WSL
   sudo apt install python3.11 python3.11-venv

   # macOS
   brew install python@3.11
   ```

2. Erstelle das venv mit Python 3.11:
   ```bash
   python3.11 -m venv venv
   ```

### Supabase Container-Konflikte

Falls du Fehler wie "container name already in use" bekommst:

```bash
cd backend
supabase stop
supabase start
```

### Port bereits in Verwendung

Falls Port 5050 (Backend) oder 3000 (Frontend) bereits belegt ist:

Backend:
```bash
# Anderen Port verwenden
python -m uvicorn quivr_api.main:app --host 0.0.0.0 --port 5051 --reload
```

Frontend:
```bash
# package.json anpassen oder
PORT=3001 npm run dev
```

### Import-Fehler

Falls du Fehler wie "ModuleNotFoundError: No module named 'quivr_core'" bekommst:

```bash
cd backend/api
source venv/bin/activate
pip install -e ../core
pip install -e .
```

## Nützliche Kommandos

### Supabase

```bash
# Status prüfen
supabase status

# Container stoppen
supabase stop

# Container neustarten
supabase stop && supabase start

# Logs anzeigen
docker logs supabase_db_secondbrain

# Migrationen anwenden
supabase migration up
```

### Backend

```bash
# Tests ausführen
cd backend/api
source venv/bin/activate
pytest

# Type-Checking
mypy quivr_api

# Linting
ruff check .
```

### Frontend

```bash
# Tests ausführen
cd frontend
npm test

# Linting
npm run lint

# Type-Checking
npm run test-type

# Build
npm run build
```

## Projektstruktur

```
quivr/
├── backend/
│   ├── api/              # FastAPI Backend
│   │   ├── venv/         # Python Virtual Environment
│   │   ├── quivr_api/    # API Code
│   │   └── pyproject.toml
│   ├── core/             # Quivr Core Library (RAG)
│   │   ├── quivr_core/
│   │   └── pyproject.toml
│   ├── worker/           # Celery Worker
│   └── supabase/         # Supabase Migrationen
├── frontend/             # Next.js Frontend
│   ├── app/
│   ├── package.json
│   └── .env
├── .env                  # Backend Environment
└── .run/                 # PyCharm Run Configurations
```

## Weitere Ressourcen

- [Quivr Dokumentation](https://docs.quivr.app/)
- [Prompt-System Dokumentation](prompts.md)
- [API Usage Guide](api-usage.md)
