# FundPilot — Production Deployment Guide (Windows)

## Architecture

```
Internet (HTTPS)
      │
      ▼
  Caddy (port 443)          ← automatic TLS via Let's Encrypt
      │
      ▼
  Uvicorn / FastAPI          ← bound to 127.0.0.1:8000 only
  (FundPilot Windows Service)
      │
      ├── OpenAI API         (outbound HTTPS)
      ├── Supabase           (outbound HTTPS)
      └── SQL Server server  (internal network)
```

**CI/CD:** GitHub Actions self-hosted runner on the VM → `deploy.ps1` on every push to `main`.

---

## Prerequisites (install manually before running install.ps1)

| Software | Download | Notes |
|---|---|---|
| Python 3.11+ | https://www.python.org/downloads/ | Add to PATH during install |
| Node.js 18+ | https://nodejs.org/ | LTS version |
| Git | https://git-scm.com/download/win | Add to PATH during install |
| ODBC Driver 18 | https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server | Required for SQL Server |

---

## Initial Setup

### 1. Run the install script (once, as Administrator)

```powershell
# Open PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope LocalMachine   # allow local scripts

# Download the install script (or clone the repo first)
# Then run:
C:\FundPilot\deploy\install.ps1
```

The script will:
- Clone the repo to `C:\FundPilot`
- Create a Python venv and install dependencies
- Build the frontend bundle
- Prompt you to fill in `.env`
- Install NSSM and register `FundPilot` as a Windows Service (Uvicorn)
- Install Caddy and register it as a Windows Service
- Open firewall ports 80 and 443

### 2. Configure your domain

In your DNS provider, add an **A record**:

```
Type: A
Name: @  (or subdomain, e.g. fundpilot)
Value: <your VM's public IP>
TTL: 300
```

Edit `C:\Caddy\Caddyfile` — replace `yourdomain.com` with your real domain.

Restart Caddy:
```powershell
nssm restart Caddy
```

Caddy will automatically obtain a TLS certificate from Let's Encrypt within ~30 seconds.

### 3. Verify deployment

```
https://yourdomain.com/health
→ {"status": "healthy", "service": "vanna"}
```

---

## GitHub Actions Runner (CI/CD)

This enables automatic deploys on every push to `main`.

### Install the runner on the VM

1. Go to your GitHub repo → **Settings → Actions → Runners → New self-hosted runner**
2. Choose **Windows** as the OS
3. Follow the on-screen instructions. The commands look like:

```powershell
# Run in PowerShell as Administrator in C:\actions-runner
mkdir C:\actions-runner; cd C:\actions-runner
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.x.x/actions-runner-win-x64-2.x.x.zip -OutFile actions-runner.zip
Expand-Archive actions-runner.zip -DestinationPath .

# Register the runner (token shown on the GitHub page)
.\config.cmd --url https://github.com/YOUR_ORG/FundPilot --token YOUR_TOKEN

# Install as Windows Service (so it survives reboots)
.\svc.ps1 install
.\svc.ps1 start
```

4. The runner label is `self-hosted` by default — this matches what's in `deploy.yml`.

### How deployments work

```
Push to main
    │
    ▼
GitHub Actions triggers job on self-hosted runner
    │
    ▼
Runner executes: C:\FundPilot\deploy\deploy.ps1
    │
    ├── git reset --hard origin/main
    ├── pip install -r requirements.txt
    ├── npm ci && npm run build
    ├── copy vanna-components.js → static/
    ├── nssm restart FundPilot
    └── health check loop (30 sec max)
```

---

## `.env` Configuration (production values)

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# SQL Server (internal network)
MSSQL_CONN_STR=DRIVER={ODBC Driver 18 for SQL Server};SERVER=server;DATABASE=CWESystemConfig;UID=kalff_ai;PWD=...;TrustServerCertificate=yes

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=sb_secret_...
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...

# Auth
REQUIRE_MFA=true

# CORS — set to your exact domain, no trailing slash
ALLOWED_ORIGINS=https://yourdomain.com

# ChromaDB — use an absolute path outside the repo
CHROMADB_PERSIST_DIR=C:\FundPilot\chromadb_data
```

> **Security:** The `.env` file is restricted to SYSTEM and Administrators by `install.ps1`.
> Never commit it to git. It's in `.gitignore`.

---

## Day-to-day Operations

### View live logs

```powershell
# Application logs
Get-Content C:\FundPilot\logs\stdout.log -Wait -Tail 50

# Error logs
Get-Content C:\FundPilot\logs\stderr.log -Wait -Tail 50

# Caddy access logs
Get-Content C:\Caddy\logs\access.log -Wait -Tail 50
```

### Restart the app

```powershell
nssm restart FundPilot
```

### Manual deploy (without pushing to git)

```powershell
# Run as Administrator or as the runner service account
C:\FundPilot\deploy\deploy.ps1
```

### Check service status

```powershell
Get-Service FundPilot
Get-Service Caddy
```

### Update the domain in Caddy

Edit `C:\Caddy\Caddyfile`, then:
```powershell
nssm restart Caddy
```

---

## Security checklist

- [x] Uvicorn bound to `127.0.0.1` only — not reachable directly from internet
- [x] Caddy enforces HTTPS, redirects HTTP → HTTPS automatically
- [x] HSTS header set (1 year)
- [x] Port 8000 firewall rule removed by `install.ps1`
- [x] Only ports 80 and 443 open to internet
- [x] `.env` permissions restricted to SYSTEM and Administrators
- [x] `.env` never committed to git
- [x] Supabase JWT + MFA enforced (`REQUIRE_MFA=true`)
- [x] All SQL queries read-only (SELECT only, validated in `fundpilot_sql_runner.py`)
- [x] `ALLOWED_ORIGINS` set to exact production domain (no wildcards)
- [ ] SQL Server firewall: restrict to VM's internal IP only
- [ ] Rotate API keys periodically (OpenAI, Supabase)
