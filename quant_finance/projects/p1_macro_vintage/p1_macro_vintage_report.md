---
title: P1 宏观实时数据实验：FRED/ALFRED Vintage 泄漏对照
subtitle: 用发布日期筛选历史信息集，而不是把最终修订值回填到过去
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Macro Vintage Experiment
---

# P1 宏观实时数据实验：FRED/ALFRED Vintage 泄漏对照

## 问题（Question） {#question}

如果同一个宏观观测在首次发布后被修订，十年前的回测应该看到哪个数值？本项目构造一个小型、可再分发的 vintage fixture，比较 2024-06-30 研究快照与最终修订快照，验证 point-in-time 选择规则和泄漏证据。

## 背景与动机（Background & Motivation） {#background}

FRED 提供官方宏观序列 API，ALFRED 面向 vintage/realtime period 访问历史版本。[1][2] 普通下载得到的最新值适合描述当前数据库状态，但不自动等于过去研究者当时可见的信息。M02 已冻结 `available_at <= asof_at` 契约；P1 将它具体化为对每个 `series_id, observation_date` 选择快照前最新发布版本。

<div class="evidence"><strong>证据边界：</strong>本地 fixture、脚本和结果是 local-evidence；FRED/ALFRED 链接支持官方入口和 vintage 研究方向。由于当前环境不直接下载真实 ALFRED 数据，本报告不声称复现任何真实 GDP 或交易策略表现。</div>

## 概念与数据契约 {#concepts}

| 字段 | 语义 | 约束 |
|---|---|---|
| `series_id` | 官方序列标识 | 不用展示名称代替稳定 ID |
| `observation_date` | 经济观测所属期间 | 不等于发布日期 |
| `release_at` | 该版本首次可被研究者看到的时间 | point-in-time 过滤依据 |
| `vintage_at` | 数据库快照/版本时间 | 需与来源文档一致 |
| `value` | 该版本的数值 | 同期可有多次修订 |
| `asof_at` | 回测或研究重放的快照时间 | 只选择 `release_at <= asof_at` |

## 方法与数学形式（Methods & Mathematical Form） {#methods}

对序列和观测期 \(o\)，研究快照 \(a\) 的可见版本为：

\[
r^*(o,a)=\arg\max_{r:\;release\_at(r)\le a,\;observation\_date(r)=o} release\_at(r).
\]

若直接使用最终版本 \(r^*(o,\infty)\)，则对历史快照的泄漏量为：

\[
\Delta(o,a)=value\big(r^*(o,\infty)\big)-value\big(r^*(o,a)\big).
\]

非零 \(\Delta\) 证明最终修订值不能无条件回填到过去；它不证明任何模型一定盈利或修订一定有方向性。

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
rows = load_vintage_rows(source_version)
assert_schema(rows, ["series_id", "observation_date", "release_at", "vintage_at", "value"])
visible = [r for r in rows if r.release_at <= asof_at]
snapshot = latest_by(visible, keys=["series_id", "observation_date"], order="release_at")
final = latest_by(rows, keys=["series_id", "observation_date"], order="release_at")
revision_delta = compare(snapshot, final)
write_hash_and_dropped_rows(snapshot, revision_delta)
```

实现见 [`audit_macro_vintage.py`](audit_macro_vintage.py)，fixture 见 [`p1_macro_vintage_fixture.csv`](p1_macro_vintage_fixture.csv)，结果见 [`p1_macro_vintage_results.json`](p1_macro_vintage_results.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/projects/p1_macro_vintage/audit_macro_vintage.py
python quant_finance/projects/p1_macro_vintage/test_audit_macro_vintage.py -v
```

截至 2024-02-28，fixture 中只有首段观测已发布；最终快照包含三段观测。共同观测的最终修订差异非零，审计器报告 `leakage_detected=true`。测试还确认未来发布日期不会进入历史快照。

## 对照与失败案例 {#comparison}

| 做法 | 历史快照结果 | 结论 |
|---|---|---|
| `release_at <= asof_at` 后取最新 | 只看到当时已发布版本 | 可用于实时重放 |
| 直接取数据库当前最终值 | 包含未来修订 | 产生 vintage leakage |
| 只按 `observation_date` join | 无法表达发布日期 | 不是 point-in-time join |
| 只保存最终 CSV | 无法重建当时信息集 | 研究不可审计 |

## 实践任务与答案边界 {#exercises}

| ID | 任务 | 达标标准 |
|---|---|---|
| P1-Q01 | 定义 observation、release、vintage、asof。 | 能区分经济期间与信息可见时间。 |
| P1-Q02 | 写出 point-in-time 选择规则。 | `release_at <= asof_at` 且按观测期取最新。 |
| P1-Q03 | 为什么最终修订值会泄漏？ | 因为发布日期晚于回测快照。 |
| P1-Q04 | 如何证明 fixture 存在修订？ | 同一观测期多版本且 value 不同。 |
| P1-Q05 | FRED 与 ALFRED 在本实验中分别扮演什么角色？ | FRED 是序列入口，ALFRED 是 vintage 语义入口。 |
| P1-Q06 | 只按 observation_date join 有何问题？ | 丢失发布日期约束。 |
| P1-Q07 | 为什么保留 source_version？ | 可重放下载和变换。 |
| P1-Q08 | 如何测试未来版本过滤？ | 注入晚于 asof 的版本并断言不可见。 |
| P1-Q09 | 修订差异能否直接转成交易信号？ | 不能，需定义发布时间、交易延迟和成本。 |
| P1-Q10 | 何时可以使用最终值？ | 描述当前历史或明确不模拟实时信息集时。 |

## 风险与后续建议（Risks & Next） {#risks}

- 本项目使用合成 fixture，未对真实 ALFRED API 字段、速率限制和许可作新的成功核验。
- 宏观发布往往有时区、初值、修订、缺失和多频率对齐问题；生产管线需记录下载时间、请求参数、响应哈希和许可证。
- 下一 slice G09/P2 将把严格时间切分应用到 EWMA/GARCH 波动率预测，并比较 QLIKE 与成本边界。

## 参考文献（References） {#references}

1. [1] Federal Reserve Bank of St. Louis, “FRED API.” [链接](https://fred.stlouisfed.org/docs/api/fred/)
2. [2] Federal Reserve Bank of St. Louis, “ALFRED.” [链接](https://alfred.stlouisfed.org/)
3. [3] Bruce E. Hansen, “Econometrics.” [链接](https://www.ssc.wisc.edu/~bhansen/econometrics/)

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| P1-Q01 | 观测期描述经济发生时间，release/vintage 描述信息版本，asof 是研究快照。 |
| P1-Q02 | 先过滤 `release_at <= asof_at`，再按观测期取发布日期最新版本。 |
| P1-Q03 | 最终值可能在回测时尚未发布。 |
| P1-Q04 | 同一观测期有多个版本且数值变化。 |
| P1-Q05 | FRED 提供序列/API 入口，ALFRED 表达 realtime/vintage 访问。 |
| P1-Q06 | join 没有信息集条件，无法防止未来版本进入。 |
| P1-Q07 | 记录版本才能重建相同输入。 |
| P1-Q08 | 构造未来 `release_at`，断言 visible snapshot 不含它。 |
| P1-Q09 | 还需交易时延、成本和策略定义。 |
| P1-Q10 | 仅在研究目标明确允许最终修订时。 |
