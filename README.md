# Quivr for Moodle - RAG Backend for Schools

A fork of [QuivrHQ/quivr](https://github.com/QuivrHQ/quivr), optimized for integration with Moodle learning platforms.

## Pedagogical Approach

Students often hesitate to ask questions in class - whether from fear of embarrassment or because the right moment doesn't arise. An AI assistant based on course materials provides a low-barrier access:

- **Anonymous Help**: Students can ask questions at any time without exposing themselves in front of classmates
- **Insights for Teachers**: Questions asked reveal where understanding gaps exist - valuable feedback for lesson planning
- **Always Available**: The assistant answers questions outside of class time
- **Source-Based**: Answers reference the actual course materials

## Features

### Moodle Integration

- **Automatic Synchronization**: Course materials are indexed directly from Moodle
- **Visibility Control**: Only sections visible to students are included in the knowledge base
- **Multiple Assistants per Course**: Different brains for various topics or learning objectives
- **Popup Chat**: Floating chat button available on all course pages

### Didactic Options

- **Counter-Question Mode**: The assistant can respond with questions to encourage independent thinking
- **Quiz Integration**: Embedding comprehension questions into the conversation
- **Customizable Prompts**: Assistant behavior adaptable to pedagogical goals

### Security

- **Scoped Token System**: Time-limited, brain-specific tokens - API keys are never transmitted to the browser
- **Data Privacy**: Self-hosted solution, all data remains on your own server

## Architecture

**Interaction with Moodle:**
```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Moodle Plugin  │◄───────►│  Quivr Backend  │◄───────►│  LLM Provider   │
│  (Frontend)     │  Token  │  (This Repo)    │  API    │  (OpenAI)       │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

**Server Infrastructure (three Docker Compose stacks):**
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

## Supported LLM Models

| Model | Description | Recommended |
|-------|-------------|-------------|
| `gpt-4o-mini` | Fast, cost-effective | ✓ Default |
| `gpt-4o` | Powerful | For complex tasks |
| `gpt-4-turbo` | GPT-4 with large context | - |
| `gpt-3.5-turbo` | Fast, very affordable | Budget option |

## Prerequisites

- **Linux Server** (Ubuntu 22.04 recommended)
- **Docker & Docker Compose** v2.x
- **Domain with DNS** (e.g., `quivr.your-school.com`, `supabase.your-school.com`)
- **OpenAI API Key**
- **Minimum 8 GB RAM**, 50 GB storage

## Installation

Installation is done in three steps:

### 1. Traefik (Reverse Proxy with SSL)

```bash
mkdir -p ~/traefik && cd ~/traefik

# Create Docker network
docker network create supabase_network_secondbrain

# Create docker-compose.yml
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
      - "--certificatesresolvers.myresolver.acme.email=admin@your-school.com"
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

### 2. Supabase (Database & Auth)

```bash
mkdir -p ~/supabase && cd ~/supabase
git clone https://github.com/supabase/supabase.git --depth 1
cd supabase/docker
cp .env.example .env
```

**Modify .env:**
```bash
# Generate secure passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 48)

# Generate keys (see Supabase Docs)
# https://supabase.com/docs/guides/self-hosting/docker

# Adjust domain
SUPABASE_PUBLIC_URL=https://supabase.your-school.com
API_EXTERNAL_URL=https://supabase.your-school.com
```

**Modify docker-compose.yml:**
- Kong service: Add Traefik labels
- Add network `supabase_network_secondbrain`
- Remove ports (Traefik handles them)

```bash
docker compose up -d
```

### 3. Quivr Backend

```bash
mkdir -p ~/quivr && cd ~/quivr
git clone https://github.com/sebastian-schluricke/quivr-for-moodle.git .
cp .env.example .env
```

**Modify .env:**
```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Supabase connection (from Supabase .env)
SUPABASE_URL=https://supabase.your-school.com
SUPABASE_SERVICE_KEY=<SERVICE_ROLE_KEY>
JWT_SECRET_KEY=<JWT_SECRET>
PG_DATABASE_URL=postgresql://postgres:<POSTGRES_PASSWORD>@supabase-db:5432/postgres

# Backend URL
BACKEND_URL=https://quivr.your-school.com
```

**Database migrations with Supabase CLI:**
```bash
# Install Supabase CLI (if not already installed)
# https://supabase.com/docs/guides/cli

# Change to backend directory
cd ~/quivr/backend

# Apply migrations to database
supabase db push --db-url "postgresql://postgres:<POSTGRES_PASSWORD>@localhost:5432/postgres"
```

**Start Quivr:**
```bash
cd ~/quivr
docker compose up -d
```

## Environment Variables

### Required Variables (.bashrc or .env)

```bash
# Supabase Credentials
export POSTGRES_PASSWORD="<secure-password>"
export JWT_SECRET="<jwt-secret-min-32-chars>"
export ANON_KEY="<supabase-anon-key>"
export SERVICE_ROLE_KEY="<supabase-service-role-key>"
export SUPABASE_URL="https://supabase.your-school.com"

# Database URLs
export PG_DATABASE_URL="postgresql://postgres:${POSTGRES_PASSWORD}@supabase-db:5432/postgres"
export PG_DATABASE_ASYNC_URL="postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@supabase-db:5432/postgres"

# JWT for Quivr
export JWT_SECRET_KEY="${JWT_SECRET}"
export SUPABASE_SERVICE_KEY="${SERVICE_ROLE_KEY}"
export NEXT_PUBLIC_SUPABASE_ANON_KEY="${ANON_KEY}"
```

### Generating Supabase Keys

The Anon and Service Role keys must be generated from the JWT Secret:

```bash
# Online Generator: https://supabase.com/docs/guides/self-hosting/docker#generate-api-keys
# Or manually with jwt.io
```

## Moodle Configuration

### Web Service Setup for Course Sync

To allow Quivr to read course contents and sections from Moodle, you need to configure an External Service with specific Web Service functions.

**Site Administration → Server → Web services → External services:**

1. Create a new service (e.g., "Quivr Integration")
2. Enable the service and set "Authorised users only" if desired
3. Add the following four functions:

| Function | Description | Required Capabilities |
|----------|-------------|----------------------|
| `core_course_get_contents` | Get course contents | `moodle/course:update`, `moodle/course:viewhiddencourses` |
| `core_course_get_courses` | Return course details | `moodle/course:view`, `moodle/course:update`, `moodle/course:viewhiddencourses` |
| `core_enrol_get_users_courses` | Get the list of courses where a user is enrolled | `moodle/course:viewparticipants` |
| `core_webservice_get_site_info` | Return site info / user info / list web service functions | - |

**Site Administration → Server → Web services → Manage tokens:**

1. Create a token for the teacher who will sync the course
2. The teacher authenticates once with their Moodle username and password
3. The generated token is used by Quivr to access the course contents

**Note:** The teacher must have the required capabilities listed above for their courses

## API Endpoints for Moodle

### POST /chat/token
Creates a time-limited, brain-specific token.

```bash
curl -X POST https://quivr.your-school.com/chat/token \
  -H "Authorization: Bearer MASTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"brain_id": "brain-uuid", "ttl_minutes": 10}'
```

### GET /brains/
Lists all available brains.

### POST /chat
Creates a new chat session.

### POST /chat/{chat_id}/question/stream
Sends a question and receives a streaming response.

## Maintenance

### Check Logs

```bash
# Quivr Backend
docker logs -f quivr-backend

# Supabase
docker logs -f supabase-kong
docker logs -f supabase-db
```

### Database Backup

```bash
docker exec supabase-db pg_dump -U postgres postgres > backup_$(date +%Y%m%d).sql
```

### Apply Updates

```bash
cd ~/quivr
git pull origin main
docker compose down
docker compose build
docker compose up -d
```

## Security Notes

1. **No Secrets in Git**: Never commit `.env` files
2. **Strong Passwords**: Minimum 32 characters for JWT_SECRET and POSTGRES_PASSWORD
3. **HTTPS Only**: Traefik enforces SSL
4. **Firewall**: Only open ports 80/443 externally
5. **Supabase Not Directly Accessible**: Only via Kong/Traefik

## Troubleshooting

### Supabase Won't Start
```bash
docker compose down -v
docker compose up -d
```

### Quivr Cannot Reach Supabase
- Check if both are in the same Docker network
- Test DNS resolution: `docker exec quivr-backend ping supabase-db`

### Chat Token Not Working
- Check API key in Supabase `api_keys` table
- Verify brain assignment to user

## Project Structure

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
│   ├── supabase/
│   │   └── migrations/         # Database Migrations
│   └── worker/                 # Celery Worker
├── docker-compose.yml
└── .env.example
```

## License

Apache License 2.0 - see [LICENSE](LICENSE)

## Related Projects

- [quivr-moodle-plugin](https://github.com/sebastian-schluricke/quivr-moodle-plugin) - Moodle Activity Plugin
- [QuivrHQ/quivr](https://github.com/QuivrHQ/quivr) - Original Quivr Project

## Support

- [GitHub Issues](https://github.com/sebastian-schluricke/quivr-for-moodle/issues)
