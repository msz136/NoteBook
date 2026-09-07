---
title: Capstone 协议冻结：复现 Fama–French (1993) 共同风险因子
subtitle: G23 · 只冻结问题、数据、估计和成功/失败判据；执行留给 G24
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Capstone Protocol
---

# Capstone 协议冻结：复现 Fama–French (1993) 共同风险因子

## 问题（Question） {#question}

Capstone 选择 Fama 与 French 的 “Common Risk Factors in the Returns on Stocks and Bonds”（1993）作为目标论文，研究公开 MKT、SMB、HML 因子能否解释冻结测试资产在样本期内的时序收益与横截面平均收益。G23 只冻结协议，不把 P3 的部分回归结果写成复现成功。

## 目标论文与研究范围（Background & Motivation） {#background}

目标论文入口为 DOI [1]。公开数据采用 Kenneth French Data Library 的三因子文件和 25 个 Size–B/M 价值加权组合；P3 已在 2026-07-22 下载并记录两个文件 SHA，文件头均显示 `202605 CRSP database`。[2] 原始文件不提交仓库，执行时重新下载并核验哈希；若文件变化，必须新建数据版本并在差异账本中说明。

<div class="evidence"><strong>协议边界：</strong>样本目标窗口冻结为 1963-07 至 1991-12、月频、百分比转小数并减 RF。这里冻结的是复现目标和比较方式，不声称该窗口当前数据已执行、论文表格已完全重建或任何结果已成功。</div>

## 数据、版本与许可 {#data}

| 项目 | 冻结协议 |
|---|---|
| 因子 URL | `F-F_Research_Data_Factors_CSV.zip` |
| 组合 URL | `25_Portfolios_5x5_CSV.zip` |
| 因子 SHA | `80b88699a18ac408e2456d25b1004e340f3f7f8d41d5b476a0285bc53c6f0436` |
| 组合 SHA | `afc2f6c40237d07b99ab84ab9375a08bc301e3801e3ad8d91aa90d5aa9ec6295` |
| 文件头 | `202605 CRSP database` |
| 原始再分发 | 不提交；只保存 hash、派生表和下载脚本 |
| 单位 | 官方百分比除以 100 |
| 超额收益 | 组合收益减同月 RF |

## 研究问题与估计协议 {#methods}

1. 对每个测试组合估计：

\[
R_{it}-R_{ft}=\alpha_i+\beta_{Mi}MKT_t+s_iSMB_t+h_iHML_t+\varepsilon_{it}.
\]

2. 运行 Fama–MacBeth 两步法：第一步冻结时序 beta 窗口，第二步逐月横截面估 lambda，并报告时间序列均值、标准误与测试资产数量。
3. 若环境支持，运行 HAC 标准误和联合定价误差检验；若不支持，标记 `NOT RUN`，不能用平均绝对 alpha 替代。
4. 比较论文定义、当前公开文件定义、样本数量、系数符号/数量级和所有不一致原因。

## 成功与失败判据 {#criteria}

| 类型 | 判据 |
|---|---|
| 数据成功 | URL、SHA、文件头、样本行数、单位和过滤日志可重建 |
| 估计成功 | 设计矩阵、缺失、频率和风险自由利率处理通过检查 |
| 论文比较成功 | 每个比较表有来源、列映射、单位和差异原因 |
| 复现成功 | 主要方向/数量级在预先定义容忍度内且无未披露偏差 |
| 部分复现 | 数据可重建但某些表/检验/许可或底层成员不可核验 |
| 无法核验 | 关键数据、定义或执行环境不可重建 |
| 绝不通过 | 选择性报告、未来数据、未经授权原始数据再分发 |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
protocol = load_frozen_protocol()
factor_bytes, portfolio_bytes = download_and_hash(protocol.data.urls)
assert_hash_or_open_new_data_version(factor_bytes, portfolio_bytes)
factors, portfolios = parse_monthly_blocks_and_units()
sample = inner_join_and_filter(protocol.sample.start, protocol.sample.end)
time_series = fit_ols_and_log_hac(sample)
cross_section = fit_fama_macbeth(sample, frozen_beta_window)
comparison = map_outputs_to_paper_tables_and_log_deviations()
status = classify_reproduced_partial_or_not_verifiable(comparison, failures)
write_manifest_tables_and_no_raw_redistribution_artifacts()
```

## 执行前检查清单 {#checklist}

- [ ] 重新下载并核验两个 SHA；若变化，创建新版本。
- [ ] 确认 1963-07 至 1991-12 的月度行数与过滤理由。
- [ ] 确认组合是价值加权、Size–B/M 定义与论文测试资产映射。
- [ ] 确认百分比/小数、RF、缺失码、月份对齐和时区无误。
- [ ] 冻结 beta 窗口、HAC/联合检验可用性和比较容忍度。
- [ ] 记录未运行组件和任何数据许可限制。

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| G23-Q01 | 为什么选这篇论文？ | 与 P3 公开因子和当前知识栈直接衔接。 |
| G23-Q02 | G23 和 G24 区别？ | G23 冻结协议，G24 执行和答辩。 |
| G23-Q03 | 两个文件 SHA 是什么？ | 能从协议 JSON 读出完整 hash。 |
| G23-Q04 | 目标样本窗口？ | 1963-07 至 1991-12，月频。 |
| G23-Q05 | 为什么不提交 raw ZIP？ | 再分发许可边界未由下载行为证明。 |
| G23-Q06 | 复现成功标准？ | 数据/变换可重建、比较有容忍度、偏差公开。 |
| G23-Q07 | 不能运行 HAC 怎么办？ | 标记 NOT RUN，不用 alpha 均值替代。 |
| G23-Q08 | 如何处理 SHA 变化？ | 新版本、保留旧记录、记录差异。 |
| G23-Q09 | 哪些结果不能提前写？ | 复现成功、论文表格一致或 alpha 结论。 |
| G23-Q10 | G24 最小交付？ | manifest、派生表、差异账本、状态和答辩题。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| G23-Q01 | 公开数据可衔接、问题有学术基准、可做时序/横截面两步。 |
| G23-Q02 | G23 是冻结；G24 是执行、审查、答辩。 |
| G23-Q03 | 因子 `80b886...f0436`，组合 `afc2f6...c6295`，协议含完整值。 |
| G23-Q04 | 1963-07 至 1991-12。 |
| G23-Q05 | 公开访问不等于原始文件再分发授权。 |
| G23-Q06 | 数据/变换/比较可重建且不隐藏偏差。 |
| G23-Q07 | `NOT RUN` 并列出缺失，不伪造检验。 |
| G23-Q08 | 新 revision/hash，不覆盖旧版本。 |
| G23-Q09 | 任何尚未执行或未核验的结果。 |
| G23-Q10 | manifest、派生结果、差异/失败账本、复现状态、答辩材料。 |

## 风险与后续建议（Risks & Next） {#risks}

- 目标论文含债券和更复杂的测试资产定义；本协议先冻结公开股票组合可执行子集，执行时若无法映射必须标记部分复现。
- 数据库更新、组合定义变化、论文表格四舍五入和 HAC/GRS 环境差异是主要未知项。
- 下一 slice G24 执行该协议；只有执行证据完整后，才能判定 reproduced、partial 或 not-verifiable。

## 参考文献（References） {#references}

1. [1] Eugene F. Fama and Kenneth R. French, “Common Risk Factors in the Returns on Stocks and Bonds,” *Journal of Financial Economics*, 1993. [链接](https://doi.org/10.1016/0304-405X(93)90023-5)
2. [2] Kenneth R. French, “Data Library.” [链接](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
3. [3] Greg Wilson et al., “Good Enough Practices in Scientific Computing,” 2017. [链接](https://doi.org/10.1371/journal.pcbi.1005510)
