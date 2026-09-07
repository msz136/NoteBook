---
title: P5 无泄漏 Alpha 研究：冻结切分、实验账本与成本后测试
subtitle: 六个候选只在 validation 排名，失败策略保留，最终 test 只打开一次
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Leakage-Free Alpha Research
---

# P5 无泄漏 Alpha 研究：冻结切分、实验账本与成本后测试

## 问题（Question） {#question}

如何把“我找到一个表现好的信号”改写成可审计研究？本项目在合成序列上预先冻结 train/validation/test、20 日 embargo、六个候选和 5 bps 换手成本；只用 validation 净 Sharpe 选择候选，保留所有失败记录，最后只打开一次 test。

## 背景与动机（Background & Motivation） {#background}

回测过拟合往往来自反复查看同一测试集、删除失败策略和不断调整阈值。White Reality Check 与 Carr–López de Prado 的工作分别强调数据窥探和规则搜索边界。[1][2] P5 的目标不是证明 alpha，而是建立一个能显示失败、选择次数和测试隔离的最小研究账本。

<div class="evidence"><strong>证据边界：</strong>所有信号、收益和成本均为合成。validation 与 test Sharpe 只是协议运行结果；朴素 p 值未修正序列相关，Bonferroni 只对登记的六个候选作保守调整。结果不构成真实 alpha、投资建议或统计发现。</div>

## 冻结协议 {#concepts}

| 项目 | 冻结值 |
|---|---|
| 原始时点 | 820 |
| Train | [0, 400) |
| Embargo 1 | [400, 420) |
| Validation | [420, 560) |
| Embargo 2 | [560, 580) |
| Test | [580, 819) |
| 标签 horizon | 1 日 |
| 候选数 | 6 |
| 成本 | 每单位 L1 仓位变化 5 bps |
| 选择规则 | 最大 validation net annualized Sharpe |

Train 在本最小实验中用于冻结特征生成机制；候选规则没有根据 test 调整。真实 ML 项目还需在 train 内拟合参数、validation 调参，并对 test 完全封存。

## 方法与数学形式（Methods & Mathematical Form） {#methods}

候选 \(j\) 的净收益：

\[
r_{j,t}^{net}=p_{j,t}r_{t+1}-c|p_{j,t}-p_{j,t-1}|.
\]

只在 validation 计算：

\[
j^*=\arg\max_j\frac{\bar r_{j,val}}{s_{j,val}}\sqrt{252}.
\]

选定 \(j^*\) 后只对它计算 test 指标。六个候选的 validation 朴素双侧 p 值使用 Bonferroni：

\[
p_{adj}=\min(1,6p_{naive}).
\]

Bonferroni 不修复策略依赖、非正态、序列相关或未登记的人工试验；它只是实验家族规模被记录后的最小校正。

## 实验账本 {#ledger}

| candidate | Validation net Sharpe | 状态 |
|---|---:|---|
| signal | 1.8585 | failed_validation |
| lagged | -0.5182 | failed_validation |
| blend | 2.1998 | selected |
| high_threshold | 1.5401 | failed_validation |
| noise | 1.0135 | failed_validation |
| reversed | -2.5899 | failed_validation |

即使 noise 候选在有限 validation 中得到正 Sharpe，也没有被删除；这正是多重搜索可能产生偶然高分的可见证据。

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
freeze_splits(train=(0,400), validation=(420,560), test=(580,819), embargo=20)
freeze_candidates_and_cost_model(candidate_ids, cost_bps=5)
ledger = []
for candidate in candidates:
    validation_net = evaluate_after_cost(candidate, validation_only)
    ledger.append(candidate_id, validation_net, status="evaluated_validation")
selected = argmax_validation_net_sharpe(ledger)
mark_all_others_failed_but_preserve_records(ledger)
test_result = evaluate_once_after_cost(selected, frozen_test)
apply_multiple_testing_disclosure(ledger)
```

实现见 [`p5_leakage_free_alpha.py`](p5_leakage_free_alpha.py)，结果见 [`p5_leakage_free_alpha_results.json`](p5_leakage_free_alpha_results.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/projects/p5_leakage_free_alpha/p5_leakage_free_alpha.py
python quant_finance/projects/p5_leakage_free_alpha/test_p5_leakage_free_alpha.py -v
```

`blend` 由 validation 选中：validation net Sharpe 2.1998，朴素 p=0.1011，Bonferroni p=0.6065，因此没有统计发现可宣称。冻结 test 的成本后结果：日均收益 0.000506、日波动 0.007299、年化 Sharpe 1.1003、朴素 p=0.2839。test 明显低于 validation，展示选择与有限样本乐观偏差。

## 失败案例与审计边界 {#comparison}

| 失败 | 本项目防护 | 仍未解决 |
|---|---|---|
| 反复看 test | 只对选中候选输出 test | 人工运行历史仍需外部账本/权限控制 |
| 删除失败候选 | 六个候选全部保存 | 未登记的灵感仍可能遗漏 |
| 忽略成本 | 5 bps×仓位变化 | 非线性冲击和容量未建模 |
| 只报 Sharpe | 同时报均值、波动、p 值 | p 值未作 HAC/Bootstrap |
| 多重检验 | 对六候选 Bonferroni | 策略相关与更广实验族 |
| 单一 DGP | 明确合成边界 | 不支持真实市场外推 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| P5-Q01 | 为什么需要 validation？ | 调参与选择不能使用 test。 |
| P5-Q02 | test 应打开几次？ | 协议上一次，之后不再调模型。 |
| P5-Q03 | embargo 在哪里？ | train/validation 和 validation/test 之间。 |
| P5-Q04 | 失败候选为何保留？ | 反映真实搜索空间和选择偏差。 |
| P5-Q05 | 选择规则是什么？ | 最大 validation 成本后年化 Sharpe。 |
| P5-Q06 | Bonferroni p 如何计算？ | min(1, 候选数×朴素 p)。 |
| P5-Q07 | Bonferroni 能修复序列相关吗？ | 不能，需 HAC/Bootstrap。 |
| P5-Q08 | noise 正 Sharpe 说明什么？ | 有限样本和多重搜索会产生偶然高分。 |
| P5-Q09 | test Sharpe 1.10 能证明 alpha 吗？ | 不能，合成数据且 p 值不显著。 |
| P5-Q10 | 真实研究还需什么？ | point-in-time 数据、容量、完整实验系统和独立复核。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| P5-Q01 | validation 承担模型选择，保护 test。 |
| P5-Q02 | 选型冻结后一次。 |
| P5-Q03 | [400,420) 和 [560,580)。 |
| P5-Q04 | 让分母和失败搜索可审计。 |
| P5-Q05 | validation net Sharpe 最大。 |
| P5-Q06 | 本项目为 \(\min(1,6p)\)。 |
| P5-Q07 | 不能；需依赖稳健推断。 |
| P5-Q08 | 无信号候选也可偶然表现良好。 |
| P5-Q09 | 不能；无真实数据且朴素 p=0.2839。 |
| P5-Q10 | 真实点时数据、成本冲击、容量、权限和独立复核。 |

## 风险与后续建议（Risks & Next） {#risks}

- 本地 JSON 账本不能阻止研究者删除文件或重跑 seed；生产系统需 append-only 记录、test 访问控制和审查人。
- 标签 horizon 为 1，未展示复杂重叠标签的 fold-level purging；M10 已提供相应基础。
- 下一 slice G19/M11 将系统化回测统计、数据窥探、策略衰减和两种回测引擎差异。

## 参考文献（References） {#references}

1. [1] Halbert White, “A Reality Check for Data Snooping,” *Econometrica*, 2000. [链接](https://doi.org/10.1111/1468-0262.00152)
2. [2] Peter Carr and Marcos López de Prado, “Determining Optimal Trading Rules without Backtesting,” 2014. [链接](https://arxiv.org/abs/1408.1159)
