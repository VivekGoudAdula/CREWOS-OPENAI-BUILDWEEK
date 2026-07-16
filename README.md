# CrewOS

> An autonomous AI software company that turns a product idea into a project plan, generated workspace, source code, and a live local preview.

![CrewOS landing page](frontend/public/img.png)

CrewOS is a full-stack platform for observing an AI company at work. Start in **Chat** with a product idea; CrewOS plans the work through its runtime, creates a dedicated project workspace, generates source code through Azure OpenAI, and exposes the generated application inside the Engineering workspace.

## What it does

- Secure account registration, login, refresh-token support, and protected routes.
- Event-driven runtime with an agent registry, shared memory, context assembly, lifecycle states, and activity events.
- Autonomous project planning: strategy, epics, tasks, milestones, dependencies, timeline, and project archive.
- Project-specific Engineering workspaces with repository tree, readable source files, patch history, and local live-preview support.
- Azure OpenAI-backed code generation provider—kept behind an interface so the runtime is not tied to one model provider.
- Enterprise-style React UI for Chat, Projects, Mission Control, Engineering, Quality, Analytics, and developer diagnostics.

## Architecture

```text
Browser (React + Vite)
        │
        ▼
FastAPI API ────── WebSocket activity updates
        │
        ├── Runtime: Event Bus · Registry · Memory · Context
        ├── Planning: CEO strategy → PM roadmap
        ├── Engineering: Workspace → Azure code generation → Patch → Preview
        └── MongoDB: users, projects, memories and runtime records
```

The application is split into two independently runnable projects:

```text
frontend/                 React, TypeScript, Vite, Tailwind, Zustand, Axios
backend/                  FastAPI, Pydantic v2, Motor, JWT, Passlib
backend/project_workspaces/  Generated project source trees (runtime output)
```

## Prerequisites

- Node.js 20 or later
- Python 3.11 or later
- MongoDB 7 or later
- Azure OpenAI deployment for code generation

## Configuration

Create `backend/.env`:

```env
JWT_SECRET_KEY=replace-with-a-long-random-secret
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=crewos
CORS_ORIGINS=http://localhost:5173

AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_API_VERSION=your-supported-api-version
AZURE_GPT_DEPLOYMENT=your-deployment-name
```

The frontend uses `http://localhost:8000/api/v1` by default. To override it, add `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Run locally

Install and run the backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal, install and run the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## End-to-end demo project

Use this flow for a complete local demo. It requires MongoDB and valid Azure OpenAI credentials in `backend/.env`.

1. Start MongoDB, the backend, and the frontend using the commands above.
2. Open `http://localhost:5173`, select **Start building**, and register a demo account:

   ```text
   Name: Demo Operator
   Email: demo@crewos.local
   Password: CrewOS-demo-2026
   ```

3. In **Chat**, submit this project brief:

   ```text
   Build a premium food delivery marketplace for urban professionals.
   Include restaurant discovery, dietary filters, live order tracking,
   merchant menus, payments, and saved favourites.
   ```

4. Watch the CEO and Product Manager complete strategy and roadmap creation.
5. Open the completed project from **Projects**, then select **Open generated workspace**.
6. In **Engineering**, inspect the generated source tree and open the **Live generated UI** preview.

No seed database is required. The demo account, planning record, event history, workspace, and generated source files are created by this flow. Generated workspaces are stored under `backend/project_workspaces/` and are intentionally ignored by Git.

### Quick API smoke check

With the backend running, verify the service first:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Expected response:

```json
{ "status": "healthy" }
```

## Product flow

1. Register or sign in. CrewOS opens **Chat**.
2. Describe a product, such as “Build a food delivery marketplace.”
3. The CEO produces a strategy and the PM produces a roadmap, tasks, dependencies, and milestones.
4. Engineering receives the approved plan through the event bus.
5. A real workspace is created under `backend/project_workspaces/<project-id>`.
6. Azure OpenAI generates source files and a patch is recorded.
7. Open the project’s **Generated workspace** to inspect code and view its live preview.

## Tests

```powershell
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
npm run build
```

## Important notes

- Generated workspaces are local development artifacts. They are not deployed products.
- The code-generation provider requires valid Azure OpenAI credentials; without them, Engineering reports the provider error rather than fabricating files.
- Local previews run independently per generated workspace. They are intended for development review, not production hosting.

## Key API areas

| Area | Examples |
| --- | --- |
| Authentication | `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/refresh` |
| Planning | `/api/v1/projects/plan`, `/api/v1/projects/{id}` |
| Runtime diagnostics | `/api/v1/runtime/status`, `/api/v1/agents`, `/api/v1/events` |
| Engineering | `/api/v1/repository`, `/api/v1/engineering/patches` |

## Current scope

CrewOS is a development-stage autonomous software-company environment. Planning, runtime coordination, code generation, workspace inspection, and local preview are included. Production deployment, CI/CD, and customer release automation are intentionally outside this repository’s current scope.

## How Codex Was Used

Codex was used as an implementation partner to accelerate the build while the project team retained responsibility for the product direction and architectural constraints.

### Components accelerated by Codex

- FastAPI module scaffolding, route wiring, Pydantic contracts, and frontend React page structure.
- Authentication integration, environment configuration, MongoDB connection handling, and test scaffolding.
- Enterprise UI refinement for the application shell, Chat experience, project archive, Engineering workspace, source viewer, and embedded preview panel.
- Azure OpenAI provider integration, generated-workspace support, patch/diff mechanics, and preview-server wiring.
- Debugging help for bcrypt/Passlib compatibility, Vite import failures, stale workspace IDs after reloads, and project-specific preview routing.
- Documentation, `.gitignore`, and the local demo workflow in this README.

### Architectural decisions made by the project team

- **Event-driven runtime:** agents communicate through a reusable event bus rather than direct method-to-method agent chains.
- **Agent responsibility boundaries:** CEO owns strategy, PM owns roadmap generation, Engineering owns workspace/code generation, and QA remains a separate validation concern.
- **Provider abstraction:** model calls are isolated behind a code-generation provider so agent code is not coupled to Azure OpenAI.
- **Workspace isolation:** each project receives its own generated source directory and preview process rather than overwriting the CrewOS application.
- **Product-first UI:** runtime, registry, memory, and event views are kept as developer diagnostics while the main product flow focuses on Chat, Projects, Engineering, and previewable output.

### Where Codex improved iteration speed

Codex was especially effective during repeated full-stack iteration: tracing runtime event loops that blocked planning, converting the generated workspace into a runnable Vite app, repairing missing generated stylesheet imports, and making previews resolve to the correct project rather than a shared development server. These changes shortened the feedback loop between an AI-generated artifact and a visible, inspectable product result.
