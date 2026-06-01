# StackPilot AI

StackPilot AI is an AI application technology stack selection assistant. It helps developers and small engineering teams turn a vague technical decision into a structured, evidence-backed selection report with candidate comparison, trade-off analysis, risks, and references.

> Current status: MVP / portfolio project. The project is adapted from the HelloAgents deep research demo and rebuilt around AI technology stack decision workflows.

## Who It Is For

- Individual developers who need to choose a practical AI application stack before building a product.
- Small engineering teams evaluating RAG, Agent, vector database, model serving, or deployment options.
- Job-seeking developers who want a realistic AI application project that demonstrates workflow orchestration, search-augmented reasoning, streaming UX, and engineering trade-offs.

## Problem It Solves

Technology selection is often messy: information is scattered across official docs, GitHub issues, blogs, benchmarks, and personal experience. StackPilot AI structures that process.

It helps answer questions like:

- Which vector database should we use for a small RAG SaaS product?
- Should we choose LangChain, LlamaIndex, Dify, or a custom orchestration layer?
- Should our AI service use API models, Ollama, vLLM, or managed model hosting?
- Which stack is most realistic given team size, budget, deployment constraints, and timeline?

The tool does not claim to produce a perfect final answer. Its value is to generate a first decision draft that is structured, inspectable, and easy to challenge.

## Demo, Video, And Screenshots

Public demo:

- Demo URL: `TODO: add deployed frontend URL`
- API URL: `TODO: add deployed backend URL`

Demo video:

- Video: `TODO: add Bilibili / YouTube / Loom link`

Core screenshots:

- Initial full-screen intake page: `TODO: docs/assets/stackpilot-intake.png`
- Live decision workflow: `TODO: docs/assets/stackpilot-progress.png`
- Comparison matrix and rendered report: `TODO: docs/assets/stackpilot-report.png`

Recommended screenshot checklist:

- Show the full-screen input form before analysis starts.
- Show the left-side compact form and right-side live progress after analysis starts.
- Show the comparison matrix, rendered report, and source references.

## Main Features

### Structured Decision Intake

Collects project background, team size, delivery timeline, budget level, deployment mode, preferred language, existing stack, special requirements, and candidate technologies.

Problem solved: avoids shallow recommendations caused by missing context.

### Candidate Discovery

If users provide candidates, StackPilot AI normalizes them. If the candidate list is empty, it suggests a small set of likely technologies based on the decision topic.

Problem solved: users can start from either a concrete shortlist or a vague selection question.

### Evaluation Dimension Planning

Breaks the decision into practical dimensions such as development efficiency, AI integration fit, ecosystem maturity, deployment complexity, and cost/risk.

Problem solved: prevents technology selection from becoming a one-dimensional popularity comparison.

### Web Research And Evidence Collection

Uses HelloAgents `SearchTool` with configurable search backends such as DuckDuckGo, Tavily, Perplexity, Searxng, or advanced hybrid search.

Problem solved: selection reports can cite external sources instead of relying only on model memory.

### Candidate Evaluation

Evaluates every candidate under every dimension and produces summaries, pros, cons, risks, source URLs, and a coarse rating.

Problem solved: turns scattered research into comparable decision units.

### Comparison Matrix

Builds a matrix where rows are evaluation dimensions and columns are candidate technologies.

Problem solved: users can quickly scan trade-offs across multiple candidates.

### Rendered Decision Report

Generates a technology selection report with background, comparison interpretation, recommendation, alternatives, risks, open questions, and references.

Problem solved: outputs can be used as a decision memo or the first draft of an Architecture Decision Record.

### Markdown Export

Allows users to export the generated report as Markdown.

Problem solved: makes the result portable for GitHub, project docs, internal wikis, and resume demos.

## Architecture

```text
frontend Vue 3 app
  -> POST /decision/stream
  -> FastAPI backend
  -> TechSelectionAgent
     -> candidate discovery
     -> dimension planning
     -> SearchTool web retrieval
     -> LLM evaluation
     -> comparison matrix builder
     -> report exporter
  -> SSE events
  -> live progress, matrix, rendered report, references
```

## Technical Choices And Trade-Offs

### Vue 3 + TypeScript + Vite

Chosen for a lightweight, fast frontend stack with good developer experience and simple deployment as static assets.

Trade-off: the current MVP keeps the UI in a single `App.vue` to move quickly. A production version should split it into form, progress, matrix, report, and references components.

### FastAPI + Uvicorn

Chosen for a clean Python API layer, strong typing via Pydantic, and simple streaming response support.

Trade-off: the current workflow is synchronous inside the request lifecycle. A production version should move long-running jobs to a task queue or background worker.

### SSE Streaming

Chosen because technology selection is a long-running workflow and users need visible progress.

Trade-off: SSE is simpler than WebSocket for one-way progress updates, but less suitable for complex bidirectional collaboration.

### HelloAgents

Chosen to reuse LLM orchestration, tool-aware agents, search tools, and note tooling from the HelloAgents ecosystem.

Trade-off: this project inherits some framework conventions and provider requirements. The MVP adds a dedicated `TechSelectionAgent` to make the business workflow clearer.

### Search-Augmented Evaluation

Chosen to reduce hallucination risk and make recommendations traceable.

Trade-off: search quality depends on backend availability and API keys. Tavily is recommended for stable demos; DuckDuckGo is convenient but may be less reliable.

### Lightweight Markdown Rendering

Chosen to avoid adding frontend dependencies in the MVP.

Trade-off: the local renderer supports common headings, lists, links, bold text, and tables, but it is not a full Markdown parser. A production version should use a mature Markdown renderer with sanitization.

## Local Development

### Requirements

- Python 3.10+
- Node.js 16+
- npm 8+
- A usable OpenAI-compatible LLM endpoint, Ollama, or LMStudio
- Optional: Tavily / Perplexity / Searxng for better search

### Backend Setup

```powershell
cd E:\agentProjects\hello-agents\code\chapter14\helloagents-deepresearch\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
Copy-Item .env.example .env
```

Edit `backend/.env`.

OpenAI-compatible example:

```env
SEARCH_API=duckduckgo

LLM_PROVIDER=custom
LLM_MODEL_ID=your-model-name
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://your-openai-compatible-endpoint/v1

HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5174
MAX_WEB_RESEARCH_LOOPS=3
FETCH_FULL_PAGE=True
ENABLE_NOTES=True
NOTES_WORKSPACE=./notes
```

Ollama example:

```env
SEARCH_API=duckduckgo

LLM_PROVIDER=ollama
LOCAL_LLM=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434

HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5174
MAX_WEB_RESEARCH_LOOPS=3
FETCH_FULL_PAGE=True
ENABLE_NOTES=True
NOTES_WORKSPACE=./notes
```

Start backend:

```powershell
python src\main.py
```

Health check:

```text
http://localhost:8000/healthz
```

Main streaming endpoint:

```text
POST http://localhost:8000/decision/stream
```

Legacy research endpoint is still available:

```text
POST http://localhost:8000/research/stream
```

### Frontend Setup

```powershell
cd E:\agentProjects\hello-agents\code\chapter14\helloagents-deepresearch\frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5174
```

Optional frontend environment:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Validation

Backend syntax check:

```powershell
cd E:\agentProjects\hello-agents\code\chapter14\helloagents-deepresearch\backend
.\.venv\Scripts\python.exe -m py_compile src\models.py src\main.py src\tech_selection_agent.py src\services\candidate_discovery.py src\services\dimension_planner.py src\services\matrix_builder.py src\services\exporter.py src\services\search.py
```

Frontend build:

```powershell
cd E:\agentProjects\hello-agents\code\chapter14\helloagents-deepresearch\frontend
npm run build
```

## Key Pull Requests

This repository currently tracks local MVP work. Add PR links after pushing to GitHub:

- PR 1: `TODO: Introduce StackPilot AI decision workflow`
- PR 2: `TODO: Rebuild frontend as technology selection workspace`
- PR 3: `TODO: Add Docker deployment and public demo`
- PR 4: `TODO: Add report history and persistence`

## Current Limitations

- The decision workflow runs inside a single HTTP streaming request.
- No user accounts, team workspace, or permission model yet.
- No persistent database for decision history; reports can be exported as Markdown.
- Search quality depends on the configured backend and network availability.
- Ratings are coarse labels rather than statistically validated scores.
- The Markdown renderer is intentionally lightweight and not a complete Markdown engine.
- No automated browser visual regression tests yet.
- No deployed demo URL or recorded demo video has been added yet.

## Roadmap

- Add Docker Compose deployment for frontend and backend.
- Deploy a public demo and add screenshots/video to this README.
- Persist selection history and generated reports.
- Split the frontend into focused components.
- Add source credibility labels such as official docs, GitHub, blog, community, and benchmark.
- Add ADR export format.
- Add background job execution for long-running decisions.
- Add retry, timeout, and partial-result handling.
- Add Playwright checks for desktop and mobile UI.
- Add GitHub Actions for build and lint validation.

## Project Structure

```text
helloagents-deepresearch/
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── tech_selection_agent.py
│   │   ├── agent.py
│   │   ├── models.py
│   │   └── services/
│   │       ├── candidate_discovery.py
│   │       ├── dimension_planner.py
│   │       ├── matrix_builder.py
│   │       ├── exporter.py
│   │       └── search.py
│   ├── pyproject.toml
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.vue
    │   └── services/api.ts
    ├── package.json
    └── vite.config.ts
```
