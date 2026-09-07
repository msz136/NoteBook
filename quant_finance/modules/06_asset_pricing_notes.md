---
title: 资产定价：CAPM、SDF、因子模型与 Fama–MacBeth
subtitle: M06 · 把平均收益、因子暴露、风险价格和定价误差分开检验
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Asset Pricing
---

# 资产定价：CAPM、SDF、因子模型与 Fama–MacBeth

## 问题（Question） {#question}

一项因子为什么既需要解释时间序列收益，也需要解释横截面平均收益？CAPM、随机贴现因子（SDF）、Fama–French 因子与 Fama–MacBeth 回归如何对应？本模块用已知真值的合成三因子系统验证 beta、alpha 和风险价格估计，并明确“定价误差小”不等于“可交易 alpha”。

## 背景与动机（Background & Motivation） {#background}

Sharpe 的 CAPM 将期望超额收益与市场 beta 联系起来；Fama 与 French 扩展了经验因子模型；Fama–MacBeth 提供逐期横截面风险价格估计与时间序列推断。[1–3] SDF 形式把无套利定价统一写为贴现后收益矩条件。Kenneth French Data Library 提供公开因子和投资组合文件，是后续 P3 复现入口，但不能替代底层点时个股和退市数据审计。[4]

<div class="evidence"><strong>证据边界：</strong>理论与方法来自原始文献及官方数据入口；本地合成实验只验证两步回归、定价误差和有限样本波动。报告不声称真实因子溢价、策略收益或因果机制。</div>

## 基础概念与术语 {#concepts}

| 概念 | 定义 | 常见误读 |
|---|---|---|
| 超额收益 | 资产收益减无风险收益 | 原始价格收益不等于超额总收益 |
| beta | 收益对因子的条件协动/回归载荷 | beta 大不自动代表 alpha 高 |
| 风险价格 \(\lambda\) | 单位因子暴露对应的横截面期望收益 | 样本因子均值会有大波动 |
| alpha | 因子模型不能解释的平均收益截距 | 显著 alpha 不自动可交易 |
| SDF | 将未来收益折现到当前价格的随机变量 | 统计 SDF 不自动等于结构偏好模型 |
| 定价误差 | 模型预测期望收益与实际平均收益差 | 小误差可能来自弱检验资产 |

## 方法与数学形式（Methods & Mathematical Form） {#methods}

### CAPM 与多因子时序回归 {#factor-model}

CAPM 的期望收益关系：

\[
E[R_i^e]=\beta_i E[R_M^e],\qquad
\beta_i=\frac{Cov(R_i^e,R_M^e)}{Var(R_M^e)}.
\]

多因子时间序列回归：

\[
R_{it}^e=\alpha_i+\beta_i'f_t+\varepsilon_{it}.
\]

若因子完全定价测试资产，\(\alpha_i\) 应接近零；联合检验比逐个挑选显著 alpha 更符合模型检验，但仍受测试资产、样本期和协方差估计影响。

### SDF 与 GMM {#sdf}

无套利定价矩条件：

\[
E[m_{t+1}R_{i,t+1}]=1,
\qquad E[m_{t+1}R_{i,t+1}^e]=0.
\]

线性 SDF 可写为 \(m=a-b'f\)，并用 GMM 估计矩条件。检验需报告矩条件、权重矩阵、Hansen–Jagannathan 距离或其他定价误差度量；不能仅凭高横截面 \(R^2\) 宣布模型正确。

### Fama–MacBeth 两步法 {#fmb}

第一步按资产估计时序 beta；第二步每期做横截面回归：

\[
R_{it}^e=\lambda_{0t}+\hat\beta_i'\lambda_t+u_{it},
\qquad \hat\lambda=\frac1T\sum_{t=1}^T\hat\lambda_t.
\]

标准误来自 \(\hat\lambda_t\) 的时间序列，存在自相关时需 HAC；第一步 beta 估计误差、弱横截面分散和时间变动暴露会影响推断。

## 数据与检验契约 {#math}

| 项目 | 必须记录 |
|---|---|
| 收益口径 | 总收益/价格收益、无风险利率、频率与单位 |
| 因子版本 | French 文件名称、下载日期、档案版本和百分比/小数 |
| 测试资产 | 组合构造、再平衡、退市、微盘与点时成员 |
| 时序估计 | 样本窗、alpha/beta、HAC/联合检验 |
| 横截面估计 | beta 来源、每期样本、lambda 序列与标准误 |
| 经济边界 | 成本、换手、容量、可交易性和数据许可 |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
returns, factors = load_point_in_time_total_returns_and_factors(asof_at)
assert_frequency_units_and_calendar_match(returns, factors)
betas, alphas = time_series_regressions(returns, factors)
lambda_t = [cross_sectional_regression(returns[t], betas) for t in dates]
lambda_mean, lambda_se = time_series_mean_and_hac(lambda_t)
pricing_errors = evaluate_alphas_and_sdf_moments(alphas, returns, factors)
report_test_assets_versions_costs_and_failure_cases()
```

可执行合成实验见 [`m06_asset_pricing.py`](../tools/m06_asset_pricing.py)，结果见 [`m06_asset_pricing_results.json`](../data/m06_asset_pricing_results.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/tools/m06_asset_pricing.py
python quant_finance/data/test_m06_asset_pricing.py -v
```

实验生成 360 期、45 个资产、3 个因子的收益系统。时序回归恢复 beta，beta RMSE 约为 0.04，平均绝对 alpha 约为 0.001；Fama–MacBeth 风险价格接近本次样本的因子均值。第二因子的样本均值明显偏离 DGP 的总体均值，恰好展示有限样本风险溢价估计可能非常嘈杂，不能用总体真值替代样本证据。

## 方法对比与失败案例 {#comparison}

| 失败 | 表现 | 处理 |
|---|---|---|
| 百分比与小数混用 | lambda/alpha 放大 100 倍 | 数据契约和单位测试 |
| 最新因子回填历史 | 构造版本泄漏 | 下载日期、档案和 hash |
| 只挑显著 alpha | 多重检验偏差 | 联合检验、失败登记、样本外复核 |
| beta 估计误差 | 两步风险价格偏误 | 更长窗口、errors-in-variables 修正/稳健性 |
| 测试资产太弱 | 横截面 \(R^2\) 虚高 | 扩展有经济张力的测试资产 |
| 因子收益可解释即称因果 | 混淆定价与机制 | 将因果设计单独论证 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| M06-Q01 | CAPM 的 beta 是什么？ | 市场协方差除以市场方差。 |
| M06-Q02 | alpha 为零意味着什么？ | 在给定测试资产/样本下模型未留下平均截距。 |
| M06-Q03 | SDF 定价矩条件是什么？ | \(E[mR]=1\) 或超额收益形式为零。 |
| M06-Q04 | 因子暴露与风险价格差异？ | beta 是数量，lambda 是单位暴露的期望补偿。 |
| M06-Q05 | Fama–MacBeth 两步是什么？ | 先时序 beta，再逐期横截面 lambda。 |
| M06-Q06 | lambda 标准误来自哪里？ | 每期 lambda 的时间序列。 |
| M06-Q07 | 为什么需 HAC？ | lambda 序列可能自相关。 |
| M06-Q08 | 为什么 beta 误差重要？ | 第二步解释变量带测量误差。 |
| M06-Q09 | 高横截面 R² 能证明模型吗？ | 不能，依赖测试资产和模型张力。 |
| M06-Q10 | French 因子文件需登记什么？ | 文件、版本、日期、单位、构造定义。 |
| M06-Q11 | 总收益为何重要？ | 分红和公司行动影响持有回报。 |
| M06-Q12 | 定价 alpha 能否直接交易？ | 还需时点、成本、换手和容量。 |
| M06-Q13 | SDF 与 GMM 有何关系？ | SDF 产生可用 GMM 估计的矩条件。 |
| M06-Q14 | 测试资产为何影响结论？ | 弱或相似组合无法区分模型。 |
| M06-Q15 | 样本因子均值为何偏离总体均值？ | 风险溢价噪声大、样本有限。 |
| M06-Q16 | 因子定价检验是因果检验吗？ | 不是，机制需额外识别。 |
| M06-Q17 | 如何查单位错误？ | 手算样例、量纲和 100 倍异常测试。 |
| M06-Q18 | 多重因子挖掘风险？ | 数据窥探导致偶然显著。 |
| M06-Q19 | 合成实验支持什么？ | 支持两步实现与已知 DGP 检查。 |
| M06-Q20 | 何时暂停定价结论？ | 口径、版本、测试资产或推断闸门失败时。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| M06-Q01 | \(Cov(R_i^e,R_M^e)/Var(R_M^e)\)。 |
| M06-Q02 | 只是在该模型、样本和测试资产下截距近零。 |
| M06-Q03 | \(E[mR]=1\)，超额收益为 \(E[mR^e]=0\)。 |
| M06-Q04 | beta 是暴露，lambda 是暴露价格。 |
| M06-Q05 | 时序估 beta，横截面逐期估 lambda。 |
| M06-Q06 | lambda_t 的时间均值及时间序列标准误。 |
| M06-Q07 | 修正风险价格序列的时间相关。 |
| M06-Q08 | 第一阶段误差进入第二阶段回归变量。 |
| M06-Q09 | 不能；需有张力的测试资产和定价误差检验。 |
| M06-Q10 | 文件名、版本、日期、单位和构造说明。 |
| M06-Q11 | 现金分配和公司行动属于投资者回报。 |
| M06-Q12 | 不能；需可用时间、成本、换手和容量。 |
| M06-Q13 | SDF 正交条件是 GMM 的矩条件。 |
| M06-Q14 | 测试资产决定模型被要求解释的横截面。 |
| M06-Q15 | 因子收益方差高且 T 有限。 |
| M06-Q16 | 不是，资产定价关系不自动识别因果机制。 |
| M06-Q17 | 检查小数/百分比、手算和异常尺度。 |
| M06-Q18 | 反复搜索制造样本内偶然显著。 |
| M06-Q19 | 验证时序/横截面两步和有限样本噪声。 |
| M06-Q20 | 任一数据、口径、版本、资产或推断闸门失败。 |

## 风险与后续建议（Risks & Next） {#risks}

- 合成 beta 是稳定的，未覆盖时变暴露、条件定价、缺失资产和估计窗口选择。
- 当前未使用真实 French 数据；P3 才会冻结公开文件、单位和样本期并复现时序/横截面检验。
- 下一 slice G12/P3 将进行公开因子定价复现，并明确底层 CRSP/Compustat 不可由公开因子文件替代。

## 参考文献（References） {#references}

1. [1] William F. Sharpe, “Capital Asset Prices,” *Journal of Finance*, 1964. [链接](https://doi.org/10.1111/j.1540-6261.1964.tb02865.x)
2. [2] Eugene F. Fama and Kenneth R. French, “Common Risk Factors in the Returns on Stocks and Bonds,” *Journal of Financial Economics*, 1993. [链接](https://doi.org/10.1016/0304-405X(93)90023-5)
3. [3] Eugene F. Fama and James D. MacBeth, “Risk, Return, and Equilibrium,” *Journal of Political Economy*, 1973. [链接](https://doi.org/10.1086/260061)
4. [4] Kenneth R. French, “Data Library.” [链接](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
5. [5] Bruce E. Hansen, “Econometrics.” [链接](https://www.ssc.wisc.edu/~bhansen/econometrics/)
