# FundPilot — Architecture & Deployment

## 1. System Architecture

How all the pieces connect — from a user's browser to the SQL Server on the internal network.

```mermaid
flowchart LR
    USER(["👤 User\nbrowser"])

    subgraph VM["🖥️ Windows VM"]
        CADDY["🔐 Caddy\nTLS · Proxy · Headers\nport 443"]
        FASTAPI["⚡ FastAPI\nAuth · CORS · SQL guard\nlocalhost:8000"]
    end

    subgraph EXTERNAL["External services"]
        OPENAI["🤖 OpenAI"]
        SUPABASE["🛡️ Supabase\nJWT auth"]
    end

    SQL[("🗄️ SQL Server\n192.168.x.x\n6 databases")]

    GH(["⚙️ GitHub\npush to main"])
    RUNNER["🔄 Actions Runner\ndeploy.ps1"]

    USER --> |"HTTPS port 443"| CADDY
    CADDY --> |"localhost only"| FASTAPI
    FASTAPI --> |"LLM calls"| OPENAI
    FASTAPI --> |"validate JWT"| SUPABASE
    FASTAPI --> |"SELECT only"| SQL
    GH --> |"triggers workflow"| RUNNER
    RUNNER --> |"restart service"| FASTAPI

    style VM fill:#fff8f0,stroke:#d4a84b
    style EXTERNAL fill:#f0f4ff,stroke:#8fa8d4
```

---

## 2. What Happens When a User Asks a Question

The full lifecycle of a single chat message.

```mermaid
sequenceDiagram
    actor User
    participant Caddy
    participant FastAPI
    participant Supabase
    participant OpenAI
    participant SQLServer

    User ->> Caddy: HTTPS + JWT token
    Note over Caddy: Terminates TLS, adds security headers
    Caddy ->> FastAPI: HTTP localhost only

    FastAPI ->> Supabase: Validate JWT
    Supabase -->> FastAPI: User confirmed + MFA passed

    alt No valid token or MFA not passed
        FastAPI -->> User: 401 Unauthorized
    end

    FastAPI ->> OpenAI: Question + system prompt
    OpenAI -->> FastAPI: Tool call to run_sql

    Note over FastAPI: Blocks anything except SELECT
    FastAPI ->> SQLServer: Safe SELECT query
    SQLServer -->> FastAPI: Result rows

    FastAPI ->> OpenAI: Tool result
    OpenAI -->> FastAPI: Final answer streamed
    FastAPI -->> User: SSE stream over HTTPS
```

---

## 3. How a Deploy Works

What happens the moment code is pushed to `main`.

```mermaid
flowchart TD
    A(["💻 git push to main"])
    B["GitHub Actions\ntriggers deploy.yml"]
    C["Self-hosted runner\nstarts on Windows VM"]

    subgraph SCRIPT["deploy.ps1"]
        D["git reset --hard origin/main"]
        E["pip install -r requirements.txt"]
        F["npm ci + npm run build"]
        G["copy vanna-components.js to static/"]
        H["nssm restart FundPilot"]
        I["GET /health — up to 10 retries"]
    end

    OK(["✅ Live"])
    FAIL(["❌ Failed — visible in GitHub Actions"])

    A --> B --> C --> D
    D --> E --> F --> G --> H --> I
    I --> OK
    I -.-> |"timeout"| FAIL

    style SCRIPT fill:#f9f9f9,stroke:#ccc
    style OK fill:#f0fff4,stroke:#4db87a
    style FAIL fill:#fff0f0,stroke:#d44
```

---

## 4. Security Layers

Every request passes through these defences in order.

```mermaid
flowchart TD
    REQ(["🌐 Incoming request"])

    L1["Layer 1 · Transport\nCaddy forces HTTPS\nHTTP is redirected, HSTS for 1 year"]

    L2["Layer 2 · Authentication\nSupabase JWT checked on every request\nMFA level AAL2 required"]

    L3["Layer 3 · Authorisation\nCORS allows only the production domain\nUser roles from Supabase metadata"]

    L4["Layer 4 · SQL safety\nOnly SELECT allowed\nINSERT UPDATE DELETE EXEC XP_ all blocked\nRow limit capped at 10 000"]

    L5["Layer 5 · Network\nFastAPI on 127.0.0.1 only\nPort 8000 blocked in Windows Firewall\nSQL Server on internal LAN only"]

    L6["Layer 6 · Secrets\n.env only readable by SYSTEM and Admins\nSecret keys never leave the server"]

    OK(["✅ Response returned"])

    REQ --> L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> OK

    style REQ fill:#f0f4ff,stroke:#8fa8d4
    style L1 fill:#fff8f0,stroke:#f0a500
    style L2 fill:#fff8f0,stroke:#f0a500
    style L3 fill:#fff8f0,stroke:#f0a500
    style L4 fill:#fff8f0,stroke:#f0a500
    style L5 fill:#fff8f0,stroke:#f0a500
    style L6 fill:#fff8f0,stroke:#f0a500
    style OK fill:#f0fff4,stroke:#4db87a
```

---

## 5. What Each File Does

| File | When to use | What it does |
|---|---|---|
| `deploy/install.ps1` | **Once** — fresh Windows VM, run as Administrator | Installs NSSM & Caddy, clones the repo, creates Python venv, builds the frontend, registers both as Windows Services, opens firewall ports 80 & 443 |
| `deploy/deploy.ps1` | **Automatically** on every push to `main`, or run manually | Pulls latest code, reinstalls Python deps, rebuilds the JS bundle, copies it to `static/`, restarts the service, verifies `/health` |
| `Caddyfile` | Edit **once** to set your domain, then leave it | Tells Caddy which domain to serve, where to proxy API requests, which security headers to set |
| `.github/workflows/deploy.yml` | Never run manually — GitHub triggers it | Tells GitHub Actions to run `deploy.ps1` on the self-hosted Windows runner on every push to `main` |
