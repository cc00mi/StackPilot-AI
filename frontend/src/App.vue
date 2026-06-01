<template>
  <main :class="['app-shell', { analyzing: hasStarted }]">
    <section class="intake">
      <header class="brand">
        <span class="brand-mark">TS</span>
        <div>
          <h1>AI 应用技术栈选型智能体</h1>
          <p>把项目背景、团队约束和候选方案转成可追溯的技术决策报告。</p>
        </div>
      </header>

      <form class="decision-form" @submit.prevent="startDecision">
        <label class="field wide">
          <span>选型主题</span>
          <textarea
            v-model="form.decisionTopic"
            required
            :rows="hasStarted ? 2 : 3"
            placeholder="例如：为中小型 RAG SaaS 项目选择向量数据库"
          ></textarea>
        </label>

        <div class="form-grid">
          <label class="field">
            <span>项目类型</span>
            <input v-model="form.projectType" placeholder="AI SaaS / RAG / Agent 平台" />
          </label>
          <label class="field">
            <span>团队规模</span>
            <input v-model="form.teamSize" placeholder="3-5 人，偏 Python" />
          </label>
          <label class="field">
            <span>上线时间</span>
            <input v-model="form.timeline" placeholder="2 个月 MVP" />
          </label>
          <label class="field">
            <span>预算水平</span>
            <select v-model="form.budgetLevel">
              <option value="">未指定</option>
              <option>低</option>
              <option>中低</option>
              <option>中</option>
              <option>中高</option>
              <option>高</option>
            </select>
          </label>
          <label class="field">
            <span>部署方式</span>
            <input v-model="form.deploymentMode" placeholder="Docker / 云服务 / 私有化" />
          </label>
          <label class="field">
            <span>偏好语言</span>
            <input v-model="form.preferredLanguage" placeholder="Python / TypeScript" />
          </label>
        </div>

        <label class="field wide">
          <span>已有技术栈</span>
          <input v-model="form.existingStack" placeholder="FastAPI, PostgreSQL, Redis" />
        </label>
        <label class="field wide">
          <span>特殊要求</span>
          <input v-model="form.requirements" placeholder="低运维成本, 检索效果稳定, 文档成熟, 支持后续扩展" />
        </label>
        <label class="field wide">
          <span>候选方案</span>
          <input v-model="form.candidates" placeholder="留空则自动推荐，如 pgvector, Milvus, Weaviate" />
        </label>

        <div class="form-grid compact">
          <label class="field">
            <span>搜索引擎</span>
            <select v-model="form.searchApi">
              <option value="">沿用后端配置</option>
              <option v-for="option in searchOptions" :key="option" :value="option">
                {{ option }}
              </option>
            </select>
          </label>
          <div class="actions">
            <button class="primary" type="submit" :disabled="loading">
              {{ loading ? "分析中" : hasStarted ? "重新分析" : "开始选型分析" }}
            </button>
            <button class="ghost" type="button" :disabled="!loading" @click="cancelDecision">
              取消
            </button>
          </div>
        </div>
      </form>
    </section>

    <section class="workspace" v-if="hasStarted">
      <header class="workspace-head">
        <div>
          <span class="eyebrow">Decision Workspace</span>
          <h2>{{ form.decisionTopic }}</h2>
          <p>{{ currentStageText }}</p>
        </div>
        <button class="ghost" type="button" :disabled="!reportMarkdown" @click="downloadReport">
          导出 Markdown
        </button>
      </header>

      <p v-if="error" class="error">{{ error }}</p>

      <section class="progress-stage">
        <div class="stage-line">
          <span
            v-for="stage in stageItems"
            :key="stage.key"
            :class="['stage-dot', stage.status]"
          >
            {{ stage.label }}
          </span>
        </div>
        <div class="progress-bar">
          <span :style="{ width: `${progressPercent}%` }"></span>
        </div>
      </section>

      <section class="metrics">
        <article>
          <span>候选方案</span>
          <strong>{{ candidates.length }}</strong>
        </article>
        <article>
          <span>评估维度</span>
          <strong>{{ dimensions.length }}</strong>
        </article>
        <article>
          <span>完成评估</span>
          <strong>{{ evaluations.length }} / {{ expectedEvaluations || "-" }}</strong>
        </article>
        <article>
          <span>来源引用</span>
          <strong>{{ references.length }}</strong>
        </article>
      </section>

      <section class="live-grid">
        <article class="process-panel">
          <h3>实时进度</h3>
          <div class="live-current" :class="{ active: loading }">
            <span></span>
            <p>{{ latestProgress }}</p>
          </div>
          <ol>
            <li v-for="(log, index) in progressLogs" :key="`${log}-${index}`">
              {{ log }}
            </li>
          </ol>
        </article>

        <article class="candidates-panel">
          <h3>候选方案</h3>
          <div class="chips" v-if="candidates.length">
            <span v-for="candidate in candidates" :key="candidate.name">
              {{ candidate.name }}
            </span>
          </div>
          <p v-else class="empty">等待候选方案生成</p>
        </article>
      </section>

      <section v-if="matrix" class="band matrix-band">
        <h3>对比矩阵</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>维度</th>
                <th v-for="candidate in matrix.candidates" :key="candidate">
                  {{ candidate }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="dimension in matrix.dimensions" :key="dimension">
                <th>{{ dimension }}</th>
                <td v-for="candidate in matrix.candidates" :key="`${dimension}-${candidate}`">
                  <span :class="['rating', ratingClass(matrix.cells?.[dimension]?.[candidate])]">
                    {{ matrix.cells?.[dimension]?.[candidate] || "中" }}
                  </span>
                  <p>{{ matrix.summaries?.[dimension]?.[candidate] || "" }}</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="reportMarkdown" class="band report-band">
        <h3>技术选型报告</h3>
        <article class="rendered-report" v-html="renderedReport"></article>
      </section>

      <section v-if="evaluations.length" class="band">
        <h3>评估明细</h3>
        <div class="evaluation-grid">
          <article v-for="item in evaluations" :key="`${item.candidate_name}-${item.dimension}`">
            <div class="card-head">
              <strong>{{ item.candidate_name }}</strong>
              <span>{{ item.dimension }} · {{ item.rating }}</span>
            </div>
            <p>{{ item.summary }}</p>
          </article>
        </div>
      </section>

      <section v-if="references.length" class="band">
        <h3>来源引用</h3>
        <ul class="references">
          <li v-for="ref in references" :key="ref.url">
            <a :href="ref.url" target="_blank" rel="noopener noreferrer">
              {{ ref.title || ref.url }}
            </a>
            <span>{{ ref.domain }}</span>
          </li>
        </ul>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";

import {
  runDecisionStream,
  type ResearchStreamEvent
} from "./services/api";

interface CandidateView {
  name: string;
  category?: string;
  description?: string;
}

interface DimensionView {
  id: number;
  name: string;
  description: string;
  query_focus?: string;
}

interface EvaluationView {
  candidate_name: string;
  dimension: string;
  summary: string;
  pros: string[];
  cons: string[];
  risks: string[];
  rating: string;
  source_urls: string[];
}

interface MatrixView {
  candidates: string[];
  dimensions: string[];
  cells: Record<string, Record<string, string>>;
  summaries: Record<string, Record<string, string>>;
}

interface ReferenceView {
  title: string;
  url: string;
  domain: string;
}

const form = reactive({
  decisionTopic: "为中小型 RAG SaaS 项目选择向量数据库",
  projectType: "AI SaaS / RAG 系统",
  teamSize: "3-5 人",
  timeline: "2 个月上线 MVP",
  budgetLevel: "中低",
  deploymentMode: "Docker 云部署，后续可能私有化",
  preferredLanguage: "Python",
  existingStack: "FastAPI, PostgreSQL, Redis",
  requirements: "低运维成本, 检索效果稳定, 文档成熟, 支持后续扩展",
  candidates: "pgvector, Milvus, Weaviate, Pinecone",
  searchApi: ""
});

const searchOptions = ["advanced", "duckduckgo", "tavily", "perplexity", "searxng"];

const loading = ref(false);
const hasStarted = ref(false);
const error = ref("");
const progressLogs = ref<string[]>([]);
const candidates = ref<CandidateView[]>([]);
const dimensions = ref<DimensionView[]>([]);
const evaluations = ref<EvaluationView[]>([]);
const matrix = ref<MatrixView | null>(null);
const reportMarkdown = ref("");
const references = ref<ReferenceView[]>([]);
const currentStage = ref("idle");

let currentController: AbortController | null = null;

const expectedEvaluations = computed(() => candidates.value.length * dimensions.value.length);
const progressPercent = computed(() => {
  if (reportMarkdown.value) {
    return 100;
  }
  if (!expectedEvaluations.value) {
    return loading.value ? 12 : 0;
  }
  const base = 28;
  const evalRatio = evaluations.value.length / expectedEvaluations.value;
  return Math.min(94, Math.round(base + evalRatio * 62));
});

const latestProgress = computed(() =>
  progressLogs.value.at(-1) || "等待开始技术选型分析"
);

const currentStageText = computed(() => {
  if (loading.value) {
    return latestProgress.value;
  }
  if (reportMarkdown.value) {
    return "报告已生成，可查看矩阵、结论、风险与来源。";
  }
  return "请填写约束并开始分析。";
});

const stageItems = computed(() => [
  { key: "candidates", label: "候选", status: stageStatus("candidates") },
  { key: "dimensions", label: "维度", status: stageStatus("dimensions") },
  { key: "evaluating", label: "评估", status: stageStatus("evaluating") },
  { key: "matrix", label: "矩阵", status: stageStatus("matrix") },
  { key: "report", label: "报告", status: stageStatus("report") }
]);

const renderedReport = computed(() => renderMarkdown(reportMarkdown.value));

function stageStatus(key: string): string {
  const order = ["candidates", "dimensions", "evaluating", "matrix", "report"];
  const currentIndex = order.indexOf(currentStage.value);
  const targetIndex = order.indexOf(key);
  if (reportMarkdown.value || currentIndex > targetIndex) {
    return "done";
  }
  if (currentStage.value === key) {
    return "active";
  }
  return "pending";
}

function splitList(value: string): string[] {
  return value
    .split(/[,，;\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function resetState() {
  error.value = "";
  progressLogs.value = [];
  candidates.value = [];
  dimensions.value = [];
  evaluations.value = [];
  matrix.value = null;
  reportMarkdown.value = "";
  references.value = [];
  currentStage.value = "idle";
}

async function startDecision() {
  if (!form.decisionTopic.trim()) {
    error.value = "请输入选型主题";
    return;
  }

  if (currentController) {
    currentController.abort();
  }

  resetState();
  hasStarted.value = true;
  loading.value = true;
  currentStage.value = "candidates";
  progressLogs.value.push("开始分析项目约束与候选技术");
  const controller = new AbortController();
  currentController = controller;

  try {
    await runDecisionStream(
      {
        decision_topic: form.decisionTopic.trim(),
        project_type: form.projectType.trim(),
        team_size: form.teamSize.trim(),
        timeline: form.timeline.trim(),
        budget_level: form.budgetLevel.trim(),
        deployment_mode: form.deploymentMode.trim(),
        preferred_language: form.preferredLanguage.trim(),
        existing_stack: splitList(form.existingStack),
        requirements: splitList(form.requirements),
        candidates: splitList(form.candidates),
        search_api: form.searchApi || undefined
      },
      handleEvent,
      { signal: controller.signal }
    );
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      progressLogs.value.push("已取消当前选型分析");
    } else {
      error.value = err instanceof Error ? err.message : "选型请求失败";
    }
  } finally {
    loading.value = false;
    if (currentController === controller) {
      currentController = null;
    }
  }
}

function handleEvent(event: ResearchStreamEvent) {
  if (event.type === "status") {
    progressLogs.value.push(String(event.message || "流程状态更新"));
    return;
  }

  if (event.type === "candidates_ready") {
    candidates.value = Array.isArray(event.candidates)
      ? (event.candidates as CandidateView[])
      : [];
    currentStage.value = "dimensions";
    progressLogs.value.push(`已确定 ${candidates.value.length} 个候选方案`);
    return;
  }

  if (event.type === "dimensions_ready") {
    dimensions.value = Array.isArray(event.dimensions)
      ? (event.dimensions as DimensionView[])
      : [];
    currentStage.value = "evaluating";
    progressLogs.value.push(`已拆解 ${dimensions.value.length} 个评估维度`);
    return;
  }

  if (event.type === "candidate_evaluation") {
    const evaluation = event.evaluation as EvaluationView | undefined;
    if (evaluation) {
      evaluations.value.push(evaluation);
      progressLogs.value.push(`完成 ${evaluation.candidate_name} / ${evaluation.dimension}`);
    }
    return;
  }

  if (event.type === "comparison_matrix_ready") {
    matrix.value = event.matrix as MatrixView;
    currentStage.value = "matrix";
    progressLogs.value.push("对比矩阵已生成");
    return;
  }

  if (event.type === "decision_report_ready") {
    reportMarkdown.value = String(event.report || "");
    matrix.value = (event.matrix as MatrixView) || matrix.value;
    references.value = Array.isArray(event.references)
      ? (event.references as ReferenceView[])
      : [];
    currentStage.value = "report";
    progressLogs.value.push("技术选型报告已生成");
    return;
  }

  if (event.type === "final_report") {
    reportMarkdown.value = String(event.report || reportMarkdown.value);
    currentStage.value = "report";
    return;
  }

  if (event.type === "error") {
    error.value = String(event.detail || "选型分析失败");
  }
}

function cancelDecision() {
  if (currentController) {
    currentController.abort();
  }
}

function ratingClass(value: string | undefined): string {
  if (value === "高" || value === "中高") {
    return "rating-good";
  }
  if (value === "低" || value === "中低") {
    return "rating-risk";
  }
  return "rating-mid";
}

function downloadReport() {
  if (!reportMarkdown.value) {
    return;
  }
  const blob = new Blob([reportMarkdown.value], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "ai-tech-selection-report.md";
  link.click();
  URL.revokeObjectURL(url);
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function inlineMarkdown(value: string): string {
  return escapeHtml(value)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\[(.*?)\]\((https?:\/\/.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
}

function renderMarkdown(markdown: string): string {
  const lines = markdown.split("\n");
  const html: string[] = [];
  let inList = false;
  let inTable = false;

  const closeList = () => {
    if (inList) {
      html.push("</ul>");
      inList = false;
    }
  };
  const closeTable = () => {
    if (inTable) {
      html.push("</tbody></table>");
      inTable = false;
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      closeList();
      closeTable();
      continue;
    }
    if (/^\|(.+)\|$/.test(line)) {
      closeList();
      const cells = line.split("|").slice(1, -1).map((cell) => inlineMarkdown(cell.trim()));
      if (cells.every((cell) => /^-+$/.test(cell.replace(/<[^>]+>/g, "")))) {
        continue;
      }
      if (!inTable) {
        html.push("<table><tbody>");
        inTable = true;
      }
      html.push(`<tr>${cells.map((cell) => `<td>${cell}</td>`).join("")}</tr>`);
      continue;
    }
    closeTable();
    if (line.startsWith("### ")) {
      closeList();
      html.push(`<h4>${inlineMarkdown(line.slice(4))}</h4>`);
      continue;
    }
    if (line.startsWith("## ")) {
      closeList();
      html.push(`<h3>${inlineMarkdown(line.slice(3))}</h3>`);
      continue;
    }
    if (line.startsWith("# ")) {
      closeList();
      html.push(`<h2>${inlineMarkdown(line.slice(2))}</h2>`);
      continue;
    }
    if (/^[-*]\s+/.test(line)) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${inlineMarkdown(line.replace(/^[-*]\s+/, ""))}</li>`);
      continue;
    }
    closeList();
    html.push(`<p>${inlineMarkdown(line)}</p>`);
  }

  closeList();
  closeTable();
  return html.join("");
}
</script>

<style scoped>
:global(*) {
  box-sizing: border-box;
}

:global(body) {
  margin: 0;
  background: #eef2f0;
  color: #172033;
  font-family: "Aptos", "Segoe UI", "Microsoft YaHei", sans-serif;
}

:global(a) {
  color: #146c78;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr;
  background:
    linear-gradient(90deg, rgba(23, 50, 77, 0.06) 1px, transparent 1px),
    linear-gradient(180deg, rgba(23, 50, 77, 0.05) 1px, transparent 1px),
    #eef2f0;
  background-size: 36px 36px;
}

.app-shell.analyzing {
  grid-template-columns: 410px minmax(0, 1fr);
}

.intake {
  min-height: 100vh;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(248, 250, 252, 0.92);
  border-right: 1px solid transparent;
}

.analyzing .intake {
  justify-content: flex-start;
  padding: 28px;
  border-right-color: #d3ded9;
  overflow-y: auto;
}

.brand {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  max-width: 980px;
  margin: 0 auto 28px;
  width: 100%;
}

.analyzing .brand {
  margin-bottom: 22px;
}

.brand-mark {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #183348;
  color: white;
  font-weight: 900;
  flex: 0 0 auto;
}

h1,
h2,
h3,
h4,
p {
  margin: 0;
}

h1 {
  font-size: 42px;
  line-height: 1.12;
}

.analyzing h1 {
  font-size: 24px;
}

.brand p,
.workspace-head p {
  margin-top: 9px;
  color: #617083;
  line-height: 1.55;
}

.decision-form {
  width: min(980px, 100%);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.analyzing .form-grid {
  grid-template-columns: 1fr;
}

.form-grid.compact {
  grid-template-columns: 1fr auto;
  align-items: end;
}

.analyzing .form-grid.compact {
  grid-template-columns: 1fr;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.field span {
  color: #405166;
  font-size: 13px;
  font-weight: 800;
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid #c8d5dd;
  border-radius: 8px;
  background: white;
  color: #172033;
  padding: 12px 13px;
  font: inherit;
  outline: none;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #1f766e;
  box-shadow: 0 0 0 3px rgba(31, 118, 110, 0.14);
}

textarea {
  resize: vertical;
}

.actions {
  display: flex;
  gap: 10px;
}

button {
  border: none;
  border-radius: 8px;
  padding: 12px 16px;
  font: inherit;
  font-weight: 800;
  cursor: pointer;
  white-space: nowrap;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.primary {
  background: #1f766e;
  color: white;
}

.ghost {
  background: #e6edf0;
  color: #243246;
}

.workspace {
  min-width: 0;
  height: 100vh;
  overflow: auto;
  padding: 28px;
}

.workspace-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.eyebrow {
  display: block;
  color: #1f766e;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.workspace-head h2 {
  font-size: 28px;
  line-height: 1.2;
}

.error {
  margin-bottom: 16px;
  padding: 12px 14px;
  border-radius: 8px;
  background: #ffe8e3;
  color: #9b2f1c;
  border: 1px solid #f5c2b8;
}

.progress-stage,
.metrics article,
.band,
.process-panel,
.candidates-panel {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid #d3ded9;
  border-radius: 8px;
}

.progress-stage {
  padding: 16px;
  margin-bottom: 14px;
}

.stage-line {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}

.stage-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  border-radius: 999px;
  background: #edf1f3;
  color: #617083;
  font-size: 13px;
  font-weight: 800;
}

.stage-dot.active {
  background: #d9f0ec;
  color: #145b55;
  box-shadow: inset 0 0 0 1px rgba(31, 118, 110, 0.24);
}

.stage-dot.done {
  background: #1f766e;
  color: white;
}

.progress-bar {
  height: 10px;
  border-radius: 999px;
  background: #e4ebe8;
  overflow: hidden;
}

.progress-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #1f766e, #b3862f);
  transition: width 0.35s ease;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(130px, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.metrics article {
  padding: 15px;
}

.metrics span {
  color: #667789;
  font-size: 13px;
  font-weight: 700;
}

.metrics strong {
  display: block;
  margin-top: 7px;
  font-size: 26px;
}

.live-grid {
  display: grid;
  grid-template-columns: minmax(280px, 0.9fr) minmax(260px, 1.1fr);
  gap: 14px;
  margin-bottom: 14px;
}

.process-panel,
.candidates-panel,
.band {
  padding: 18px;
}

.process-panel h3,
.candidates-panel h3,
.band h3 {
  margin-bottom: 13px;
}

.live-current {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  background: #f0f6f4;
  color: #17324d;
  margin-bottom: 12px;
}

.live-current span {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #1f766e;
}

.live-current.active span {
  animation: blink 1.1s ease-in-out infinite;
}

.process-panel ol {
  margin: 0;
  padding-left: 20px;
  max-height: 240px;
  overflow: auto;
}

.process-panel li {
  margin-bottom: 8px;
  color: #526273;
  line-height: 1.45;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chips span {
  padding: 9px 12px;
  border-radius: 999px;
  background: #edf7f5;
  color: #145b55;
  font-weight: 800;
}

.empty {
  color: #667789;
}

.band {
  margin-bottom: 14px;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
}

th,
td {
  border-bottom: 1px solid #e1e8ef;
  padding: 13px;
  text-align: left;
  vertical-align: top;
}

thead th {
  background: #f2f6f7;
}

tbody th {
  width: 150px;
  color: #243246;
}

td p {
  margin-top: 8px;
  color: #607086;
  font-size: 13px;
  line-height: 1.5;
}

.rating {
  display: inline-flex;
  min-width: 42px;
  justify-content: center;
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 900;
}

.rating-good {
  background: #dff3e8;
  color: #12633a;
}

.rating-mid {
  background: #edf0f4;
  color: #475569;
}

.rating-risk {
  background: #fce7df;
  color: #a43d1f;
}

.rendered-report {
  background: #fbfdfc;
  border: 1px solid #d6e0dc;
  border-radius: 8px;
  padding: 22px;
  line-height: 1.72;
}

.rendered-report :deep(h2) {
  font-size: 25px;
  margin: 0 0 16px;
}

.rendered-report :deep(h3) {
  font-size: 19px;
  margin: 22px 0 10px;
  padding-top: 12px;
  border-top: 1px solid #e3ebe8;
}

.rendered-report :deep(h4) {
  font-size: 16px;
  margin: 18px 0 8px;
}

.rendered-report :deep(p) {
  margin: 8px 0;
  color: #304156;
}

.rendered-report :deep(ul) {
  margin: 8px 0 12px;
  padding-left: 20px;
}

.rendered-report :deep(li) {
  margin-bottom: 6px;
}

.rendered-report :deep(table) {
  margin: 12px 0;
  min-width: 0;
}

.evaluation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.evaluation-grid article {
  border: 1px solid #e1e8ef;
  border-radius: 8px;
  padding: 14px;
  background: #fbfdff;
}

.card-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.card-head span {
  color: #1f766e;
  font-weight: 800;
}

.evaluation-grid p {
  color: #536376;
  line-height: 1.55;
}

.references {
  margin: 0;
  padding-left: 20px;
}

.references li {
  margin-bottom: 9px;
  line-height: 1.55;
}

.references a {
  color: #146c78;
  font-weight: 800;
}

.references span {
  margin-left: 8px;
  color: #64748b;
  font-size: 13px;
}

@keyframes blink {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.35;
    transform: scale(1.5);
  }
}

@media (max-width: 1120px) {
  .app-shell.analyzing {
    grid-template-columns: 1fr;
  }

  .analyzing .intake {
    min-height: auto;
    border-right: none;
    border-bottom: 1px solid #d3ded9;
  }

  .workspace {
    height: auto;
  }
}

@media (max-width: 760px) {
  .intake,
  .analyzing .intake,
  .workspace {
    padding: 20px;
  }

  h1 {
    font-size: 28px;
  }

  .form-grid,
  .form-grid.compact,
  .metrics,
  .live-grid,
  .stage-line {
    grid-template-columns: 1fr;
  }

  .workspace-head {
    flex-direction: column;
  }
}
</style>
