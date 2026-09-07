# NoteBook 项目指引

## 项目定位

本仓库用于记录具身智能（Embodied AI）、LLM 后训练（Post-Training）、Agent 等领域的技术笔记与调研报告。

## 报告规范

### 文件格式

- 所有报告输出为 **HTML 文件**（`.html`）
- 使用 MathJax 渲染数学公式
- 页面应为自包含的单文件（内联 CSS，通过 CDN 引入 MathJax）

### 文件命名

- 技术报告/调研报告：`<topic>_report.html`（如 `opd_report.html`、`rlhf_report.html`）
- 读书笔记/论文笔记：`<topic>_notes.html`
- 文件名使用小写英文 + 下划线

### HTML 文档结构

每份报告应包含以下结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>报告标题</title>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>/* 内联样式 */</style>
</head>
<body>
    <article>
        <h1>报告标题</h1>
        <section id="question"><h2>问题（Question）</h2></section>
        <section id="background"><h2>背景与动机（Background & Motivation）</h2></section>
        <!-- 技术报告正文：按方法/主题分节 -->
        <section id="comparison"><h2>方法对比与选择建议</h2></section>
        <section id="references"><h2>参考文献（References）</h2></section>
    </article>
</body>
</html>
```

### 样式规范

- 正文字体：系统无衬线字体栈（`-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`）
- 正文字号：16px，行高 1.8
- 最大内容宽度：900px，居中显示
- 代码块：等宽字体 + 浅灰背景 + 圆角
- 表格：带边框、斑马纹行、响应式
- 配色：简洁学术风格，深色文字 + 白色背景
- 响应式设计：移动端可读

### 数学公式

- 使用 LaTeX 语法，通过 MathJax 3 渲染
- 行内公式：`\( ... \)`
- 独立公式块：`\[ ... \]` 或 `$$ ... $$`
- 重要变量首次出现时给出中英文释义

### 引用规范

- 每个方法/观点必须标注来源
- 论文引用格式：`[编号] 作者, "标题", 年份. <a href="url">链接</a>`
- 若无法确认来源，明确标注"⚠️ 未找到可靠来源"
- 优先使用：arXiv、顶会论文、官方 GitHub 仓库、官方文档

### 术语规范

- 首次出现的英文术语附中文翻译，格式：`中文（English）`
- 缩写首次出现时展开全称
- 保持全文术语一致性

### 排版规范

- `<h1>` 仅用于文档标题（每页一个）
- `<h2>` 用于主要章节
- `<h3>` 用于子章节/各方法
- `<h4>` 用于方法内部细分（如"数学形式"、"实验结果"）
- 列表使用 `<ul>` / `<ol>`，保持紧凑
- 代码块使用 `<pre><code>` 并标注语言类型
- 表格使用 `<table>` 并包含 `<thead>` 和 `<tbody>`

## 工作流程

1. 用户提出问题
2. Claude 检索论文、研究报告、本地或远端项目等来源，交叉核对
3. 若某条目找不到可靠来源，明确标注不确定性
4. 撰写符合上述规范的报告
5. 输出为本地 `.html` 文件
6. **每次写完报告后，更新 `README.md` 中的报告列表**，添加指向新 HTML 文件的相对链接

## 质量要求

- 技术细节准确，包含算法原理与数学推导
- 有效性证据基于论文实验数据，非主观判断
- 信息源可追溯，链接有效
- 报告面向有一定基础的研究者/工程师，不做过度简化
- HTML 文件可直接在浏览器中打开，公式正确渲染
- 实现需要有对应片段的证据支撑
- 设计需要有对应的伪代码与解释
- 提及到非llm/vlm领域时，需要讲解对应领域的基础概念与进阶概念
- 如果探索的项目有实际落地/部署/评估，需要阐述具体情况并附上证据

# Repository Instructions

## HTML rendering standard

The HTML artifacts in `interview_materials/vla/` are designed study and interview documents, not generic Markdown previews. All new pages and all re-renders must use the repository's academic layout described below.

### Canonical source and generated artifacts

- Treat the matching Markdown file as the canonical content source. Edit `*.md` first, then render the corresponding `*.html`.
- Keep formulas, citations, headings, tables, code, links, and question-card markup semantically identical between Markdown and HTML.
- Write the full SHA-256 of the canonical Markdown into the HTML metadata and keep the matching `*.review.json` SHA synchronized.
- Do not hand-edit generated HTML as the normal workflow. A direct HTML repair is allowed only to restore a broken artifact; then preserve or backport the fix into the rendering workflow so that the next render cannot erase it.

### Required visual template: ARIS academic v1

Use the existing `ARIS render-html (academic, v1)` design as the repository-wide HTML baseline. The following files are visual references:

- `interview_materials/vla/questions/vol_03_vla_action.html`
- `interview_materials/vla/knowledge/vol_03_vla_action.html`

Every rendered page must preserve these characteristics:

- warm paper background `#fdfcf7`, soft paper surface `#f4f1ea`, dark ink `#1a1a1a`;
- academic serif body stack: `Source Serif Pro`, `Source Serif 4`, `Crimson Pro`, `Georgia`, `Songti SC`, `STSong`, then `serif`;
- blue primary color `#1a4a8c` and rust-red accent `#b8390e`;
- desktop content width around `1280px`, with a `260px` sticky left table of contents and a readable main column;
- a compact eyebrow/subtitle area and an H1 separated by a blue double rule;
- H2 headings with a restrained bottom rule, blue H3 headings, and clear H1/H2/H3/H4 hierarchy;
- dark-blue table headers, paper-colored zebra rows, bordered academic tables;
- code blocks with Highlight.js `atom-one-light`, a blue left rule, horizontal overflow, and a monospaced font stack;
- display formulas in a dedicated `.formula` block with the same academic surface, border, padding, and horizontal overflow behavior;
- callouts or metadata blocks styled as deliberate academic notes, not default browser blockquotes;
- print rules that hide navigation and remove decorative backgrounds;
- a responsive breakpoint at approximately `900px` that collapses the page to one column, makes the TOC non-sticky, and keeps tables, code, and formulas usable on narrow screens.

Do not replace this design with the simplified white-page renderer (`Segoe UI`, centered `980px` article, blue left-bar H2 blocks, two-column in-body TOC). In particular, do not run `interview_materials/vla/tools/render_report.py` over an academic page if its current output template would wash out the ARIS layout. Upgrade or select the academic renderer/template first.

### MathJax and Markdown safety

- Use MathJax 3 and support inline `\(...\)` / `$...$` plus display `\[...\]` / `$$...$$` delimiters.
- Configure MathJax to skip `script`, `noscript`, `style`, `textarea`, `pre`, and `code` tags.
- Protect complete math spans before applying Markdown emphasis or other inline substitutions. LaTeX underscores must never be interpreted as HTML emphasis.
- Render important display equations as opaque formula blocks. For example, this must remain intact:

  ```latex
  \ell\!\left(\hat{\bar a}*{b,h,j},\\bar a*{b,h,j}\right)
  ```

- A rendered `.formula` block must contain no accidental `<em>` nodes or Markdown-generated markup inside LaTeX.

### Required render checks

Before completing any HTML creation or re-render:

1. Confirm there is exactly one H1 and a valid heading hierarchy.
2. Confirm the academic palette, serif typography, sticky desktop TOC, and `900px` responsive rule are present.
3. Confirm MathJax delimiters are balanced and representative equations compile without visible source text or parser corruption.
4. Confirm `.formula em` count is zero and LaTeX subscripts such as `_{b,h,j}` remain literal in the HTML source.
5. Confirm tables, code blocks, and formulas scroll internally rather than forcing page-wide horizontal overflow.
6. Confirm all local links and anchors resolve.
7. Confirm the embedded source SHA matches the canonical Markdown and `*.review.json`.
8. Perform browser visual QA when the environment permits it, checking both desktop and narrow layouts.

If a renderer cannot satisfy these checks, do not use it to overwrite an existing academic artifact.
