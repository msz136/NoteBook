---
title: P4 组合与风险实验：估计误差、换手、成本与压力敏感性
subtitle: 严格 walk-forward 比较样本均值组合与收缩均值＋换手限制组合
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Portfolio Risk Experiment
---

# P4 组合与风险实验：估计误差、换手、成本与压力敏感性

## 问题（Question） {#question}

均值估计噪声如何通过优化器变成集中持仓和高换手？加入横截面均值收缩、单次换手上限和线性交易成本后，样本外组合表现及压力损失如何变化？本项目用合成八资产收益执行 720 日 walk-forward 实验。

## 背景与动机（Background & Motivation） {#background}

Markowitz 框架对预期收益输入高度敏感；M08 已说明收缩、约束、成本和压力测试是生产组合不可分割的部分。[1] 本项目不比较“神奇策略”，而是固定同一收益样本、协方差窗口和风险厌恶，只改变均值处理与换手控制，直接观察估计误差和成本的传播。

<div class="evidence"><strong>证据边界：</strong>所有收益、成本和压力情景均为合成。本结果只验证 walk-forward、换手、成本扣除和约束实现；Sharpe 数字不是实际市场表现、投资建议或未来收益证据。</div>

## 实验协议 {#concepts}

| 项目 | 冻结值 |
|---|---|
| 资产数 | 8 |
| 总样本 | 720 个交易日 |
| 初始/滚动估计窗 | 120 日 |
| 再平衡 | 每 20 日 |
| 交易成本 | 每单位双边 L1 换手 10 bps |
| 约束 | 长仓、权重和为 1 |
| 策略 A | 直接样本均值＋样本协方差 |
| 策略 B | 25% 样本均值＋75% 横截面均值；单次 L1 换手上限 0.35 |

## 方法与数学形式（Methods & Mathematical Form） {#methods}

每次再平衡只使用此前 120 日估计 \(\hat\mu_t,\hat\Sigma_t\)：

\[
w_t^*=\arg\max_{w\ge0,\mathbf1'w=1}
w'\hat\mu_t-\frac{\gamma}{2}w'\hat\Sigma_tw.
\]

策略 B 的收缩均值：

\[
\tilde\mu_t=0.25\hat\mu_t+0.75\bar\mu_t\mathbf1.
\]

换手和净收益：

\[
TO_t=\sum_i|w_{i,t}-w_{i,t^-}|,
\qquad R_{t,net}=R_{t,gross}-c\,TO_t.
\]

成本在再平衡块的第一天扣除；这是简化线性模型，没有报价价差、冲击、延迟、税费或容量函数。

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
for rebalance_t in range(lookback, T, 20):
    history = returns[rebalance_t-120:rebalance_t]
    mu, cov = estimate(history)
    raw_weights = optimize_long_only(mu, cov)
    shrink_weights = optimize_long_only(shrink(mu), cov)
    shrink_weights = cap_l1_turnover(old_weights, shrink_weights, 0.35)
    gross = future_20_days @ weights
    net[0] = gross[0] - 0.0010 * l1_turnover
    record_weights_returns_turnover_and_stress()
```

实现见 [`p4_portfolio_risk.py`](p4_portfolio_risk.py)，结果见 [`p4_portfolio_risk_results.json`](p4_portfolio_risk_results.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/projects/p4_portfolio_risk/p4_portfolio_risk.py
python quant_finance/projects/p4_portfolio_risk/test_p4_portfolio_risk.py -v
```

| 指标 | 样本均值 | 收缩＋换手上限 |
|---|---:|---:|
| 总 L1 换手 | 11.9516 | 3.8341 |
| Gross 日均收益 | 0.000389 | 0.000489 |
| Net 日均收益 | 0.000370 | 0.000483 |
| Gross 年化 Sharpe | 1.1080 | 1.8620 |
| Net 年化 Sharpe | 1.0523 | 1.8386 |
| 压力损失 | 0.0967 | 0.0999 |

在该 seed 和 DGP 下，收缩＋换手限制同时降低换手和提高样本外风险调整结果；但其压力损失略高，说明低波动/低换手不保证所有情景下更安全。该排序不能外推到真实市场或其他 DGP。

## 敏感性与失败案例 {#comparison}

| 失败 | 本实验如何暴露 | 后续要求 |
|---|---|---|
| 均值噪声 | 策略 A 权重更集中、换手更高 | 多 shrink 强度和窗口敏感性 |
| 线性成本过简 | 只扣 10 bps×换手 | 分段冲击、ADV、容量和价差 |
| 单一 seed | 排名可能偶然 | 多 seed/多制度 Monte Carlo |
| Sharpe 年化 | 假设日收益尺度稳定 | 置信区间和序列相关修正 |
| 单一压力情景 | 不能代表全尾部 | 历史、假设和反向压力集合 |
| 无可交易数据 | 无停牌/涨跌停/成交约束 | 真实点时数据和执行协议 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| P4-Q01 | 实验如何避免未来泄漏？ | 每次只用此前 120 日。 |
| P4-Q02 | L1 换手怎么定义？ | 新旧权重绝对差之和。 |
| P4-Q03 | 成本在哪里扣除？ | 再平衡块第一日按换手扣。 |
| P4-Q04 | 均值收缩作用？ | 降低横截面噪声和极端权重。 |
| P4-Q05 | 换手上限为何不是成本模型？ | 只限制交易量，不给真实冲击价格。 |
| P4-Q06 | 净收益为什么低于 gross？ | 扣除了非负成本。 |
| P4-Q07 | 低换手为何仍可能压力损失高？ | 压力方向与持仓暴露不同于常态方差。 |
| P4-Q08 | Sharpe 排名能否推广？ | 不能，依赖 seed、DGP 和协议。 |
| P4-Q09 | 真实容量还需要什么？ | ADV、冲击、成交时延和退出期。 |
| P4-Q10 | 下一步最重要的稳健性？ | 多 seed、窗口、成本和压力网格。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| P4-Q01 | 估计窗严格结束在再平衡日前。 |
| P4-Q02 | \(\sum_i|w_{i,t}-w_{i,t^-}|\)。 |
| P4-Q03 | 每个新持仓块第一期。 |
| P4-Q04 | 把 noisy 均值拉向共同中心。 |
| P4-Q05 | 上限没有映射到价差和非线性冲击。 |
| P4-Q06 | 线性成本为非负且按换手扣除。 |
| P4-Q07 | 常态协方差与指定尾部冲击方向不同。 |
| P4-Q08 | 不能；只是一个合成路径。 |
| P4-Q09 | 需要成交量、价差、冲击、延迟和清算。 |
| P4-Q10 | 对随机路径、窗口、成本和压力做网格敏感性。 |

## 风险与后续建议（Risks & Next） {#risks}

- 未实现非线性市场冲击、融资、借券、税费、现金缓冲与不可交易状态。
- 未给 Sharpe 差异置信区间，不能声称策略 B 在统计上优越。
- 下一 slice G16/M09 将进入市场微观结构、订单簿、流动性、市场冲击、执行和容量，为成本模型补足机制。

## 参考文献（References） {#references}

1. [1] Harry Markowitz, “Portfolio Selection,” *Journal of Finance*, 1952. [链接](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x)
2. [2] Fischer Black and Robert Litterman, “Global Portfolio Optimization,” *Financial Analysts Journal*, 1992. [链接](https://doi.org/10.2469/faj.v48.n5.28)
