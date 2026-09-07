---
title: Capstone 执行与答辩材料：Fama–French (1993) 部分复现
subtitle: G24 · 数据哈希与冻结样本通过；论文表格、HAC 与 GRS 保持未运行披露
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Capstone Execution
---

# Capstone 执行与答辩材料：Fama–French (1993) 部分复现

## 问题（Question） {#question}

按 G23 冻结协议重新下载两个 Kenneth French 官方文件，检查 SHA 和 1963-07 至 1991-12 样本，执行 25 个 Size–B/M 组合的三因子时序回归和 Fama–MacBeth 横截面回归，并对未完成的论文表格、HAC 与 GRS 逐项披露。最终状态只能在证据支持的 `reproduced`、`partial_reproduction` 或 `not_verifiable` 中选择。

## 执行状态与证据边界（Background & Motivation） {#background}

执行脚本重新访问两个官方 URL，哈希与 G23 协议完全一致；样本为 342 个月、25 个组合。时序 OLS 与 Fama–MacBeth 已运行，`statsmodels` 不可用，因此 HAC 标准误、GRS 联合检验和论文原表机器映射保持 `NOT_RUN`。[1][2]

<div class="evidence"><strong>结论边界：</strong>本 Capstone 状态为 <code>partial_reproduction</code>。这证明数据版本、样本过滤和两类回归路径已执行，不证明论文表格完全重建、数值等价、因果机制或可交易 alpha。</div>

## 数据核验 {#data}

| 项目 | 执行结果 |
|---|---|
| 因子 SHA | `80b88699a18ac408e2456d25b1004e340f3f7f8d41d5b476a0285bc53c6f0436`，match |
| 组合 SHA | `afc2f6c40237d07b99ab84ab9375a08bc301e3801e3ad8d91aa90d5aa9ec6295`，match |
| 样本起点 | 1963-07 |
| 样本终点 | 1991-12 |
| 月数 | 342 |
| 测试资产 | 25 |
| 单位 | 百分比转小数，减同月 RF |
| 原始文件 | 未提交，仅保留 hash/派生结果 |

## 估计结果 {#methods}

时序模型：

\[
R_{it}-R_{ft}=\alpha_i+\beta_{Mi}MKT_t+s_iSMB_t+h_iHML_t+\varepsilon_{it}.
\]

| 指标 | 结果 |
|---|---:|
| 平均绝对 alpha | 0.0009369（月度小数） |
| 最大绝对 alpha | 0.0036881 |
| 平均市场 beta | 1.0157 |
| 平均 SMB beta | 0.5584 |
| 平均 HML beta | 0.2174 |

Fama–MacBeth 平均 lambda：

| 因子 | 平均 lambda | 逐月标准差 |
|---|---:|---:|
| MKT | -0.001546 | 0.08175 |
| SMB | 0.002003 | 0.02911 |
| HML | 0.004254 | 0.02594 |

逐月 lambda 的标准差不是 HAC 标准误，不能直接作显著性结论。

## 差异与失败账本 {#difference}

| 项目 | 状态 | 原因/下一步 |
|---|---|---|
| 原论文表格机器数字化 | NOT_RUN | 未在本 slice 提取论文表格，不能做逐格差异 |
| GRS 联合定价误差检验 | NOT_RUN | 实现未冻结，环境缺统计包 |
| HAC 标准误 | NOT_RUN | `statsmodels` 不可用；只保留 lambda 标准差 |
| 数据 hash/样本过滤 | PASS | 与协议一致，342×25 |
| 时序 OLS | PASS | 设计矩阵和结果已生成 |
| Fama–MacBeth | PASS | 逐月横截面和均值已生成 |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
factor_bytes, portfolio_bytes = download_and_hash(protocol_urls)
assert_hashes_match_or_open_new_version()
factors, portfolios = parse_monthly_blocks()
sample = align_and_filter("196307", "199112", subtract_rf=True)
time_series = fit_ff3_ols(sample)
fmb = fit_monthly_cross_sections(time_series.betas)
ledger = record_passes_and_NOT_RUN_components()
status = "partial_reproduction" if ledger.has_unrun_items() else "reproduced"
```

实现见 [`execute_capstone.py`](execute_capstone.py)，机器结果见 [`capstone_execution_results.json`](capstone_execution_results.json)，冻结协议见 [`capstone_protocol.json`](capstone_protocol.json)。

## 答辩问题与答案边界 {#exercises}

| ID | 问题 | 答案边界 |
|---|---|---|
| G24-Q01 | 为什么不是 reproduced？ | 论文表格、HAC、GRS 未运行。 |
| G24-Q02 | 两个 hash 是否匹配？ | 是，与 G23 完全一致。 |
| G24-Q03 | 样本多少？ | 342 月、25 组合。 |
| G24-Q04 | 平均绝对 alpha 是多少？ | 0.0009369 月度小数。 |
| G24-Q05 | Fama–MacBeth lambda 能直接显著吗？ | 不能，当前只有逐月标准差，HAC NOT_RUN。 |
| G24-Q06 | 为什么不提交 raw？ | 公开下载不等于再分发许可。 |
| G24-Q07 | 结果能否证明论文错？ | 不能，定义/表格/检验尚未完全对齐。 |
| G24-Q08 | partial reproduction 含义？ | 数据和部分估计执行，关键组件未完成。 |
| G24-Q09 | 下一步优先级？ | HAC、GRS、原表数字化与差异映射。 |
| G24-Q10 | 能否作为投资策略？ | 不能，没有样本外、成本、容量和执行证据。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| G24-Q01 | 三项关键差异账本仍为 NOT_RUN。 |
| G24-Q02 | factor/portfolio SHA 均 match。 |
| G24-Q03 | 1963-07—1991-12 共 342 月、25 组合。 |
| G24-Q04 | `0.0009368909703585307`。 |
| G24-Q05 | 不能；标准差不等于 HAC SE。 |
| G24-Q06 | 只存 hash 和派生结果。 |
| G24-Q07 | 未完成定义、检验和表格映射。 |
| G24-Q08 | 可复现子集通过，完整论文复现未完成。 |
| G24-Q09 | 先完成论文表格、HAC、GRS，再补稳健性。 |
| G24-Q10 | 不能，研究证据不等于交易部署。 |

## 风险与后续建议（Risks & Next） {#risks}

- 目标论文还涉及债券因子和更完整测试资产，本执行只覆盖协议明确的公开股票组合子集。
- 当前环境缺 `statsmodels`，HAC/GRS 不应通过手写近似冒充已完成。
- Capstone 的可辩护结论是“部分复现”；若后续补齐未运行组件，需新建 revision、重新生成结果和审查，不覆盖本次记录。

## 参考文献（References） {#references}

1. [1] Eugene F. Fama and Kenneth R. French, “Common Risk Factors in the Returns on Stocks and Bonds,” *Journal of Financial Economics*, 1993. [链接](https://doi.org/10.1016/0304-405X(93)90023-5)
2. [2] Kenneth R. French, “Data Library.” [链接](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
