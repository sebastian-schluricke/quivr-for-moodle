# Quivr Development Scripts

Diese Scripts erleichtern das Starten und Stoppen des Quivr-Stacks während der Entwicklung.

## Verfügbare Scripts

### 🚀 Stack starten

#### Kompletter Stack in tmux
```bash
cd backend
./start-all.sh
```
Startet alle Services (Backend, Celery, Notifier, Frontend) in einem tmux-Session mit 4 Panes:
- **Pane 0 (links)**: Backend API (Port 5050)
- **Pane 1 (oben rechts)**: Celery Worker
- **Pane 2 (mitte rechts)**: Notifier
- **Pane 3 (unten rechts)**: Frontend (Port 3000)

**Wichtige tmux Kommandos:**
- `Ctrl+b` dann `d` - Session verlassen (Services laufen weiter)
- `Ctrl+b` dann `Pfeiltasten` - Zwischen Panes wechseln
- `Ctrl+c` - Service im aktuellen Pane stoppen
- `tmux attach -t quivr-dev` - Wieder zur Session verbinden
- `tmux kill-session -t quivr-dev` - Session beenden

#### Einzelne Services starten
```bash
# Backend API
./start-backend.sh

# Frontend (auf 0.0.0.0 für Windows-Zugriff)
./start-frontend.sh

# Celery Worker
./start-celery.sh

# Notifier
./start-notifier.sh
```

### 🔄 Stack neu starten

#### In laufender tmux-Session
```bash
./restart-all.sh
```
Stoppt und startet alle Services in der bestehenden tmux-Session neu.

### 🛑 Stack stoppen

```bash
./stop-all.sh
```
Stoppt alle Services:
- Wenn eine tmux-Session läuft, wird diese beendet
- Ansonsten werden alle einzelnen Prozesse gestoppt

**Hinweis:** Supabase wird nicht gestoppt. Um Supabase zu stoppen:
```bash
cd backend
supabase stop
```

## Wichtige Hinweise

### Windows/WSL Zugriff
- **Backend** läuft auf `0.0.0.0:5050` → Von Windows erreichbar unter `localhost:5050`
- **Frontend** läuft auf `0.0.0.0:3000` → Von Windows erreichbar unter `localhost:3000`

### Logs
Bei Verwendung von tmux sind die Logs direkt in den Panes sichtbar.

Bei einzeln gestarteten Services:
```bash
# Backend Logs (wenn im Hintergrund gestartet)
tail -f /tmp/quivr_backend.log

# Frontend Logs (wenn im Hintergrund gestartet)
tail -f /tmp/quivr_frontend.log
```

### Voraussetzungen
- Conda environment "quivr" muss existieren
- `.env` Datei im Projekt-Root
- Supabase muss laufen (`supabase start` im backend-Verzeichnis)
- Node.js und npm müssen installiert sein

## Schnellstart-Workflow

1. **Supabase starten** (einmalig):
   ```bash
   cd backend
   supabase start
   ```

2. **Kompletten Stack starten**:
   ```bash
   cd backend
   ./start-all.sh
   ```

3. **Von tmux-Session trennen** (Services laufen weiter):
   ```
   Ctrl+b dann d
   ```

4. **Später wieder verbinden**:
   ```bash
   tmux attach -t quivr-dev
   ```

5. **Alles stoppen**:
   ```bash
   cd backend
   ./stop-all.sh
   ```

## Services URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5050
- **API Dokumentation**: http://localhost:5050/docs
- **Supabase Studio**: http://localhost:54323

