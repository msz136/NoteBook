---
title: P3 公开因子定价复现：French 三因子与 25 个 Size–B/M 组合
subtitle: 冻结官方 ZIP 哈希、单位和样本，并比较 CAPM 与 FF3 时序定价误差
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Public Factor Pricing Reproduction
---

# P3 公开因子定价复现：French 三因子与 25 个 Size–B/M 组合

## 问题（Question） {#question}

使用 Kenneth French Data Library 的公开因子和组合文件，CAPM 与 Fama–French 三因子模型对 25 个 Size–B/M 价值加权组合的月度时序 alpha 有何差异？如何冻结文件哈希、CRSP 数据库版本、百分比单位和原始数据再分发边界？

## 背景与动机（Background & Motivation） {#background}

Fama–French (1993) 使用市场、规模和账面市值比相关因子解释股票与债券收益的共同变化；French Data Library 发布相应因子、组合构造说明与历史文件。[1][2] 本项目在 2026-07-22 直接下载官方三因子 ZIP 和 25 组合 ZIP，内存解析月度价值加权部分，并记录完整 SHA-256。两个文件头均声明基于 `202605 CRSP database`。

<div class="evidence"><strong>证据边界：</strong>下载 URL、字节哈希、文件头、样本区间和回归统计是本地可复核证据。原始 ZIP/CSV 不提交仓库；公开可访问不自动等于可自由再分发。结果是全样本描述性复现，不是样本外策略、因果机制或未来收益证明。</div>

## 数据契约 {#concepts}

| 项目 | 冻结值 |
|---|---|
| 因子文件 | `F-F_Research_Data_Factors_CSV.zip` |
| 组合文件 | `25_Portfolios_5x5_CSV.zip` |
| 文件版本 | 文件头：使用 202605 CRSP database 创建 |
| 样本 | 1926-07 至 2026-05，共 1199 个月 |
| 测试资产 | 25 个 Size–B/M 价值加权组合 |
| 原始单位 | 百分比；解析后除以 100 转小数 |
| 超额收益 | 组合收益减同月 RF |
| 缺失值 | 官方说明的 -99.99/-999 行拒绝进入回归 |

完整哈希保存在 [`p3_factor_pricing_results.json`](p3_factor_pricing_results.json)，脚本见 [`p3_factor_pricing.py`](p3_factor_pricing.py)。

## 方法与数学形式（Methods & Mathematical Form） {#methods}

CAPM 时序回归：

\[
R_{it}-R_{ft}=\alpha_i+\beta_{Mi}(R_{Mt}-R_{ft})+\varepsilon_{it}.
\]

FF3 时序回归：

\[
R_{it}-R_{ft}=\alpha_i+\beta_{Mi}MKT_t+s_iSMB_t+h_iHML_t+\varepsilon_{it}.
\]

本项目比较 25 个组合的 \(|\hat\alpha_i|\) 横截面均值和最大值。较低平均绝对 alpha 只说明该样本和测试资产下截距较小；没有 HAC t 值、联合 GRS 检验或样本外协议时，不能把它升级为模型最终胜出。

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
factor_zip = download(FRENCH_FACTOR_URL)
portfolio_zip = download(FRENCH_25_PORTFOLIO_URL)
record_sha256_and_file_header(factor_zip, portfolio_zip)
factors = parse_monthly_percent_to_decimal(factor_zip)
portfolios = parse_value_weighted_monthly(portfolio_zip)
dates = strict_inner_join(factors, portfolios)
excess = portfolios - factors["RF"]
capm = regress_each_asset(excess, factors[["Mkt-RF"]])
ff3 = regress_each_asset(excess, factors[["Mkt-RF", "SMB", "HML"]])
report_alphas_without_redistributing_raw_files(capm, ff3)
```

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/projects/p3_factor_pricing/p3_factor_pricing.py
python quant_finance/projects/p3_factor_pricing/test_p3_factor_pricing.py -v
```

| 指标 | CAPM | FF3 |
|---|---:|---:|
| 25 组合平均绝对月度 alpha | 0.001535 | 0.001123 |
| FF3 最大绝对月度 alpha | — | 0.006685 |

FF3 的平均绝对 alpha 比 CAPM 低，但仍存在非零定价误差。测试验证月度解析器、25 个组合、1199 个月、两个 64 位十六进制 SHA，以及 FF3 平均绝对 alpha 小于 CAPM。网络文件可能更新，因此未来重跑若哈希变化应生成新版本记录，而非静默覆盖本结果。

## 复现边界与失败案例 {#comparison}

| 失败 | 影响 | 防护 |
|---|---|---|
| 百分比未除 100 | 系数/alpha 放大 100 倍 | 单位断言与手算首行 |
| 未减 RF | 混淆总收益与超额收益 | 同月 RF 显式相减 |
| 解析到年度区块 | 频率和样本数错误 | 在首个月度空行终止 |
| 文件更新无记录 | 结果不可重建 | URL、文件头与 SHA-256 |
| 提交原始 CRSP 派生 CSV | 再分发边界不清 | 只保存派生统计和下载脚本 |
| 全样本拟合称样本外 | 夸大预测能力 | 明确本项目是描述性复现 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| P3-Q01 | 两个官方文件是什么？ | 三因子与 25 个 Size–B/M 组合 ZIP。 |
| P3-Q02 | 原始单位如何处理？ | 百分比除以 100。 |
| P3-Q03 | 组合超额收益怎么构造？ | 同月组合收益减 RF。 |
| P3-Q04 | SHA 为什么重要？ | 文件更新后仍能识别复现版本。 |
| P3-Q05 | FF3 alpha 更小证明什么？ | 只说明该样本/资产下时序截距更小。 |
| P3-Q06 | 为什么不提交原始 ZIP？ | 公开访问不等于再分发授权。 |
| P3-Q07 | 如何避免解析年度表？ | 在月度区块首个空行终止。 |
| P3-Q08 | 还缺哪些正式检验？ | HAC t 值、联合 GRS、稳健样本期。 |
| P3-Q09 | 公开因子能替代 CRSP 点时个股吗？ | 不能，无法重建底层成员和退市处理。 |
| P3-Q10 | 本结果是否可交易？ | 不能，没有样本外、成本和执行协议。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| P3-Q01 | `F-F_Research_Data_Factors_CSV.zip` 与 `25_Portfolios_5x5_CSV.zip`。 |
| P3-Q02 | 所有收益/因子百分数转换成小数。 |
| P3-Q03 | \(R_i^e=R_i-R_f\)。 |
| P3-Q04 | 哈希把统计结果绑定到确切字节版本。 |
| P3-Q05 | 仅支持全样本描述性拟合改善。 |
| P3-Q06 | 许可/再分发权尚未被下载行为证明。 |
| P3-Q07 | 识别月度表头并在空行停止。 |
| P3-Q08 | HAC、GRS、子样本和样本外。 |
| P3-Q09 | 公开组合无法替代底层点时证券数据库。 |
| P3-Q10 | 缺少可交易信号、成本、容量和执行证据。 |

## 风险与后续建议（Risks & Next） {#risks}

- 官方文件会随数据库更新；本结果只对应已记录的 202605 CRSP 文件头和两个 SHA。
- 未实现 GRS 联合检验、Shanken 修正、Fama–MacBeth 横截面第二步或多模型比较；这些不能由平均绝对 alpha 替代。
- 下一 slice G13/M07 将进入固定收益、衍生品与随机过程，包括债券曲线、Black–Scholes、风险中性定价和数值对冲误差。

## 参考文献（References） {#references}

1. [1] Eugene F. Fama and Kenneth R. French, “Common Risk Factors in the Returns on Stocks and Bonds,” *Journal of Financial Economics*, 1993. [链接](https://doi.org/10.1016/0304-405X(93)90023-5)
2. [2] Kenneth R. French, “Data Library.” [链接](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
3. [3] William F. Sharpe, “Capital Asset Prices,” *Journal of Finance*, 1964. [链接](https://doi.org/10.1111/j.1540-6261.1964.tb02865.x)
