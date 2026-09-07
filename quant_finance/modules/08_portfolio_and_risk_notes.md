---
title: 组合与风险：均值—方差、Black–Litterman、因子风险与 VaR/ES
subtitle: M08 · 把估计误差、约束、尾部损失和压力情景纳入组合决策
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Portfolio and Risk
---

# 组合与风险：均值—方差、Black–Litterman、因子风险与 VaR/ES

## 问题（Question） {#question}

为什么理论最优权重在实践中常极端不稳？Black–Litterman 如何把市场先验与观点结合？因子风险、VaR、Expected Shortfall 和压力测试分别回答什么问题？本模块用合成资产验证长仓全投资约束、后验收益、风险分解与尾部指标顺序。

## 背景与动机（Background & Motivation） {#background}

Markowitz 均值—方差框架把组合选择写为预期收益与方差权衡；Black–Litterman 用均衡先验和观点缓解直接使用噪声均值所导致的极端权重。[1][2] Basel 市场风险框架推动 Expected Shortfall 在尾部风险计量中的应用。[3] 任何风险数字都依赖持仓、价格、分布、流动性与估值时间，不能脱离数据契约解释。

<div class="evidence"><strong>证据边界：</strong>模型形式来自经典文献和监管入口；本地权重、VaR/ES 和压力损失只来自合成收益与示例观点，不构成投资建议。未运行 cvxpy，长仓约束使用 NumPy 投影梯度作为教学实现。</div>

## 基础概念与术语 {#concepts}

| 概念 | 含义 | 边界 |
|---|---|---|
| 有效前沿 | 给定风险下最高期望收益的组合集合 | 输入均值/协方差估计误差巨大 |
| 风险厌恶 | 收益与方差权衡系数 | 不是客观市场常数 |
| Black–Litterman | 均衡先验与线性观点的后验组合 | 依赖 tau、Omega 与观点可信度 |
| 因子风险 | 由共同因子暴露解释的方差 | 剩余特质风险仍需建模 |
| VaR | 给定置信度的损失分位数 | 不描述分位点之外损失大小 |
| Expected Shortfall (ES) | 超过 VaR 后的平均损失 | 仍依赖样本、模型和流动性假设 |
| 压力测试 | 指定极端情景下的重估损失 | 非概率预测，不能与 VaR 混为一谈 |

## 均值—方差与约束 {#mean-variance}

基本问题：

\[
\max_w\; w'\mu-\frac{\gamma}{2}w'\Sigma w,
\quad \text{s.t.}\quad \mathbf1'w=1,\;w\ge0.
\]

\(\mu\) 是预期收益，\(\Sigma\) 是协方差矩阵，\(\gamma\) 是风险厌恶。实际还需杠杆、单名、行业、因子、换手、成交量和融资约束。小幅均值变化可能造成巨大权重变化，因此必须做 shrinkage、重采样和参数敏感性分析。

## Black–Litterman {#black-litterman}

令均衡先验为 \(\pi=\delta\Sigma w_{mkt}\)，观点为 \(P\mu=q+\epsilon\)，观点误差协方差为 \(\Omega\)。后验均值：

\[
\mu_{BL}=\left[(\tau\Sigma)^{-1}+P'\Omega^{-1}P\right]^{-1}
\left[(\tau\Sigma)^{-1}\pi+P'\Omega^{-1}q\right].
\]

\(P\) 定义相对/绝对观点，\(q\) 给出观点回报，\(\Omega\) 表达不确定性。后验并不证明观点正确；它只把先验与观点以可审计方式结合。

## 因子风险与归因 {#factor-risk}

若资产收益：

\[
r=Bf+\varepsilon,\qquad \Sigma=B\Sigma_fB'+D,
\]

则组合因子方差为 \(w'B\Sigma_fB'w\)，特质方差为 \(w'Dw\)。风险贡献应与总方差/波动率一致；因子定义、暴露时点和协方差窗口必须冻结。

## VaR、ES 与压力测试 {#tail-risk}

对损失 \(L=-R_p\)，置信水平 \(\alpha\)：

\[
VaR_\alpha=\inf\{l:P(L\le l)\ge\alpha\},
\qquad ES_\alpha=E[L\mid L\ge VaR_\alpha].
\]

历史模拟保留经验分布但受样本窗口限制；参数法依赖分布；Monte Carlo 依赖风险因子和估值模型。压力测试需定义冲击、相关性破裂、流动性折价、保证金和二阶重估。

## 数据与治理契约 {#math}

| 项目 | 必须冻结 |
|---|---|
| 持仓 | 数量、价格、币种、杠杆、衍生品 Greeks/完整重估 |
| 输入 | 预期收益、协方差、窗口、缺失、点时可见性 |
| 约束 | 长短仓、单名/行业/因子、换手、成本、容量 |
| 风险 | VaR/ES 水平、持有期、重叠、回测和例外数 |
| 压力 | 历史/假设情景、冲击传播、流动性和恢复动作 |
| 治理 | 限额、升级、覆盖、模型版本和人工 override |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
mu, cov = estimate_inputs(point_in_time_returns, shrinkage=True)
prior = risk_aversion * cov @ market_weights
posterior = black_litterman(prior, cov, P, q, Omega, tau)
weights = solve_constrained_portfolio(posterior, cov, long_only=True, turnover_limit=limit)
factor_risk = decompose_factor_and_idiosyncratic_variance(weights, B, factor_cov, D)
var, es = historical_or_model_tail_risk(weights, returns, confidence=.95)
stress = full_revalue(weights, stress_scenarios, liquidity_haircuts)
report_constraints_sensitivity_backtests_and_breaches()
```

实现见 [`m08_portfolio_risk.py`](../tools/m08_portfolio_risk.py)，结果见 [`m08_portfolio_risk_results.json`](../data/m08_portfolio_risk_results.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/tools/m08_portfolio_risk.py
python quant_finance/data/test_m08_portfolio_risk.py -v
```

| 指标 | 结果 |
|---|---:|
| 权重和 | 1.0000 |
| 最小权重 | 0.1463 |
| 日预期收益 | 0.000264 |
| 日波动率 | 0.009709 |
| Historical VaR 95% | 0.01573 |
| Historical ES 95% | 0.02035 |
| 指定压力情景损失 | 0.08575 |

测试验证长仓全投资约束、ES 不小于 VaR、压力损失为正、因子方差不超过总方差，以及 Black–Litterman 观点确实改变先验均值。结果只属于本地合成机制。

## 方法对比与失败案例 {#comparison}

| 失败 | 影响 | 处理 |
|---|---|---|
| 直接用样本均值 | 极端且不稳定权重 | shrinkage、BL、权重/换手约束 |
| 协方差病态 | 数值不稳、虚假分散 | shrinkage、因子模型、条件数检查 |
| 把 VaR 当最大损失 | 忽略尾部分布 | ES、压力和反向压力测试 |
| 正态参数 VaR | 尾部/偏度低估 | 历史/重尾/EVT 与回测 |
| 忽略流动性和容量 | 组合无法交易 | 冲击、成交量、退出天数和折价 |
| 压力情景无行动 | 风险报告不能治理 | 限额、触发器、升级和恢复计划 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| M08-Q01 | 写出均值—方差目标。 | 收益减风险厌恶乘方差并含约束。 |
| M08-Q02 | 为什么均值误差危险？ | 逆协方差放大噪声并产生极端权重。 |
| M08-Q03 | Black–Litterman 先验是什么？ | 常用均衡隐含收益 \(\pi=\delta\Sigma w\)。 |
| M08-Q04 | P、q、Omega 含义？ | 观点映射、观点值、观点误差协方差。 |
| M08-Q05 | 因子风险如何计算？ | \(w'B\Sigma_fB'w\)。 |
| M08-Q06 | VaR 与 ES 差异？ | 分位数 vs 超过分位数的平均损失。 |
| M08-Q07 | 为什么 ES 通常不小于 VaR？ | ES 平均更坏尾部损失。 |
| M08-Q08 | 历史 VaR 的风险？ | 窗口有限且未来制度可能不同。 |
| M08-Q09 | 参数 VaR 的风险？ | 分布错设和相关性变化。 |
| M08-Q10 | 压力测试是概率预测吗？ | 不是，是条件情景损失。 |
| M08-Q11 | 反向压力测试是什么？ | 找到导致不可接受损失的情景。 |
| M08-Q12 | 换手约束为何重要？ | 降低成本和估计噪声驱动交易。 |
| M08-Q13 | 容量如何进入优化？ | 仓位/交易量/冲击约束。 |
| M08-Q14 | 协方差 shrinkage 作用？ | 降低估计方差和病态性。 |
| M08-Q15 | 风险贡献应满足什么？ | 分项贡献和总风险一致。 |
| M08-Q16 | 衍生品压力如何估值？ | Greeks 近似或完整重估并含非线性。 |
| M08-Q17 | point-in-time 如何约束组合？ | 所有输入和持仓在 asof 前可见。 |
| M08-Q18 | BL 后验能证明观点吗？ | 不能，只融合观点与先验。 |
| M08-Q19 | 合成实验支持什么？ | 支持约束、风险指标和公式实现。 |
| M08-Q20 | 何时暂停优化结果？ | 数据、约束、稳定性或风险治理失败时。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| M08-Q01 | \(\max w'\mu-\gamma w'\Sigma w/2\) 并列出约束。 |
| M08-Q02 | 最优权重对噪声均值高度敏感。 |
| M08-Q03 | 市场权重和风险厌恶隐含的均衡收益。 |
| M08-Q04 | P 映射观点，q 是值，Omega 是不确定性。 |
| M08-Q05 | 组合暴露乘因子协方差再乘暴露。 |
| M08-Q06 | VaR 是阈值，ES 是阈值后的平均。 |
| M08-Q07 | 尾部条件均值包含更严重损失。 |
| M08-Q08 | 历史未发生不等于未来不发生。 |
| M08-Q09 | 正态/稳定相关假设可能失效。 |
| M08-Q10 | 压力是指定情景，不附带频率承诺。 |
| M08-Q11 | 搜索突破资本/限额的最小或合理冲击。 |
| M08-Q12 | 控制交易成本和模型噪声。 |
| M08-Q13 | 用 ADV、冲击、持仓上限和退出期约束。 |
| M08-Q14 | 用结构化目标降低样本协方差噪声。 |
| M08-Q15 | Euler/方差贡献应加总到组合风险。 |
| M08-Q16 | 非线性显著时用完整重估。 |
| M08-Q17 | 输入满足 `available_at <= asof_at`。 |
| M08-Q18 | 不能；观点仍可能错误。 |
| M08-Q19 | 验证长仓约束、BL、VaR/ES 和压力实现。 |
| M08-Q20 | 任一输入、约束、稳定性或治理闸门失败。 |

## 风险与后续建议（Risks & Next） {#risks}

- 当前优化器是教学投影梯度，未提供 cvxpy 的求解器状态、对偶变量与不可行诊断。
- VaR/ES 使用合成历史收益，未完成实际持仓回测、期限缩放、流动性调整或监管口径。
- 下一 slice G15/P4 将加入成本、换手、估计误差与压力情景敏感性，形成组合实验报告。

## 参考文献（References） {#references}

1. [1] Harry Markowitz, “Portfolio Selection,” *Journal of Finance*, 1952. [链接](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x)
2. [2] Fischer Black and Robert Litterman, “Global Portfolio Optimization,” *Financial Analysts Journal*, 1992. [链接](https://doi.org/10.2469/faj.v48.n5.28)
3. [3] Basel Committee on Banking Supervision, “Minimum capital requirements for market risk,” 2019. [链接](https://www.bis.org/bcbs/publ/d457.htm)
