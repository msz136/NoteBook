---
title: P6 LEAN 事件驱动回测：订单生命周期、费用与滑点重建
subtitle: 冻结官方 revision，交付 QCAlgorithm 骨架，并诚实记录本机无 LEAN/.NET 运行时
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · LEAN Event-Driven Backtest
---

# P6 LEAN 事件驱动回测：订单生命周期、费用与滑点重建

## 问题（Question） {#question}

如何把研究信号迁移到 LEAN 的事件、订单和成交语义中？当本机没有 LEAN CLI 与 .NET 时，哪些内容可以真实验证，哪些必须保持 `NOT RUN`？本项目交付一个 `QCAlgorithm` 兼容骨架和独立本地订单账本，验证提交、部分成交、完成、费用、滑点、现金和持仓守恒。

## 背景与动机（Background & Motivation） {#background}

LEAN 是 QuantConnect 的开源事件驱动算法交易引擎，支持研究、回测和实盘接口。[1] 本项目在 2026-07-22 通过 `git ls-remote` 冻结官方仓库 HEAD `153d0b7427a918063a018ec18964ddf450edc125`。环境检查结果为 `LEAN_CLI_NOT_FOUND`、`DOTNET_NOT_FOUND`，因此没有生成或声称任何 LEAN 回测统计。

<div class="evidence"><strong>证据边界：</strong>`lean_momentum_algorithm.py` 已通过 Python AST 语法检查，但由于 `AlgorithmImports` 只存在于 LEAN 环境，API 兼容性和引擎运行均未验证。本地事件账本是独立 deterministic harness，不是 LEAN 替代品。官方 HEAD 是访问时状态，不等于长期稳定版本。</div>

## 冻结环境与产物 {#concepts}

| 项目 | 状态 |
|---|---|
| LEAN CLI | NOT FOUND |
| .NET SDK/runtime | NOT FOUND |
| 官方仓库 HEAD | `153d0b7427a918063a018ec18964ddf450edc125` |
| QCAlgorithm 骨架 | 已创建、AST parse PASS |
| LEAN compile/backtest | NOT RUN |
| 本地事件账本 | PASS |
| 真实市场数据/成交 | 未使用 |

产物包括 [`lean_momentum_algorithm.py`](lean_momentum_algorithm.py)、[`local_event_ledger.py`](local_event_ledger.py) 和 [`p6_lean_event_results.json`](p6_lean_event_results.json)。

## LEAN 策略契约 {#lean-contract}

策略骨架冻结：SPY 日线、2020 年样例区间、初始现金 100,000、六期滚动窗口、五日动量为正时目标仓位 50%，否则空仓。配置示例固定 `ConstantFeeModel(1.0)` 和 `ConstantSlippageModel(0.0002)`，并在 `on_order_event` 记录部分成交/完成事件。

这只是接口候选。真正运行前必须在冻结 revision 下确认 Python API 命名、模型构造器、数据订阅、warm-up、拆股分红、时区和历史数据许可。

## 订单生命周期与账本 {#methods}

订单状态至少包括：

\[
New\rightarrow Submitted\rightarrow PartiallyFilled\rightarrow Filled,
\]

并允许 CancelPending、Canceled、Invalid/Rejected。买入成交对现金和持仓的更新：

\[
Cash_{new}=Cash_{old}-qP_{fill}-Fee,
\qquad Position_{new}=Position_{old}+q.
\]

卖出时 \(q\) 的方向相反。账本必须逐 fill 更新，不能在订单提交时假设全额成交。

本地 harness 模拟：100 股买单分 40/60 两次成交，随后 100 股卖单一次成交；每个 fill 收费 1，买卖方向各施加 2 bps 不利滑点。

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
freeze_lean_commit_and_runtime_versions()
algorithm = load_qcalgorithm_skeleton()
subscribe_data_and_define_point_in_time_signal()
configure_fee_slippage_fill_and_brokerage_models()
submit_orders_only_after_signal_is_available()
for order_event in engine_events:
    update_cash_position_fee_and_order_state(order_event)
reconcile_engine_orders_fills_holdings_cash_and_statistics()
mark_NOT_RUN_if_lean_cli_or_data_runtime_is_missing()
```

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/projects/p6_lean_event_backtest/local_event_ledger.py
python quant_finance/projects/p6_lean_event_backtest/test_local_event_ledger.py -v
```

| 指标 | 本地账本结果 |
|---|---:|
| 初始现金 | 100,000.00 |
| 最终现金 | 100,192.96 |
| 最终持仓 | 0 |
| fill 数 | 3 |
| 总费用 | 3.00 |
| 费用/滑点后已实现 P&L | 192.96 |

测试确认包含 `partially_filled`，两个订单最终各有一个 `filled`，最终持仓归零，费用等于三次 fill×1，算法文件可被 AST 解析且包含 `QCAlgorithm` 与 `on_order_event`。

## LEAN 与本地证据对照 {#comparison}

| 能力 | 本地 harness | LEAN 引擎 |
|---|---|---|
| 确定性状态转换 | 已验证 | 未运行 |
| 部分成交与现金守恒 | 已验证固定场景 | 未运行 |
| `QCAlgorithm` API | 仅静态骨架 | 未编译/未执行 |
| 数据订阅/公司行动 | 不支持 | 未验证 |
| 官方 fill/fee/slippage 模型 | 不支持 | 未验证 |
| 统计与结果 JSON | 本地自定义 | 未生成 |

不能把本地 P&L 与 LEAN 回测结果等同。P6 的诚实退出状态是：事件账本 slice 完成，LEAN runtime integration 仍为开放边界。

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| P6-Q01 | 冻结的 LEAN revision？ | 给出完整 40 字符 commit。 |
| P6-Q02 | 为什么未运行 LEAN？ | CLI 和 .NET 均不存在。 |
| P6-Q03 | AST 通过能证明 API 可用吗？ | 不能，只证明 Python 语法。 |
| P6-Q04 | 部分成交如何更新账本？ | 每个 fill 分别更新现金/持仓/费用。 |
| P6-Q05 | 滑点方向如何设置？ | 买入价格上调、卖出价格下调。 |
| P6-Q06 | 费用为何按 fill 而非 order？ | 本示例模型定义为每次成交收费。 |
| P6-Q07 | 最终持仓为何为零？ | 买入 100 后卖出 100。 |
| P6-Q08 | LEAN 运行前还需核验什么？ | API、数据、时区、公司行动和模型配置。 |
| P6-Q09 | 本地 P&L 能否称 LEAN 结果？ | 不能。 |
| P6-Q10 | 下一步集成证据是什么？ | 冻结 runtime 下成功编译/回测及结果哈希。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| P6-Q01 | `153d0b7427a918063a018ec18964ddf450edc125`。 |
| P6-Q02 | 环境输出 `LEAN_CLI_NOT_FOUND`、`DOTNET_NOT_FOUND`。 |
| P6-Q03 | 不能；缺少 `AlgorithmImports` 和引擎类型检查。 |
| P6-Q04 | 每次成交立即记数量、价格、现金和费用。 |
| P6-Q05 | 对交易者不利方向应用。 |
| P6-Q06 | 三个 fill 因而收三次固定费用。 |
| P6-Q07 | +40+60-100=0。 |
| P6-Q08 | 至少 API revision、数据、时区、公司行动、fee/fill/slippage。 |
| P6-Q09 | 不能，本地 harness 不是 LEAN。 |
| P6-Q10 | 引擎退出码、日志、订单/fill/统计和产物哈希。 |

## 风险与后续建议（Risks & Next） {#risks}

- `ConstantFeeModel`、`ConstantSlippageModel` 及 snake_case API 需要在冻结 LEAN Python 环境中实际编译确认。
- 示例只包含一个证券和固定费用/滑点，不含公司行动、现金利息、保证金、借券、分红或真实数据。
- 下一 slice G21/P7 将建立 Qlib 或自建研究生产管线；当前环境若同样缺包，将用可执行本地 stage manifest 验证数据—特征—训练—回测—报告闭环，并明确 Qlib 未运行。

## 参考文献（References） {#references}

1. [1] QuantConnect, “LEAN,” official repository. [链接](https://github.com/QuantConnect/Lean)
2. [2] QuantConnect, “LEAN Documentation.” [链接](https://www.quantconnect.com/docs/v2/lean-engine/getting-started/lean-cli)
