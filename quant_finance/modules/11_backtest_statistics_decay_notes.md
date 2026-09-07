---
title: 回测统计与策略衰减：数据窥探、成本、引擎语义与失效诊断
subtitle: M11 · 把回测视为可证伪的事件协议，而不是收益曲线生成器
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Backtest Statistics and Strategy Decay
---

# 回测统计与策略衰减：数据窥探、成本、引擎语义与失效诊断

## 问题（Question） {#question}

为什么同一信号在向量化回测和事件驱动引擎中会得到不同收益？如何区分数据窥探、成本遗漏、成交假设和真实策略衰减？本模块用合成制度变化对照“满额、无成本向量回测”和“90% 成交、费用与滑点事件回测”，并记录早期/晚期失效。

## 背景与动机（Background & Motivation） {#background}

White Reality Check 针对数据窥探下的模型比较；Carr–López de Prado 讨论反复回测校准规则的过拟合边界。[1][2] Qlib 提供面向量化研究的数据和工作流；LEAN 提供事件驱动回测与交易引擎。[3][4] 工具本身不会消除时间泄漏、错误成交语义或选择偏差，因此两种引擎的差异必须成为研究对象。

<div class="evidence"><strong>证据边界：</strong>本地结果来自合成信号、已知制度衰减、90% 填单和固定 bps 成本；只验证引擎语义、成本和衰减诊断。没有实际运行 Qlib/LEAN，也不构成真实策略或平台性能比较。</div>

## 回测对象与时间语义 {#concepts}

| 时点 | 必须区分 |
|---|---|
| observed_at | 市场/事件实际发生时间 |
| available_at | 数据首次可用于策略的时间 |
| decision_at | 策略生成目标仓位时间 |
| submitted_at | 订单发送时间 |
| accepted_at | 市场/券商接受时间 |
| filled_at | 实际成交时间 |
| marked_at | P&L 估值时间与价格来源 |

若使用 close 生成信号，则不能无条件以同一 close 满额成交。回测必须指定 next-open、VWAP、limit/market、延迟、部分成交和未成交处理。

## 回测统计与多重检验 {#statistics}

样本 Sharpe：

\[
\widehat{SR}=\frac{\bar r}{s_r}\sqrt A.
\]

年化因子 \(A\) 依赖频率；收益自相关、偏度、厚尾和非平稳会破坏朴素标准误。多重检验下应登记尝试次数、相关性、选择规则，并根据问题使用 Reality Check、SPA、FDR、deflated Sharpe 或 PBO；不存在单一万能校正。

最大回撤：

\[
MDD=\min_t\left(\frac{W_t}{\max_{s\le t}W_s}-1\right).
\]

回撤依赖路径和样本端点，不能作为尾部概率的完整替代。

## 向量化与事件驱动引擎 {#engines}

| 方面 | 向量化 | 事件驱动 |
|---|---|---|
| 速度 | 快，适合研究筛选 | 慢，逐事件状态更新 |
| 成交 | 常用收益×仓位近似 | 显式订单、成交、费用和持仓 |
| 时间 | 易出现 shift/close 泄漏 | 仍需正确事件/时钟排序 |
| 部分成交 | 通常省略 | 可模拟但需队列/流动性模型 |
| 用途 | 机制和大规模初筛 | 执行语义与部署前重建 |

两类结果不一致不应简单取“更好看”的一个；需要从信号时间、目标仓位、成交价、费用、公司行动、现金和估值逐项调和。

## 成本、容量与衰减 {#decay}

净收益可写为：

\[
r_t^{net}=w_{t-1}r_t-c_t(|\Delta w_t|,\sigma_t,ADV_t,venue_t).
\]

策略衰减可能来自拥挤、制度变化、数据定义变化、成本上升、执行恶化或纯样本噪声。诊断应按时间、资产、方向、波动、流动性、成交场所和模型版本分解，而不是只画累计收益。

## 研究与失败契约 {#math}

| 闸门 | 必须记录 |
|---|---|
| 数据 | source/hash、point-in-time、公司行动、universe |
| 信号 | feature/decision 时间、持有期、换仓规则 |
| 订单 | 类型、延迟、成交价、部分成交、费用/返佣 |
| P&L | 现金、融资、借券、mark、汇率和税费 |
| 统计 | 所有尝试、基准、区间、子样本和多重检验 |
| 衰减 | 预设监控、触发器、归因、暂停/退役规则 |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
vector_result = vectorized_backtest(signal.shift_to_next_tradable_period(), returns)
event_result = event_backtest(
    signal, orders, latency, partial_fill, spread, impact, fees, cash_and_positions
)
reconcile_daily_positions_turnover_fills_and_marks(vector_result, event_result)
statistics = robust_performance_and_multiple_testing(all_experiments)
decay = diagnose_by_regime_liquidity_direction_and_model_version(event_result)
trigger_pause_if_cost_capacity_or_decay_limits_breach(decay)
```

实现见 [`m11_backtest_decay.py`](../tools/m11_backtest_decay.py)，结果见 [`m11_backtest_decay_results.json`](../data/m11_backtest_decay_results.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/tools/m11_backtest_decay.py
python quant_finance/data/test_m11_backtest_decay.py -v
```

| 指标 | 向量化 gross | 事件 gross | 事件 net |
|---|---:|---:|---:|
| 日均收益 | 0.000780 | 0.000702 | 0.000461 |
| 年化 Sharpe | 1.5129 | 1.5129 | 0.9933 |
| 最大回撤 | -0.2635 | -0.2400 | -0.2875 |

事件模型假设 90% 填单、4 bps 费用和 2 bps 滑点，每单位仓位变化扣费，总换手 360.97。早期事件净 Sharpe 为 2.8518，晚期为 -0.8194，对应 DGP 中信号系数从 0.0016 降至 0.0002。测试验证成本降低净收益、引擎差异为正且晚期衰减。

## 失效诊断与方法对比 {#comparison}

| 症状 | 可能原因 | 区分证据 |
|---|---|---|
| vector 好、event 差 | 成交/成本/时间语义 | 仓位、fill、turnover 日级对账 |
| gross 好、net 差 | 高频换手或冲击 | 成本按规模/流动性分解 |
| 早期好、晚期差 | 制度衰减或选择偏差 | 预设滚动监控和外部制度事件 |
| 少数资产贡献全部 | universe/集中风险 | 资产和行业归因 |
| 仅一种阈值好 | 参数过拟合 | 邻域敏感性和完整实验族 |
| 回测好、纸面差 | 延迟/数据/订单语义 | live shadow 与 replay 对账 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| M11-Q01 | close 信号能否同 close 成交？ | 通常不能，除非有更早可用证据。 |
| M11-Q02 | 向量化和事件驱动核心差异？ | 数组收益映射 vs 显式状态/订单/成交。 |
| M11-Q03 | 为什么 gross Sharpe 不够？ | 忽略成本、容量和成交。 |
| M11-Q04 | 最大回撤如何定义？ | 财富相对历史峰值的最小跌幅。 |
| M11-Q05 | Sharpe 年化需要什么假设？ | 频率和依赖结构明确。 |
| M11-Q06 | 数据窥探是什么？ | 多次搜索后只报告最好结果。 |
| M11-Q07 | Reality Check 解决什么？ | 数据窥探下的相对模型检验。 |
| M11-Q08 | 部分成交如何影响回测？ | 仓位、收益、风险和后续订单都变化。 |
| M11-Q09 | 为什么现金账本重要？ | 融资、费用和可用购买力影响仓位。 |
| M11-Q10 | 公司行动如何影响事件引擎？ | 价格、数量、现金和订单需一致调整。 |
| M11-Q11 | 策略衰减可能来源？ | 拥挤、制度、成本、执行、数据或噪声。 |
| M11-Q12 | 如何区分衰减和坏运气？ | 预设窗口、区间、归因和外部证据。 |
| M11-Q13 | 引擎对账最小粒度？ | 日级/事件级仓位、成交、现金和 mark。 |
| M11-Q14 | 为什么未成交是成本？ | 错失信号收益且改变风险路径。 |
| M11-Q15 | 多重检验分母是什么？ | 所有真实尝试而非最终保留策略。 |
| M11-Q16 | Qlib 与 LEAN 角色差异？ | 研究工作流 vs 事件驱动执行重建。 |
| M11-Q17 | 何时暂停策略？ | 成本、容量、数据或衰减触发器突破。 |
| M11-Q18 | point-in-time 回测要求？ | 决策只使用当时可见数据。 |
| M11-Q19 | 合成实验支持什么？ | 支持引擎差异和制度衰减诊断。 |
| M11-Q20 | 何时禁止发布收益结论？ | 数据、成交、成本、统计或对账失败。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| M11-Q01 | close 后才完整可见时需在后续可交易价格成交。 |
| M11-Q02 | 向量映射不维护完整订单生命周期。 |
| M11-Q03 | 可实现收益必须扣成本并受容量限制。 |
| M11-Q04 | \(\min_t(W_t/\max_{s\le t}W_s-1)\)。 |
| M11-Q05 | 频率、独立/依赖和尺度必须说明。 |
| M11-Q06 | 反复搜索同一历史并选择性报告。 |
| M11-Q07 | 校正“最佳模型”在搜索分母下的显著性。 |
| M11-Q08 | 实际持仓偏离目标并改变 P&L。 |
| M11-Q09 | 订单、融资、费用和保证金依赖现金。 |
| M11-Q10 | 拆股/分红同步更新数量、现金、价格和订单。 |
| M11-Q11 | 至少列拥挤、制度、成本、执行、数据、噪声。 |
| M11-Q12 | 用预注册诊断而非事后故事。 |
| M11-Q13 | 仓位、订单/fill、现金、成本、估值逐项。 |
| M11-Q14 | opportunity cost 属于 implementation shortfall。 |
| M11-Q15 | 完整实验账本中的所有尝试。 |
| M11-Q16 | Qlib 偏研究流水线，LEAN 偏事件/订单语义。 |
| M11-Q17 | 预先定义的 breach 触发暂停/复核。 |
| M11-Q18 | `available_at <= decision_at`。 |
| M11-Q19 | 验证成本/填单导致的引擎差异和衰减。 |
| M11-Q20 | 任一数据、订单、成本、统计或对账闸门失败。 |

## 风险与后续建议（Risks & Next） {#risks}

- 固定 90% fill 和固定 bps 成本不是订单簿仿真；只用于语义对照。
- 合成衰减由已知系数变化产生，现实衰减归因更难且可能不可识别。
- 下一 slice G20/P6 将在事件驱动协议中重建一个已审查策略；若 LEAN CLI 不可用，将保留兼容接口和明确未运行边界，不伪造引擎执行。

## 参考文献（References） {#references}

1. [1] Halbert White, “A Reality Check for Data Snooping,” *Econometrica*, 2000. [链接](https://doi.org/10.1111/1468-0262.00152)
2. [2] Peter Carr and Marcos López de Prado, “Determining Optimal Trading Rules without Backtesting,” 2014. [链接](https://arxiv.org/abs/1408.1159)
3. [3] Microsoft, “Qlib,” official repository. [链接](https://github.com/microsoft/qlib)
4. [4] QuantConnect, “LEAN,” official repository. [链接](https://github.com/QuantConnect/Lean)
