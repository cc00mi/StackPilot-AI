# StackPilot AI

> 面向 AI 应用开发的技术栈选型智能体：输入项目背景、约束和候选方案，自动完成资料检索、评估维度拆解、对比矩阵生成与技术选型报告输出。

[English](./README.en.md) · [项目进度文档](./PROJECT_PROGRESS.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![Vue](https://img.shields.io/badge/Vue%203-Frontend-42B883?logo=vuedotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-UI-3178C6?logo=typescript&logoColor=white)
![SSE](https://img.shields.io/badge/Streaming-SSE-f59e0b)

## 项目简介

StackPilot AI 是一个用于辅助 AI 应用技术栈选型的智能体工作台。它面向 RAG、Agent、AI SaaS、企业知识库、智能工作流等开发场景，将“该选哪套技术方案”这类模糊问题，转化为结构化、可追溯、可讨论的技术决策报告。

传统技术选型往往依赖碎片化搜索、个人经验和零散笔记。StackPilot AI 将选型流程拆成可执行的智能体工作流：理解项目背景、识别候选方案、规划评估维度、联网检索资料、生成对比矩阵、输出推荐结论与风险提示。它不是替代架构师做最终决策，而是帮助团队更快得到一份有证据、有边界、有讨论价值的选型初稿。

## 适用场景

- 个人开发者准备启动 AI 应用，希望快速比较模型服务、向量数据库、Agent 框架、部署方案等技术路线。
- 小型团队需要在上线周期、预算、人力、部署环境和维护成本之间做现实取舍。
- 技术负责人希望把技术调研过程沉淀为可复盘的 ADR 或项目决策文档。
- 求职作品集需要展示完整的 AI 应用工程能力，包括智能体编排、联网检索、流式输出、前后端集成和工程部署。

## 核心能力

| 能力 | 解决的问题 |
| --- | --- |
| 结构化需求输入 | 收集项目类型、团队规模、预算、部署方式、上线周期、已有技术栈等上下文，减少泛泛而谈的回答。 |
| 候选方案发现 | 用户可以手动输入候选技术，也可以让系统根据主题自动补全候选方案。 |
| 评估维度拆解 | 自动生成适合当前项目的评估维度，例如开发效率、生态成熟度、AI 集成能力、成本、运维复杂度和风险。 |
| 联网资料检索 | 基于搜索工具获取候选技术资料，为报告提供来源引用，降低纯模型生成的幻觉风险。 |
| 对比矩阵生成 | 将候选方案按维度横向比较，帮助用户快速看清方案差异。 |
| 推荐与风险提示 | 输出主推荐、备选方案、适用边界、关键风险和待确认问题。 |
| 报告导出 | 将技术选型结果导出为 Markdown，便于进入项目文档、Wiki、PR 或 ADR 流程。 |

## 工作流

```text
用户输入项目背景、约束和候选方案
        ↓
TechSelectionAgent 拆解选型任务
        ↓
候选方案发现 + 评估维度规划
        ↓
联网检索候选技术资料
        ↓
按维度评估候选方案
        ↓
生成对比矩阵、推荐结论、风险提示和来源引用
        ↓
前端实时展示进度并渲染技术选型报告
```

## 技术架构

```text
frontend/
  Vue 3 + TypeScript + Vite
  - 全屏选型输入页
  - SSE 实时进度展示
  - 对比矩阵与报告渲染

backend/
  FastAPI + HelloAgents
  - /decision/stream 流式选型接口
  - TechSelectionAgent 业务智能体
  - SearchTool 联网检索
  - 报告导出与结果结构化
```

后端核心调用链：

```text
FastAPI /decision/stream
  -> TechSelectionAgent.run()
  -> CandidateDiscoveryService
  -> DimensionPlannerService
  -> SearchTool
  -> MatrixBuilderService
  -> ReportExporter
  -> SSE events
```

## 技术选型说明

| 模块 | 技术 | 选择原因 |
| --- | --- | --- |
| 前端 | Vue 3 + TypeScript + Vite | 轻量、启动快、适合快速构建交互型 AI 工作台。 |
| 后端 | FastAPI + Uvicorn | Python AI 生态友好，类型建模和流式响应实现清晰。 |
| 智能体 | HelloAgents + 自定义 TechSelectionAgent | 复用 LLM、工具调用和搜索能力，同时将业务流程聚焦到技术选型。 |
| 实时通信 | Server-Sent Events | 选型任务是单向长流程，SSE 比 WebSocket 更简单、更适合实时进度推送。 |
| 检索增强 | DuckDuckGo / Tavily / Perplexity / Searxng | 通过外部资料增强报告可信度，并保留可配置搜索后端。 |
| 报告格式 | Markdown | 易于保存到 GitHub、Wiki、PR、ADR 和作品集文档。 |

## 快速开始

### 1. 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
Copy-Item .env.example .env
python src\main.py
```

后端默认运行在：

```text
http://localhost:8000
```

健康检查：

```text
GET http://localhost:8000/healthz
```

### 2. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

前端默认运行在：

```text
http://localhost:5174
```

### 3. 配置环境变量

后端配置文件位于 `backend/.env`。OpenAI 兼容接口示例：

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

前端可选配置：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 项目结构

```text
helloagents-deepresearch/
├── backend/
│   ├── src/
│   │   ├── main.py                    # FastAPI 入口与流式接口
│   │   ├── tech_selection_agent.py    # 技术选型智能体主流程
│   │   ├── models.py                  # 请求、事件和报告数据模型
│   │   └── services/
│   │       ├── candidate_discovery.py # 候选方案发现
│   │       ├── dimension_planner.py   # 评估维度规划
│   │       ├── matrix_builder.py      # 对比矩阵生成
│   │       ├── exporter.py            # 报告导出
│   │       └── search.py              # 联网检索封装
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.vue                    # 主页面与报告渲染
│   │   └── services/api.ts            # SSE 接口调用
│   └── package.json
├── README.md                          # 对外项目介绍
├── README.en.md                       # 英文说明
└── PROJECT_PROGRESS.md                # 项目进度与内部备忘录
```

## 截图与演示

当前仓库预留以下展示位，适合在部署后补充到 GitHub 首页：

| 类型 | 链接 |
| --- | --- |
| 在线 Demo | TODO |
| 演示视频 | TODO |
| 初始输入页截图 | TODO |
| 实时进度截图 | TODO |
| 技术选型报告截图 | TODO |

## 验证命令

后端语法检查：

```powershell
cd backend
.\.venv\Scripts\python.exe -m py_compile src\models.py src\main.py src\tech_selection_agent.py src\services\candidate_discovery.py src\services\dimension_planner.py src\services\matrix_builder.py src\services\exporter.py src\services\search.py
```

前端构建：

```powershell
cd frontend
npm run build
```

## 当前状态

项目处于 MVP 阶段，已完成从通用深度研究示例到 AI 技术栈选型智能体的核心改造：

- 已支持结构化选型输入、候选方案发现、评估维度规划、联网检索、对比矩阵和报告生成。
- 已支持 SSE 实时进度事件，前端可边执行边展示当前阶段。
- 已重构主页面体验，初始页全屏展示，分析开始后切换为侧栏配置 + 右侧报告工作台。
- 已支持将技术选型报告直接渲染到页面，并保留 Markdown 导出能力。

## Roadmap

- 增加 Docker Compose 一键部署。
- 部署公开 Demo，补充截图和演示视频。
- 增加报告历史记录、项目空间和持久化存储。
- 支持 ADR、PDF、HTML 等更多报告导出格式。
- 引入来源可信度标签，例如官方文档、GitHub、Benchmark、社区讨论和技术博客。
- 增加后台任务队列，支持长耗时任务恢复、重试和部分结果返回。
- 拆分前端组件，补充 Playwright UI 测试和 GitHub Actions。
- 支持企业内部知识库和私有技术标准作为选型约束。

## 项目来源

本项目基于 HelloAgents 深度研究示例进行二次开发，核心目标从“通用主题研究”调整为“AI 应用技术栈选型”。改造重点包括业务智能体流程、结构化数据模型、联网评估链路、实时进度展示和面向作品集/企业实践的前端体验。

## 当前限制

- 选型结果用于辅助决策，不应替代真实架构评审、PoC 压测和安全合规审查。
- 搜索质量依赖所配置的搜索后端、网络环境和 API Key。
- 当前报告评分为粗粒度评价，不是严格量化 Benchmark。
- MVP 尚未加入数据库、用户系统、团队协作和权限模型。
- Markdown 渲染为轻量实现，生产环境建议引入成熟渲染器并做安全清洗。

## License

当前仓库尚未声明开源许可证。如需对外开放复用，建议补充 `LICENSE` 文件。
