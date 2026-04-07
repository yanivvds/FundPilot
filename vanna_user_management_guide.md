# Vanna AI: move out of Demo mode and add user management

## What “Demo mode” means

In Vanna 2.0, demo mode usually means two things:

1. You are using **in-memory demo components** like `DemoAgentMemory()`
2. You are **not resolving real users yet**, so everyone is effectively treated like a demo/guest user

To move toward a real app, the docs show that you should replace demo/in-memory pieces with:

- a real **`UserResolver`**
- a real/persistent **Agent Memory** backend
- group-based **tool permissions**
- a real **FastAPI or Flask deployment** with `dev_mode=False`

---

## The simple migration plan

### Step 1 — Stop using demo memory

If your code currently has something like:

```python
from vanna.integrations.local.agent_memory import DemoAgentMemory

memory = DemoAgentMemory()
```

replace it with a persistent memory backend, for example Chroma:

```python
from vanna.integrations.chromadb import ChromaAgentMemory

memory = ChromaAgentMemory(
    persist_directory="./chroma_memory",
    collection_name="tool_memories"
)
```

Why: `DemoAgentMemory()` is the in-memory demo backend, while `ChromaAgentMemory()` stores memories locally on disk so they survive restarts.

---

### Step 2 — Add a real `UserResolver`

Vanna’s model is: **you handle authentication, Vanna consumes it**.

That means Vanna does **not** log users in for you.  
Instead, you implement a `UserResolver` that reads identity from your app’s cookies, session, JWT, or headers, and returns a `User` object.

Minimal example:

```python
from vanna.core.user import UserResolver, User, RequestContext

class MyUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        # Example: read from a header or cookie
        user_email = request_context.get_header("X-User-Email") or request_context.get_cookie("vanna_email")

        if not user_email:
            user_email = "guest@example.com"

        groups = ["admin"] if user_email.endswith("@yourcompany.com") else ["user"]

        return User(
            id=user_email,
            username=user_email.split("@")[0],
            email=user_email,
            group_memberships=groups,
            metadata={}
        )
```

In production, replace this with your real auth source:

- NextAuth / Auth.js session
- Clerk
- Auth0
- Azure AD / Entra ID
- your own JWT or session cookie

---

### Step 3 — Pass the resolver into the `Agent`

Your Vanna `Agent` should be created with both:

- `user_resolver=...`
- `agent_memory=...`

Example:

```python
from vanna import Agent

agent = Agent(
    llm_service=llm_service,
    tool_registry=tools,
    user_resolver=MyUserResolver(),
    agent_memory=memory
)
```

This is the key switch that makes the app user-aware.

---

### Step 4 — Restrict tools by groups

Once users have `group_memberships`, register tools with access groups.

Example:

```python
from vanna import ToolRegistry
from vanna.tools import RunSqlTool, VisualizeDataTool

tools = ToolRegistry()

tools.register_local_tool(
    RunSqlTool(sql_runner=sql_runner),
    access_groups=["user", "admin"]
)

tools.register_local_tool(
    VisualizeDataTool(),
    access_groups=["admin"]
)
```

Meaning:

- regular users can run SQL
- only admins can use visualization

This is the first layer of user management in Vanna.

---

### Step 5 — Add row/table-level restrictions in your own code

Vanna gives you the **user identity** and **groups**, but you still need to enforce data access in your database/tool layer.

A practical pattern is:

- map each user/group to allowed tables
- or use a per-user DB role / connection
- or inject access constraints into the prompt/context

Example idea from the docs:

```python
class PermissionBasedEnhancer(LlmContextEnhancer):
    def __init__(self, permission_service):
        self.permissions = permission_service

    async def enhance_system_prompt(self, system_prompt, user_message, user):
        accessible_tables = await self.permissions.get_accessible_tables(user.id)

        constraints = "\n\n## Data Access Constraints\n\n"
        constraints += f"You can only query these tables: {', '.join(accessible_tables)}\n"
        constraints += "If the user asks for other tables, explain they don't have access.\n"

        return system_prompt + constraints
```

Important: prompt constraints help, but **real security should be enforced in the database/tool layer too**.

---

### Step 6 — Turn off dev/demo deployment settings

When deploying with FastAPI, set `dev_mode=False`.

Example:

```python
from vanna.servers.fastapi import VannaFastAPIServer

server = VannaFastAPIServer(
    agent,
    config={
        "dev_mode": False,
        "cors": {
            "enabled": True,
            "allow_origins": ["https://yourapp.com"],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST"],
            "allow_headers": ["Authorization", "Content-Type", "X-User-Email"]
        }
    }
)

app = server.create_app()
```

This is the deployment side of exiting demo/dev mode.

---

## Recommended order for your project

### Phase 1 — Basic user management
Do this first:

1. Replace `DemoAgentMemory()` with `ChromaAgentMemory()`
2. Add `MyUserResolver`
3. Return `User(id, username, email, group_memberships)`
4. Register tools with `access_groups`
5. Run with `dev_mode=False`

### Phase 2 — Real authentication
Then connect it to your real stack:

- if you already have login in your app, expose the user via cookie/header/JWT
- read that in `UserResolver`
- derive groups from your own users table or auth claims

### Phase 3 — Real authorization
Then harden access:

- per-group tool access
- allowed tables/views by user/group
- row-level security in the database if possible
- audit logging for sensitive queries

---

## A good minimal production-ready skeleton

```python
from vanna import Agent, ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.integrations.chromadb import ChromaAgentMemory
from vanna.integrations.openai import OpenAILlmService
from vanna.integrations.postgres import PostgresRunner
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.servers.fastapi import VannaFastAPIServer

class MyUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        user_email = request_context.get_header("X-User-Email")

        if not user_email:
            user_email = "guest@example.com"

        groups = ["admin"] if user_email.endswith("@yourcompany.com") else ["user"]

        return User(
            id=user_email,
            username=user_email.split("@")[0],
            email=user_email,
            group_memberships=groups,
            metadata={}
        )

llm_service = OpenAILlmService(api_key="YOUR_OPENAI_KEY", model="gpt-5")
sql_runner = PostgresRunner(connection_string="postgresql://user:pass@host:5432/db")
memory = ChromaAgentMemory(
    persist_directory="./chroma_memory",
    collection_name="tool_memories"
)

tools = ToolRegistry()
tools.register_local_tool(RunSqlTool(sql_runner=sql_runner), access_groups=["user", "admin"])
tools.register_local_tool(VisualizeDataTool(), access_groups=["admin"])

agent = Agent(
    llm_service=llm_service,
    tool_registry=tools,
    user_resolver=MyUserResolver(),
    agent_memory=memory
)

server = VannaFastAPIServer(
    agent,
    config={
        "dev_mode": False,
        "cors": {
            "enabled": True,
            "allow_origins": ["http://localhost:3000"],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST"],
            "allow_headers": ["Authorization", "Content-Type", "X-User-Email"]
        }
    }
)

app = server.create_app()
```

Run with Uvicorn:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## What to change in your current codebase

Search your code for these patterns and replace them:

### Replace this
```python
DemoAgentMemory()
```

### With this
```python
ChromaAgentMemory(...)
```

### Add this if missing
```python
user_resolver=MyUserResolver()
```

### Add access groups when registering tools
```python
register_local_tool(..., access_groups=["user"])
```

### Make sure deployment config has
```python
"dev_mode": False
```

---

## Important note about the docs

Some Vanna docs pages are still marked as **placeholder / coming soon**, but the main architecture is already clear and consistent:

- Vanna 2.0 is designed to be **user-aware**
- user identity flows through the agent using `UserResolver`
- permissions are enforced through groups and tool access
- demo memory should be replaced with a persistent backend for real use

---

## Practical recommendation for you

Since you are building an app and want to “exit Demo mode”, the **best next move** is:

1. keep your current Vanna agent
2. swap memory to `ChromaAgentMemory`
3. implement a simple resolver using a header first (`X-User-Email`)
4. add groups like `["admin"]` and `["user"]`
5. restrict tools by group
6. later connect the resolver to your real auth provider

That gives you a clean migration path without rebuilding everything.

---

## Sources consulted

- Vanna Docs homepage
- Auth / Authentication & Permissions docs
- Configure examples
- FastAPI deployment docs
- Python API overview
- Migration docs
