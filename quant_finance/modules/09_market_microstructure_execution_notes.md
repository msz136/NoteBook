---
title: 市场微观结构与执行：订单簿、流动性、冲击与容量
subtitle: M09 · 从信号收益走向可成交价格、队列状态和 implementation shortfall
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Market Microstructure and Execution
---

# 市场微观结构与执行：订单簿、流动性、冲击与容量

## 问题（Question） {#question}

为什么收盘价回测中的 25 bps alpha 不能直接视为可实现收益？限价簿的价差、深度、队列、冲击、延迟和成交概率如何进入 implementation shortfall？本模块用合成订单簿验证扫单数量增加时 VWAP 成本单调上升，并用平方根冲击模型给出明确但仅示例性的容量上限。

## 背景与动机（Background & Motivation） {#background}

Kyle 模型用订单流和价格冲击描述信息交易与流动性；Almgren–Chriss 将执行问题写为冲击成本和风险之间的动态权衡。[1][2] 真实订单簿是事件序列而非静态图片：新增、撤单、改单、成交、隐藏流动性、交易所优先级和网络延迟共同决定填单。没有执行协议，研究信号不能升级为策略收益。

<div class="evidence"><strong>证据边界：</strong>理论边界来自经典微观结构和最优执行文献；本地簿、冲击参数和容量数字均为合成示例。没有真实逐笔数据、排队位置或券商成交回报，因此不支持实盘滑点、市场容量或最佳执行结论。</div>

## 基础概念与术语 {#concepts}

| 概念 | 定义 | 容易遗漏的边界 |
|---|---|---|
| mid price | 最优买卖价中点 | 不一定可成交 |
| quoted spread | 最优 ask 减 best bid | 与 effective/realized spread 不同 |
| depth | 各价位可见数量 | 可撤单、隐藏单和重复快照 |
| queue priority | 同价订单的成交先后规则 | price-time/pro-rata 因场所不同 |
| market impact | 自身交易引起的价格变化 | 临时与永久成分难分 |
| implementation shortfall | 决策价格到实际成交/未成交的差额 | 包含延迟、冲击、机会成本与费用 |
| capacity | 在成本/风险限额下可部署规模 | 随波动、ADV、持有期和拥挤变化 |

## 订单簿与成交协议 {#order-book}

一笔买入市价单会依次消耗 ask 侧价格层。若第 \(l\) 层成交量为 \(q_l\)、价格为 \(p_l\)：

\[
VWAP=\frac{\sum_l p_lq_l}{\sum_lq_l},
\qquad Shortfall_{bps}=10^4\left(\frac{VWAP}{P_{decision}}-1\right).
\]

限价单可能降低立即成本但引入未成交和逆向选择。回放必须定义事件排序、同时间戳规则、排队位置、部分成交、撤单确认和撮合优先级。

## 流动性与冲击 {#impact}

常见经验平方根冲击近似：

\[
I(Q)=Y\sigma\sqrt{\frac{Q}{V}},
\]

其中 \(Q\) 是订单量，\(V\) 是对应期间成交量，\(\sigma\) 是波动率，\(Y\) 是需校准系数。它是量级模型而非市场定律；小单、大宗、不同持有期和流动性制度需要重新估计。

Almgren–Chriss 类型执行在期望成本和价格风险间权衡：

\[
\min_{x_t}\;E[Cost(x)]+\lambda Var(Cost(x)),
\]

并受完成时间、参与率、盘口深度和风险限制约束。

## 容量与成本预算 {#capacity}

若 gross alpha 为 \(a\)，半价差为 \(s\)，可容忍冲击满足：

\[
s+10^4Y\sigma\sqrt{Q/V}\le a.
\]

可反解 \(Q/V\) 的示例上限。真实容量还需双边交易、换手、借券、融资、信号衰减、拥挤、退出时间和多日执行；单日 ADV 比例不是完整容量证明。

## 数据与回放契约 {#math}

| 类别 | 必须保留 |
|---|---|
| 时钟 | exchange timestamp、receive timestamp、sequence number、时区 |
| 订单 | venue/order id、side、price、size、type、TIF、状态转换 |
| 行情 | bid/ask levels、trade condition、lot、tick、auction 状态 |
| 执行 | decision/arrival/fill time、partial fill、fee/rebate、reject/cancel |
| 质量 | gap、duplicate、out-of-order、crossed book、halt/correction |
| 许可 | 原始逐笔数据的访问、使用和再分发权限 |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
events = load_sequenced_market_data(venue, session, asof_at)
book = replay_add_cancel_modify_trade(events, priority_rule="price-time")
decision_mid = book.mid(decision_timestamp)
fills = simulate_or_match_orders(book, latency, queue_position, fees)
shortfall = implementation_shortfall(decision_mid, fills, unfilled_quantity)
impact = calibrate_by_size_volatility_adv_and_horizon(fills)
capacity = solve_alpha_after_spread_impact_borrow_and_risk_budget()
report_fill_rate_shortfall_tail_cost_and_failure_sessions()
```

合成扫单与容量实现见 [`m09_execution_costs.py`](../tools/m09_execution_costs.py)，结果见 [`m09_execution_costs_results.json`](../data/m09_execution_costs_results.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/tools/m09_execution_costs.py
python quant_finance/data/test_m09_execution_costs.py -v
```

合成 best bid/ask 为 99.99/100.01，quoted spread 为 2 bps。以 mid=100 作为 decision price：

| 买入数量 | VWAP | Shortfall (bps) | 平方根冲击 (bps) |
|---:|---:|---:|---:|
| 500 | 100.0100 | 1.00 | 2.21 |
| 1,500 | 100.0120 | 1.20 | 3.83 |
| 4,000 | 100.0220 | 2.20 | 6.26 |
| 9,000 | 100.0453 | 4.53 | 9.39 |

测试验证扫单 shortfall 和平方根冲击均随数量单调上升。示例 25 bps gross alpha、1 bps 半价差、2% 波动率、\(Y=0.7\)、ADV 200 万下，模型反解上限约为 58,776 单位；这只是代数示例，不是市场容量估计。

## 方法对比与失败案例 {#comparison}

| 失败 | 回测偏差 | 修复 |
|---|---|---|
| 用 mid/close 当成交价 | 忽略价差和深度 | bid/ask 与簿级扫单 |
| 假设限价单全成 | 低估机会成本和逆向选择 | 队列、延迟、fill probability |
| 静态盘口回放 | 忽略撤单和事件顺序 | sequence-based event replay |
| 固定 bps 成本 | 忽略规模、波动与 ADV | 分层冲击和容量模型 |
| 只看平均 shortfall | 忽略尾部执行事故 | 分位数、拒单、停牌和失败场次 |
| 混用多场所时钟 | 产生虚假先后关系 | 时钟同步和 receive-time 审计 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| M09-Q01 | quoted/effective spread 区别？ | 报价宽度 vs 实际成交相对 mid。 |
| M09-Q02 | 为什么 mid 不可成交？ | 买入通常触及 ask，卖出触及 bid。 |
| M09-Q03 | VWAP 如何计算？ | 成交价格按数量加权。 |
| M09-Q04 | implementation shortfall 包含什么？ | 延迟、成交、费用和机会成本。 |
| M09-Q05 | 限价单的主要风险？ | 不成交和逆向选择。 |
| M09-Q06 | queue position 为什么重要？ | 同价位成交按优先级分配。 |
| M09-Q07 | 平方根冲击变量是什么？ | Q、V、sigma、Y。 |
| M09-Q08 | 冲击模型为何需重估？ | 市场、规模、期限和制度变化。 |
| M09-Q09 | capacity 与 ADV 比例相同吗？ | 不同，容量还含 alpha、成本、风险和退出。 |
| M09-Q10 | permanent/temporary impact 差异？ | 持久信息效应 vs 执行后回落成本。 |
| M09-Q11 | 决策价和到达价差异？ | 信号决策时 vs 订单到市场时。 |
| M09-Q12 | 为什么需 sequence number？ | 同时间戳事件仍需确定排序。 |
| M09-Q13 | crossed book 一定是错误吗？ | 可能是不同场所/延迟，也需标记调查。 |
| M09-Q14 | auction 如何处理？ | 独立撮合和价格形成规则。 |
| M09-Q15 | fee/rebate 为什么重要？ | 改变 maker/taker 净成本。 |
| M09-Q16 | 如何量化未成交？ | fill rate 和未成交机会成本。 |
| M09-Q17 | 真实容量最少报告什么？ | ADV、参与率、冲击、换手、退出期。 |
| M09-Q18 | point-in-time 如何进入执行？ | 决策只能看到当时收到的簿状态。 |
| M09-Q19 | 合成实验支持什么？ | 支持扫单/冲击公式，不支持实盘。 |
| M09-Q20 | 何时暂停执行结论？ | 时钟、事件、队列或成交协议不可信时。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| M09-Q01 | quoted 是 bid–ask，effective 是成交相对 mid 的双倍偏离。 |
| M09-Q02 | mid 位于盘口之间，没有挂单保证。 |
| M09-Q03 | \(\sum pq/\sum q\)。 |
| M09-Q04 | 决策到完成的价格、费用和未成交成本。 |
| M09-Q05 | queue 不到和坏消息时被动成交。 |
| M09-Q06 | 决定可成交数量和等待时间。 |
| M09-Q07 | 订单量、成交量、波动率、校准系数。 |
| M09-Q08 | 参数不是跨市场/时期常数。 |
| M09-Q09 | ADV 只是容量约束之一。 |
| M09-Q10 | 临时成本会衰减，永久成分持续。 |
| M09-Q11 | arrival 包含信号到市场的延迟。 |
| M09-Q12 | 保证事件重放顺序确定。 |
| M09-Q13 | 先检查 venue、时钟、延迟和异常。 |
| M09-Q14 | 使用拍卖阶段专有订单和清算价规则。 |
| M09-Q15 | 净成本需扣返佣并加费用。 |
| M09-Q16 | 报告 fill ratio 与未成交反事实价格。 |
| M09-Q17 | 至少规模/ADV、参与率、冲击、换手、退出期。 |
| M09-Q18 | 使用 receive-time 可见事件集。 |
| M09-Q19 | 只验证合成簿 VWAP 和模型单调性。 |
| M09-Q20 | 任一时钟、序列、队列、费用或 fill 闸门失败。 |

## 风险与后续建议（Risks & Next） {#risks}

- 静态四档订单簿不含撤单、隐藏单、排队、拍卖和多场所路由。
- 平方根冲击参数未由真实成交校准，58,776 单位不能作为部署额度。
- 下一 slice G17/M10 将进入因子研究与金融 ML，严格引入 purging/embargo、walk-forward、概率预测和消融；执行成本继续作为标签/目标后的经济闸门。

## 参考文献（References） {#references}

1. [1] Albert S. Kyle, “Continuous Auctions and Insider Trading,” *Econometrica*, 1985. [链接](https://doi.org/10.2307/1913210)
2. [2] Robert Almgren and Neil Chriss, “Optimal Execution of Portfolio Transactions,” *Journal of Risk*, 2001. [链接](https://www.math.nyu.edu/~chriss/optliq_f.pdf)
