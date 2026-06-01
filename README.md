# StackPilot AI

语言：中文 | [English](./README.en.md)

StackPilot AI 是一个面向 AI 应用开发场景的技术栈选型智能体。它帮助个人开发者和小型工程团队，把模糊的技术决策问题转化为结构化、可追溯、可讨论的选型报告，包含候选方案对比、方案取舍、风险提示和来源引用。

> 当前状态：MVP / 作品集项目。项目基于 HelloAgents 深度研究示例进行二次改造，核心方向从“通用深度研究”升级为“AI 技术栈选型决策工作流”。

## 这是给谁用的？

- 准备开发 AI 应用、RAG 系统、Agent 产品或智能工作流的个人开发者。
- 需要在多个技术方案之间做取舍的小型工程团队。
- 希望展示 AI 应用工程能力、工作流编排能力和前后端交付能力的求职者。

## 解决什么问题？

技术选型经常不是“哪个技术最好”的问题，而是“哪个技术在当前约束下最合适”的问题。真实决策会受到团队经验、上线周期、部署方式、预算、生态成熟度、运维成本和后续扩展需求影响。

StackPilot AI 解决的是技术选型前期调研低效、信息分散、结论不可追溯的问题。

它可以辅助回答：

- 中小型 RAG SaaS 项目应该选 pgvector、Milvus、Weaviate 还是 Pinecone？
- Agent 框架应该选 LangChain、LlamaIndex、Dify、AutoGen 还是自研编排？
- 模型接入方案应该选 OpenAI 兼容 API、Ollama、vLLM 还是托管模型服务？
- 在团队规模、预算、部署方式和上线周期约束下，哪个技术栈更现实？

StackPilot AI 不承诺给出绝对正确的最终答案。它的价值是生成一份结构化、可验证、可继续讨论的技术决策初稿。

## Demo、视频和截图

线上 Demo：

- Demo 地址：`TODO: 添加前端部署地址`
- API 地址：`TODO: 添加后端部署地址`

演示视频：

- 视频地址：`TODO: 添加 Bilibili / YouTube / Loom 链接`

核心截图：

- 初始全屏输入页：`TODO: docs/assets/stackpilot-intake.png`
- 实时选型执行过程：`TODO: docs/assets/stackpilot-progress.png`
- 对比矩阵与报告页：`TODO: docs/assets/stackpilot-report.png`

建议截图内容：

- 展示开始分析前的全屏结构化输入表单。
- 展示开始分析后的左侧配置栏和右侧实时进度。
- 展示候选方案对比矩阵、渲染后的技术选型报告和来源引用。

## 主要功能

### 结构化决策输入

收集选型主题、项目类型、团队规模、上线时间、预算水平、部署方式、偏好语言、已有技术栈、特殊要求和候选方案。

解决的问题：避免因为上下文不足导致模型给出泛泛而谈的建议。

### 候选方案发现

如果用户提供候选方案，系统会直接标准化处理；如果候选方案为空，系统会根据选型主题自动推荐一组候选技术。

解决的问题：用户既可以从明确候选列表开始，也可以从模糊问题开始。

### 评估维度拆解

将技术选型拆解为开发效率、AI 集成友好度、生态成熟度、部署与运维复杂度、成本与风险等维度。

解决的问题：避免技术选型只比较热度或单一指标。

### 联网检索与证据收集

基于 HelloAgents `SearchTool` 调用可配置搜索后端，包括 DuckDuckGo、Tavily、Perplexity、Searxng 或高级混合搜索。

解决的问题：让选型报告具备外部资料引用，而不是只依赖模型记忆。

### 候选方案评估

针对每个候选技术和每个评估维度，生成摘要、优势、不足、风险、来源链接和粗粒度评级。

解决的问题：把分散资料转化成可比较的决策单元。

### 对比矩阵

将评估结果整理成“维度 x 候选方案”的矩阵。

解决的问题：用户可以快速横向比较不同技术方案的取舍。

### 技术选型报告

生成包含背景约束、矩阵解读、推荐方案、备选方案、风险边界、待确认问题和来源引用的报告。

解决的问题：输出可以作为技术决策备忘录，或作为 ADR（Architecture Decision Record）的初稿。

### Markdown 导出

支持将报告导出为 Markdown 文件。

解决的问题：便于沉淀到 GitHub、项目文档、团队 Wiki 或作品集说明中。

## 系统架构

```text
Vue 3 前端
  -> POST /decision/stream
  -> FastAPI 后端
  -> TechSelectionAgent
     -> 候选方案发现
     -> 评估维度规划
     -> SearchTool 联网检索
     -> LLM 候选评估
     -> 对比矩阵构建
     -> 报告生成与导出
  -> SSE 流式事件
  -> 实时进度、对比矩阵、渲染报告、来源引用
```

## 技术选型与方案取舍

### Vue 3 + TypeScript + Vite

选择原因：前端轻量、启动快、工程体验好，适合快速构建交互型 AI 工具。

方案取舍：当前 MVP 为了快速交付，主要界面集中在 `App.vue`。后续生产化版本应拆分为表单、进度、矩阵、报告和来源组件。

### FastAPI + Uvicorn

选择原因：Python 生态适合 AI 应用开发，FastAPI 对类型建模、接口开发和流式响应支持较好。

方案取舍：当前选型流程运行在一次 HTTP 流式请求中。生产化版本应引入后台任务队列或异步任务系统。

### SSE 流式响应

选择原因：技术选型是长耗时工作流，用户需要实时看到进度。

方案取舍：SSE 比 WebSocket 更简单，适合单向进度推送；如果后续做多人协作或交互式追问，可以升级为 WebSocket。

### HelloAgents

选择原因：复用 HelloAgents 的 LLM 封装、工具调用、搜索工具和智能体工作流能力。

方案取舍：项目保留 HelloAgents 能力，同时新增 `TechSelectionAgent`，让业务流程更清晰地面向技术选型场景。

### 搜索增强评估

选择原因：技术选型需要引用外部资料，降低纯模型生成带来的幻觉风险。

方案取舍：搜索质量依赖后端和 API Key。演示场景推荐使用 Tavily；DuckDuckGo 使用方便，但稳定性可能较弱。

### 轻量 Markdown 渲染

选择原因：MVP 阶段避免引入额外前端依赖。

方案取舍：当前本地渲染器支持标题、列表、链接、加粗和表格，但不是完整 Markdown 解析器。生产版本建议接入成熟 Markdown 渲染库并加入安全清洗。

## 本地运行

### 环境要求

- Python 3.10+
- Node.js 16+
- npm 8+
- 可用的 OpenAI 兼容 LLM 接口、Ollama 或 LMStudio
- 可选：Tavily / Perplexity / Searxng，用于更稳定的联网检索

### 后端启动

```powershell
cd E:\agentProjects\hello-agents\code\chapter14\helloagents-deepresearch\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
Copy-Item .env.example .env
```

编辑 `backend/.env`。

OpenAI 兼容接口示例：

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

Ollama 示例：

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

启动后端：

```powershell
python src\main.py
```

健康检查：

```text
http://localhost:8000/healthz
```

主接口：

```text
POST http://localhost:8000/decision/stream
```

兼容保留的旧接口：

```text
POST http://localhost:8000/research/stream
```

### 前端启动

```powershell
cd E:\agentProjects\hello-agents\code\chapter14\helloagents-deepresearch\frontend
npm install
npm run dev
```

访问：

```text
http://localhost:5174
```

可选前端环境变量：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 验证命令

后端语法检查：

```powershell
cd E:\agentProjects\hello-agents\code\chapter14\helloagents-deepresearch\backend
.\.venv\Scripts\python.exe -m py_compile src\models.py src\main.py src\tech_selection_agent.py src\services\candidate_discovery.py src\services\dimension_planner.py src\services\matrix_builder.py src\services\exporter.py src\services\search.py
```

前端构建：

```powershell
cd E:\agentProjects\hello-agents\code\chapter14\helloagents-deepresearch\frontend
npm run build
```

## 关键 PR

当前项目仍处于本地 MVP 阶段，推送到 GitHub 后建议补充以下 PR 链接：

- PR 1：`TODO: Introduce StackPilot AI decision workflow`
- PR 2：`TODO: Rebuild frontend as technology selection workspace`
- PR 3：`TODO: Add Docker deployment and public demo`
- PR 4：`TODO: Add report history and persistence`

## 当前限制

- 决策工作流运行在一次 HTTP 流式请求中，尚未引入后台任务队列。
- 暂无用户系统、团队空间和权限模型。
- 暂无数据库持久化历史记录，报告目前以 Markdown 导出为主。
- 搜索质量依赖配置的搜索后端和网络状态。
- 评级是粗粒度标签，不是严格统计评分。
- Markdown 渲染器是轻量实现，不是完整 Markdown 引擎。
- 尚未加入自动化浏览器视觉回归测试。
- README 中的 Demo 地址、演示视频和截图仍待补充。

## 后续计划

- 增加 Docker Compose 部署。
- 部署公开 Demo，并补充截图和演示视频。
- 增加选型历史记录和报告归档。
- 将前端拆分为独立组件。
- 增加来源可信度标签，例如官方文档、GitHub、技术博客、社区讨论、Benchmark。
- 增加 ADR 导出格式。
- 引入后台任务执行，支持长耗时选型任务恢复。
- 增加重试、超时和部分结果返回机制。
- 增加 Playwright 桌面端和移动端 UI 检查。
- 增加 GitHub Actions 构建与检查流程。

## 项目结构

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
