---
title: P7 研究生产管线：数据、特征、训练、回测与报告哈希链
subtitle: 冻结 Qlib revision，在无 Qlib 环境下交付可恢复的本地 stage manifest
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Research Production Pipeline
---

# P7 研究生产管线：数据、特征、训练、回测与报告哈希链

## 问题（Question） {#question}

如何让量化研究从一组 Notebook 单元格变成可恢复、可审计的生产管线？本项目冻结 Qlib 官方 revision，检查本机安装状态，并实现 deterministic data→feature→train→backtest→report 五阶段流水线；每阶段记录输入和输出 SHA-256，删除中间回测产物后可逐字节重建。

## 背景与动机（Background & Motivation） {#background}

Microsoft Qlib 提供面向量化研究的 AI/数据工作流和实验基础设施。[1] 本项目在 2026-07-22 冻结官方仓库 HEAD `d5379c520f66a39953bad76234a7019a72796fd0`，但环境检查为 `QLIB_NOT_FOUND`。因此交付物是自建最小 stage contract，不是 Qlib 实验，也不声称 Qlib API 兼容。

<div class="evidence"><strong>证据边界：</strong>五阶段执行、哈希链、确定性和删除中间产物后的恢复均为本地证据。数据为合成价格，模型为 NumPy 线性回归，回测为简化净收益。没有真实数据、Qlib、实验追踪服务、容器或部署。</div>

## 环境与产物契约 {#concepts}

| 项目 | 冻结状态 |
|---|---|
| Qlib Python package | NOT FOUND |
| Qlib official HEAD | `d5379c520f66a39953bad76234a7019a72796fd0` |
| 数据 | 固定 seed 生成 500 期价格 |
| 特征 | 1 日收益、5 日动量 |
| 模型 | 前 349 个训练样本的线性回归 |
| 回测 | 后续冻结区间、5 bps 换手成本 |
| 报告 | JSON 摘要和证据边界 |
| Manifest | stage 状态、输入/输出路径与 SHA-256 |

## Stage DAG 与哈希链 {#methods}

```text
01_data.json
    -> 02_features.json
        -> 03_model.json
            -> 04_backtest.json
                -> 05_report.json
                    -> pipeline_manifest.json
```

对阶段 \(k\)，产物哈希：

\[
h_k=SHA256(bytes(output_k)).
\]

下游产物内容嵌入上游哈希，manifest 再记录每条边。若上游字节变化，下游哈希必须变化；若删除中间产物并以相同代码、seed 和输入重跑，所有字节和 manifest 应恢复一致。

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
data = generate_or_load_versioned_data(seed, source_hash)
features = build_features(data, available_at_contract)
model = fit_train_only(features, train_end=350)
backtest = evaluate_after_cost(model, frozen_test)
report = summarize_metrics_and_evidence_boundary(backtest)
manifest = hash_every_input_output_and_record_stage_status()
assert_delete_and_rebuild("04_backtest.json") == original_bytes
```

实现见 [`run_pipeline.py`](run_pipeline.py)，manifest 见 [`pipeline_manifest.json`](pipeline_manifest.json)，生成产物位于 [`artifacts/05_report.json`](artifacts/05_report.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/projects/p7_research_pipeline/run_pipeline.py
python quant_finance/projects/p7_research_pipeline/test_pipeline.py -v
```

| Stage | 状态 | 输出 SHA-256 前 12 位 |
|---|---|---|
| data | PASS | `9cfc6fe858bf` |
| feature | PASS | `b0b575585b69` |
| train | PASS | `06208613033b` |
| backtest | PASS | `0cea7ff95b52` |
| report | PASS | `00115f92a789` |

测试先执行全管线并保存所有字节，删除 `04_backtest.json` 后重跑，再逐项比较五个产物和 manifest；结果完全一致。测试还验证 Qlib 状态为未安装、五个 stage 均为 PASS 且顺序固定。

## Qlib 与本地管线对照 {#comparison}

| 能力 | 本地 P7 | Qlib |
|---|---|---|
| 五阶段 DAG | 已执行 | 未运行 |
| 输入/输出哈希 | 已实现 | 未验证其原生机制 |
| 数据/特征缓存 | 每次确定性重算 | 未运行 |
| 模型/Recorder | JSON 自定义 | 未运行 |
| Dataset/Handler | 不兼容 | 未运行 |
| 真实市场数据 | 无 | 未配置 |

P7 证明的是可审计 stage contract，而不是“已完成 Qlib 部署”。后续安装 Qlib 时，应把相同数据、切分和指标接入官方 Dataset/Model/Recorder，并对照产物。

## 失败恢复与治理 {#recovery}

| 失败 | 检测 | 恢复 |
|---|---|---|
| 上游文件变更 | SHA 不匹配 | 使所有依赖 stage 失效并重算 |
| 中间文件缺失 | manifest 路径不存在 | 从最近可信上游重建 |
| 随机性漂移 | 同配置字节不同 | 冻结 seed、包和算法版本 |
| 数据修订 | source hash 变化 | 新建版本，不覆盖旧 run |
| 测试泄漏 | split contract 失败 | 阻止 backtest/report stage |
| 报告陈旧 | report 输入 hash 不匹配 | 重新生成并审查 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| P7-Q01 | 冻结的 Qlib revision？ | 给出完整 40 字符 commit。 |
| P7-Q02 | 本机是否运行 Qlib？ | 否，package 未安装。 |
| P7-Q03 | 五个 stage 顺序？ | data、feature、train、backtest、report。 |
| P7-Q04 | 哈希链用途？ | 绑定下游结果和确切上游字节。 |
| P7-Q05 | 如何验证恢复？ | 删除中间产物、重跑、逐字节比较。 |
| P7-Q06 | deterministic 是否等于有效策略？ | 不是，只表示可重放。 |
| P7-Q07 | 数据更新如何处理？ | 新版本/hash，不静默覆盖。 |
| P7-Q08 | manifest 至少记录什么？ | stage、状态、输入/输出路径与 hash。 |
| P7-Q09 | 本地管线能否称 Qlib？ | 不能。 |
| P7-Q10 | 生产化还缺什么？ | 环境锁、真实数据、CI、追踪、权限和监控。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| P7-Q01 | `d5379c520f66a39953bad76234a7019a72796fd0`。 |
| P7-Q02 | `QLIB_NOT_FOUND`。 |
| P7-Q03 | data→feature→train→backtest→report。 |
| P7-Q04 | 任一输入变化可沿依赖边传播失效。 |
| P7-Q05 | 删除 `04_backtest.json` 后重建字节一致。 |
| P7-Q06 | 不是；还需数据和经济/统计验证。 |
| P7-Q07 | 新建不可变版本并保留旧产物。 |
| P7-Q08 | 名称、状态、路径、输入 hash、输出 hash。 |
| P7-Q09 | 不能，自建 contract 不等于 Qlib API。 |
| P7-Q10 | 锁文件/容器、真实 point-in-time 数据、CI、追踪、访问控制和监控。 |

## 风险与后续建议（Risks & Next） {#risks}

- 当前脚本每次全量重算，未实现基于 DAG 的缓存命中、并发锁和原子提交。
- JSON 适合小 fixture，不适合真实行情规模；真实管线需列式存储、分区、catalog 和权限。
- 下一 slice G22/M12 将整合研究复现、实验追踪、CI、模型风险、监控和治理，形成生产/审计模块。

## 参考文献（References） {#references}

1. [1] Microsoft, “Qlib,” official repository. [链接](https://github.com/microsoft/qlib)
2. [2] Greg Wilson et al., “Good Enough Practices in Scientific Computing,” 2017. [链接](https://doi.org/10.1371/journal.pcbi.1005510)
