---
title: 研究复现与模型治理：实验追踪、CI、监控、审计与退役
subtitle: M12 · 让模型从“能跑”进入可复核、可批准、可暂停和可恢复状态
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Reproducibility and Model Governance
---

# 研究复现与模型治理：实验追踪、CI、监控、审计与退役

## 问题（Question） {#question}

一个研究模型何时可以被别人复现、被风险人员批准、被监控和被安全退役？如何把数据/代码/环境版本、实验参数、批准角色、风险限额、故障演练和 rollback 证据连成一条审计链？本模块创建可执行治理记录验证器，并用负向测试拒绝缺 owner 或未批准部署。

## 背景与动机（Background & Motivation） {#background}

Wilson 等人将数据、软件、版本和项目组织视为可复现计算的基本实践；NIST AI RMF 将治理、映射、测量和管理作为风险生命周期；SR 11-7 则强调模型开发、验证、治理和持续监控。[1–3] 金融模型还需保留数据许可、点时性、成本、容量和人工 override 证据，不能把 Git commit 等同于风险批准。

<div class="evidence"><strong>证据边界：</strong>来源支撑治理原则和生命周期，不替代机构政策/法律意见。`m12_model_governance_record.json` 是本地合成模板，`m12_validate_governance.py` 是本地规则验证器；它们不代表生产模型已获批准或部署。</div>

## 治理对象与角色 {#concepts}

| 对象 | 必须记录 | 失败后果 |
|---|---|---|
| 模型身份 | model_id、目的、owner、版本 | 无法归责/复现 |
| 数据 | source、revision、许可、hash、point-in-time | 结果无法重建或侵权 |
| 代码/环境 | commit、锁文件、OS、包、随机算法 | “在我机器上能跑” |
| 验证 | 指标、基准、压力、失败和独立 reviewer | 自我批准 |
| 运行 | freshness、drift、P&L、风险限额、告警 | 失效后继续下单 |
| 退役 | trigger、rollback artifact、审批和通知 | 无法安全停止 |

独立验证人不能与模型 owner 相同；生产批准是显式状态，不应由“测试通过”自动推导。

## 复现与实验追踪 {#repro}

一次运行的最小身份：

\[
RunID=H(data\_revision,code\_revision,environment\_lock,config,seed).
\]

每个 stage 应记录输入/输出 hash、命令、开始/结束、状态和日志位置。实验追踪必须保存失败和被否决的 run；只保存最佳模型会破坏多重检验和审计。

## CI 与验证门 {#ci}

CI 至少分层：

1. schema、单位、point-in-time 和本地链接检查；
2. 纯函数/估计器/订单账本单元测试；
3. 小 fixture 端到端 smoke；
4. 结果 hash/指标基线 drift 检查；
5. 安全、依赖、许可和密钥扫描；
6. 人工 review、批准和发布签名。

绿色 CI 只证明定义的测试通过，不证明模型识别、收益、容量或监管合规。

## 监控、事件与退役 {#monitoring}

监控应覆盖：数据新鲜度、缺失、分布/特征漂移、预测校准、成交/成本、P&L、回撤、暴露、限额和系统健康。阈值触发 warning、降级、阻断下单或 rollback；每类动作需 owner、SLA 和通知路径。

事件演练至少验证：

\[
Detect\rightarrow Notify\rightarrow Block\rightarrow Rollback\rightarrow Verify\rightarrow Review.
\]

“模型停止”不等于“风险消失”：需要现金、未成交订单、持仓、借券、融资、数据修订和恢复版本的完整检查。

## 治理记录与状态机 {#math}

推荐状态：`draft → validated_not_deployed → approved → deployed → degraded/blocked → retired`。禁止 `deployed` 没有 production approval。每次状态转移要记录人、时间、证据和理由。

本地验证规则：

| 检查 | 规则 |
|---|---|
| required_fields | 身份、版本、指标、限额、监控、rollback、事件演练齐全 |
| independent_roles | owner 与 reviewer 不同 |
| production_approval | deployed 必须显式 production=true |
| incident_drill | detected/blocked/notified/recovered 全为 true |
| rollback_defined | action 与 artifact_revision 非空 |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
record = load_governance_record(model_id)
validate_schema_roles_versions_limits_monitoring_and_rollback(record)
run_ci_and_reproducibility_smoke(record.code_revision, record.environment_hash)
if record.status == "deployed":
    require(record.approvals.production is True)
simulate_stale_data_incident()
assert orders_blocked and owner_notified and rollback_verified
append_audit_event(actor, transition, evidence_hash)
```

实现见 [`m12_validate_governance.py`](../tools/m12_validate_governance.py)，模板见 [`m12_model_governance_record.json`](../data/m12_model_governance_record.json)，验证输出见 [`m12_model_governance_validation.json`](../data/m12_model_governance_validation.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/tools/m12_validate_governance.py
python quant_finance/data/test_m12_governance.py -v
```

有效记录验证 `PASS`：required fields、独立角色、未批准部署阻断、rollback 和 stale-data 事件演练全部通过。负向测试删除 owner 或将 status 改为 deployed 但不批准，均返回 `FAIL`。这是规则覆盖证据，不是生产审批。

## 治理对比与失败案例 {#comparison}

| 失败 | 为什么危险 | 防护 |
|---|---|---|
| 只有代码 commit | 数据/环境/参数仍漂移 | RunID 与多版本 hash |
| 只保存最佳实验 | 多重检验不可见 | append-only 实验账本 |
| owner 自己批准 | 独立验证缺失 | reviewer/审批分离 |
| 监控只有 P&L | 数据/成本/暴露先失效 | 多层运行和风险指标 |
| 告警无动作 | 风险继续扩大 | block/rollback/SLA |
| rollback 无 artifact | 无法恢复已知版本 | immutable artifact 与演练 |
| 测试绿即部署 | 测试范围有限 | 显式 production approval |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| M12-Q01 | RunID 应包含什么？ | 数据、代码、环境、配置、seed。 |
| M12-Q02 | 为什么保存失败 run？ | 审计搜索空间和多重检验。 |
| M12-Q03 | owner/reviewer 为何分离？ | 独立验证减少自我确认。 |
| M12-Q04 | deployed 需要什么？ | 显式 production approval。 |
| M12-Q05 | 监控哪些类别？ | 新鲜度、漂移、校准、成本、P&L、暴露、系统。 |
| M12-Q06 | 事件响应顺序？ | detect→notify→block→rollback→verify→review。 |
| M12-Q07 | rollback 记录什么？ | 动作、目标 artifact revision、验证证据。 |
| M12-Q08 | CI 绿灯证明什么？ | 定义测试通过，不证明收益/合规。 |
| M12-Q09 | 为什么需要环境 hash？ | 包/OS/算法差异影响结果。 |
| M12-Q10 | 数据修订如何治理？ | 新 revision/hash，不静默覆盖。 |
| M12-Q11 | stale data 事件如何演练？ | 检测、阻断订单、通知、恢复和验证。 |
| M12-Q12 | 模型退役为何不止删代码？ | 需处理持仓、订单、融资、数据和审计。 |
| M12-Q13 | risk limit 与 metric 区别？ | 限额是动作边界，metric 是观测量。 |
| M12-Q14 | 生产批准可否由测试自动给？ | 不可，需权限分离。 |
| M12-Q15 | drift 阈值如何使用？ | warning/blocked 动作和 owner/SLA 预先定义。 |
| M12-Q16 | 合成模板支持什么？ | 验证字段和规则路径。 |
| M12-Q17 | 审计事件最少字段？ | actor、transition、time、reason、evidence hash。 |
| M12-Q18 | 模型风险与数据风险差异？ | 模型错设/实现 vs 输入/可见性/质量。 |
| M12-Q19 | 为什么要锁文件？ | 复现依赖和安全更新可追踪。 |
| M12-Q20 | 何时暂停治理结论？ | 角色、版本、事件或 rollback 闸门缺失。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| M12-Q01 | hash(data, code, env, config, seed)。 |
| M12-Q02 | 否则无法知道搜索分母和失败边界。 |
| M12-Q03 | reviewer 不等于 owner。 |
| M12-Q04 | production=true 的显式批准。 |
| M12-Q05 | 数据、特征、预测、执行、风险和系统健康。 |
| M12-Q06 | 六步状态机。 |
| M12-Q07 | 动作＋不可变目标版本＋恢复检查。 |
| M12-Q08 | 只证明测试范围内不失败。 |
| M12-Q09 | 环境改变会改变数值和安全。 |
| M12-Q10 | 建新版本并保留旧工件。 |
| M12-Q11 | 发现、阻断、通知、回滚和复核。 |
| M12-Q12 | 还要处置订单/持仓/融资和审计。 |
| M12-Q13 | metric 观测，limit 触发动作。 |
| M12-Q14 | 不可，审批是权限和责任决策。 |
| M12-Q15 | 每阈值绑定动作、owner 和 SLA。 |
| M12-Q16 | 规则/字段的本地验证。 |
| M12-Q17 | actor、transition、time、reason、evidence。 |
| M12-Q18 | 模型结构风险 vs 输入版本/质量/时点风险。 |
| M12-Q19 | 依赖版本、漏洞和升级可重建。 |
| M12-Q20 | 任一治理证据不可验证。 |

## 风险与后续建议（Risks & Next） {#risks}

- 验证器是最小规则集，不覆盖机构权限系统、密钥管理、隐私、监管报告或法律意见。
- 监控阈值是示例值，不能直接作为生产限额。
- 下一 slice G23 将冻结 Capstone 论文、数据、指标、协议与复现边界；G24 再执行并形成最终答辩材料。

## 参考文献（References） {#references}

1. [1] Greg Wilson et al., “Good Enough Practices in Scientific Computing,” 2017. [链接](https://doi.org/10.1371/journal.pcbi.1005510)
2. [2] NIST, “AI Risk Management Framework (AI RMF 1.0),” 2023. [链接](https://www.nist.gov/itl/ai-risk-management-framework)
3. [3] Federal Reserve and OCC, “Supervisory Guidance on Model Risk Management (SR 11-7),” 2011. [链接](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm)
