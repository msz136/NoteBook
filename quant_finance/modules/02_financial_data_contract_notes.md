---
title: 金融数据契约：收益口径、公司行动、交易日历与 Point-in-Time
subtitle: M02 · 在任何回归或回测前，先证明数据在当时可得且字段含义一致
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Financial Data Contract
---

# 金融数据契约：收益口径、公司行动、交易日历与 Point-in-Time

## 问题（Question） {#question}

为什么同一只资产会有价格收益、总收益、复权价格和不同版本的因子数据？为什么一个看似合理的 join 可能把未来分类、修订财报或退市信息泄漏到过去？本模块建立一个可执行的数据契约，并用不含受限市场数据的合成 fixture 验证字段、时间和收益计算。

## 背景与动机（Background & Motivation） {#background}

FRED 提供公开宏观序列与 API 入口，Kenneth French Data Library 提供因子与投资组合数据及历史档案；它们适合教学和研究原型，但字段频率、修订、许可和点时属性仍需逐项确认。[1][2] Princeton 金融课程把金融会计、金融数据统计、资产定价和金融计量并列为核心内容，说明数据定义不是编程前的附属工作，而是金融分析对象本身的一部分。[3]

Wilson 等人强调组织数据、记录步骤、版本跟踪和项目结构是可复现计算的基本实践。[4] 本仓库因此把数据字典、获取时间、版本、哈希、许可和转换规则写入数据契约；`data/` 不提交受限大数据。

<div class="evidence"><strong>证据边界：</strong>FRED/French 官方入口支撑公开数据来源的存在和使用方向；本模块的字段 schema、合成 fixture、审计器和示例收益是本地设计/本地证据。ALFRED、SEC、CRSP/Compustat/TAQ 的具体字段与许可不在本切片中假定已核验。</div>

## 基础概念与术语 {#concepts}

| 术语 | 首次定义 | 研究影响 |
|---|---|---|
| 交易会话（trading session） | 按交易所日历定义的可交易日期/时段 | 缺失周末不能直接填 0 收益；跨时区会改变排序 |
| 观测时间（observed_at） | 价格或事件实际记录发生的时间 | 不等于数据发布/可见时间 |
| 可用时间（available_at） | 研究管线最早能看到该记录的时间 | 控制信息泄漏的关键字段 |
| 研究快照（asof_at） | 本次特征或回测重放所模拟的时间 | 必须满足 `available_at <= asof_at` |
| 价格收益（price return） | 只使用价格变化的回报 | 不包含现金分红 |
| 总收益（total return） | 价格变化加现金分配的回报 | 需要统一每股、除息和复权口径 |
| 点时（point-in-time） | 只使用当时已发布且当时有效的数据 | 防止修订、重分类、未来成分股泄漏 |
| 幸存者偏差（survivorship bias） | 只保留今天仍存在的资产/公司 | 历史资产池和收益被系统性筛选 |
| 许可（license） | 数据使用和再分发的法律边界 | 能下载不等于能提交到 Git 或发布 |

## 方法与项目拆解（Methods） {#methods}

### 数据来源分层 {#source-tiers}

| 层级 | 例子 | 适合做什么 | 必须补充的证据 |
|---|---|---|---|
| 官方宏观/因子 | FRED、French Data Library | 教学、公开因子复现、宏观研究原型 | 频率、修订、下载日期、许可证 |
| 公司披露 | SEC EDGAR/XBRL（本切片待复核） | 财报和事件研究 | 发布时点、修订、字段映射、速率限制 |
| 学术数据库 | CRSP、Compustat、TAQ（通常机构许可） | 退市收益、公司事件、微观结构 | 订阅、再分发、点时字段和版本 |
| 交易/供应商 | 交易所授权源、券商/API | 实时/生产执行 | SLA、时钟、公司行动、成本和权限 |

### 最小可审计面板 {#panel-schema}

本模块的合成样本见 [`m02_price_panel_fixture.csv`](../data/m02_price_panel_fixture.csv)，字段契约见 [`m02_data_contract.md`](../data/m02_data_contract.md)。真实数据应至少保留：

1. 标识：稳定 `symbol`、供应商标识、必要时的实体/证券映射版本；
2. 时间：`session_date`、`observed_at`、`available_at`、研究 `asof_at`、时区和交易日历；
3. 价格与行动：raw close、adjusted close、现金分红、拆股因子、币种和单位；
4. 质量：缺失、重复、异常值、停牌/退市标记和处理日志；
5. 来源：source id、获取日期、版本/哈希、许可证、转换脚本和参数。

## 数学形式与训练目标（Mathematical Form） {#math}

### 价格收益与总收益 {#returns}

令 \(P_t^{raw}\) 是未经公司行动调整的每股价格，\(D_t\) 是同一每股口径下的现金分红。价格收益与总收益分别为：

\[
R_t^{price}=\frac{P_t^{raw}}{P_{t-1}^{raw}}-1,
\qquad
R_t^{total}=\frac{P_t^{raw}+D_t}{P_{t-1}^{raw}}-1.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>价格收益回答“报价本身怎么变”，总收益回答“持有资产并收到现金分配后的回报”。fixture 审计器同时输出两列；若有拆股，raw price 的跳变不能直接当经济损失/收益，应使用明确的 adjusted close 或公司行动转换。</div>

### 复权序列的边界 {#adjustment}

若供应商给出同口径的调整价格 \(P_t^{adj}\)，可计算：

\[
R_t^{adj}=\frac{P_t^{adj}}{P_{t-1}^{adj}}-1.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>\(P^{adj}\) 的调整因子方向、除息/除权日期和回溯范围必须有文档与样例。`close_adjusted` 不是一个可以无条件信任的列名；审计器保留 raw、adjusted、分红和 split_factor 让差异可追踪。</div>

### Point-in-time 连接 {#pit}

对研究快照 \(a\)，一条记录只有在：

\[
\operatorname{usable}(x,a)=\mathbf 1\{\operatorname{available\_at}(x)\le a\}=1
\]

时才可以进入特征或回测状态。

<div class="note"><strong>变量、直觉与实现映射：</strong>这里的比较对象是可见时间和研究快照，不是事件发生日。fixture 专门放入“观测后发布”的记录，并用 `asof_at` 判定可用；真实数据若只有 `event_date` 而没有发布/版本时间，必须标注未验证。</div>

### 交易会话与年化 {#calendar}

若一年内有效交易会话数为 \(N_{year}\)，日收益序列的年化波动率常写为：

\[
\hat\sigma_{annual}=\operatorname{sd}(r_{daily})\sqrt{N_{year}}.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>年化因子依赖频率、交易日历和独立/弱依赖近似；不能把 252 当成跨市场、跨时期、跨资产的无条件常数。数据契约要记录日历和缺失会话处理。</div>

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
def build_point_in_time_panel(raw_rows, asof_at):
    # 1. Parse UTC timestamps and sort within each stable security identifier.
    rows = parse_and_sort(raw_rows, keys=["symbol", "session_date"])

    # 2. Reject missing/duplicate sessions, non-positive prices, and unknown license class.
    validate_schema(rows)

    # 3. Keep only fields available by the research snapshot; do not substitute event_date.
    visible = [row for row in rows if row["available_at"] <= asof_at]

    # 4. Compute price/total/adjusted returns only within an entity and adjacent sessions.
    returns = compute_returns(visible, fields=["close_raw", "close_adjusted", "cash_dividend"])

    # 5. Persist source version, calendar, transformation, hashes, and dropped-row reasons.
    return attach_provenance(returns, asof_at=asof_at)
```

真实 fixture 审计实现见 [`audit_price_panel.py`](../tools/audit_price_panel.py)，其输出保存于 [`m02_price_panel_audit.json`](../data/m02_price_panel_audit.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

### Fixture 审计结果 {#fixture-results}

命令：

```powershell
# Run the schema, timestamp, value, ordering, and return-field audit.
python quant_finance/tools/audit_price_panel.py

# Run positive and future-availability negative tests.
python quant_finance/data/test_audit_price_panel.py -v
```

本地结果为 `PASS`：7 行合成记录、5 条相邻收益记录；包括现金分红和拆股的 raw/total/adjusted 差异。负向测试把一行 `available_at` 改到 `asof_at` 之后，审计器拒绝该数据。

| symbol | session | raw price return | raw total return | adjusted-close return | 说明 |
|---|---|---:|---:|---:|---|
| AAA | 2024-01-04 | -0.009804 | 0.000000 | 0.000000 | 现金分红抵消价格下降 |
| AAA | 2024-01-05 | -0.500000 | -0.500000 | -0.009804 | 2:1 split 下 raw 跳变不能直接解释 |
| BBB | 2024-01-04 | 0.018987 | 0.025316 | 0.018987 | 分红使 total return 高于 price return |

## 公源/本地设计边界（Evidence Boundary） {#boundary}

| 类别 | 证据 |
|---|---|
| 公有来源 | FRED API、French Data Library、Princeton 金融课程、Wilson 可复现计算规范。[1–4] |
| 本地证据 | `m02_price_panel_fixture.csv`、`m02_data_contract.md`、`audit_price_panel.py`、`m02_price_panel_audit.json`、测试输出。 |
| 本地推断 | 以 `available_at <= asof_at` 作为通用数据管线接口，并把 raw/total/adjusted 三种回报并列保存。 |
| 尚未核实 | ALFRED 页面字段、SEC EDGAR/XBRL 当前接口、CRSP/Compustat/TAQ 的具体许可和点时字段。 |

## 方法对比与选择建议（Comparison） {#comparison}

| 研究目标 | 起步数据 | 必须补充 | 不应做的事 |
|---|---|---|---|
| 宏观时间序列 | FRED；修订问题进入 ALFRED 复核 | 频率、发布日期、vintage、缺失和日历 | 直接把最新修订值当历史实时值 |
| 公开因子复现 | French Data Library | 档案版本、构造定义、样本期和因子单位 | 把因子文件当作点时个股数据库 |
| 公司事件 | SEC/供应商/学术数据库（需重新核验） | 发布时点、重述、实体映射和许可 | 用当前字段回填历史并称无泄漏 |
| 高频/执行 | 授权订单/成交源 | 时钟、队列、撤单、成本和容量 | 用收盘价替代成交协议 |

建议顺序：先用合成 fixture 和公开数据学会契约，再进入 M03 估计器；只有当研究问题需要退市、公司事件或微观结构时，才申请相应的受限数据权限。

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 通过边界 |
|---|---|---|
| M02-Q01 | 区分 observed_at、available_at、asof_at。 | 能说明观测可以先于发布，且只比较 available_at 与 asof_at。 |
| M02-Q02 | 写出价格收益和总收益公式。 | 分母、现金分红每股口径和不含分红差异正确。 |
| M02-Q03 | 为什么拆股日不能直接比较 raw close？ | 能指出名义价格变化与经济持仓变化不同。 |
| M02-Q04 | adjusted close 进入生产前需登记什么？ | 因子方向、除息/除权规则、版本、样例和来源。 |
| M02-Q05 | 交易日历为什么影响年化波动率？ | 能说明有效会话数和缺失会话不能随意填充。 |
| M02-Q06 | 什么是 point-in-time join？ | join 条件含 available_at <= asof_at，而非只看 event_date。 |
| M02-Q07 | 给出一个幸存者偏差例子。 | 历史资产池只保留今天仍存续证券。 |
| M02-Q08 | 为什么“能下载”不等于“能再分发”？ | 能区分访问权、使用权和许可/版权边界。 |
| M02-Q09 | 如何处理重复 session_date？ | 拒绝或按可追溯规则去重，不能静默覆盖。 |
| M02-Q10 | 现金分红应落在哪个时间字段？ | 明确 ex-date/pay-date/record-date 选择和每股口径。 |
| M02-Q11 | 为什么需要稳定证券标识而不只用 ticker？ | ticker 会重用、变更，实体与证券映射需版本化。 |
| M02-Q12 | 如何审计 UTC 与本地时区？ | 解析时区、转换规则、交易所日历和跨日边界都有记录。 |
| M02-Q13 | 最新修订宏观值能否用于十年前回测？ | 只有在模拟当时 vintage 或明确研究目标时才可用。 |
| M02-Q14 | 为什么要保存 dropped-row reasons？ | 可解释缺失、异常、许可过滤并恢复同一面板。 |
| M02-Q15 | raw return 与 adjusted return 差异大时先查什么？ | 公司行动、因子方向、除息规则、币种和供应商文档。 |
| M02-Q16 | 何时可以计算相邻收益？ | 同实体、相邻有效会话、价格单位和口径一致。 |
| M02-Q17 | 设计一个未来可用时间的负向测试。 | 把 available_at 设置晚于 asof_at，审计器必须 FAIL。 |
| M02-Q18 | 为什么 point-in-time 不只是 SQL 技巧？ | 它约束研究可获得信息和结论解释，而不只是 join 语法。 |
| M02-Q19 | 数据字典至少应包含哪五类信息？ | 字段、类型、时间语义、来源/许可、转换/质量规则。 |
| M02-Q20 | M02 fixture 能否支持真实 alpha 结论？ | 不能；它只支持契约和计算路径的本地验证。 |

## 答案索引（Answer Boundary） {#answer-boundary}

为便于自动审查和复习定位，以下索引把每道题的达标边界单独列出；题目表仍保留完整题干。

| ID | 答案边界 |
|---|---|
| M02-Q01 | 观测可早于发布；研究快照只比较 `available_at <= asof_at`。 |
| M02-Q02 | 正确区分价格收益、总收益、分母和每股分红口径。 |
| M02-Q03 | 拆股改变名义价格，不等于持仓经济损失。 |
| M02-Q04 | 记录调整因子方向、公司行动规则、版本、样例和来源。 |
| M02-Q05 | 年化因子依赖有效交易会话数，缺失会话不能任意填充。 |
| M02-Q06 | Point-in-time join 必须含 `available_at <= asof_at`。 |
| M02-Q07 | 能构造只保留存续证券而遗漏退市证券的例子。 |
| M02-Q08 | 区分下载访问权、研究使用权与再分发许可。 |
| M02-Q09 | 重复会话要拒绝或按可追溯规则去重，不能静默覆盖。 |
| M02-Q10 | 明确 ex-date/pay-date/record-date 与每股口径的选择。 |
| M02-Q11 | ticker 会变更或重用，需稳定证券标识和映射版本。 |
| M02-Q12 | 记录时区解析、UTC 转换、交易所日历和跨日边界。 |
| M02-Q13 | 回测需模拟当时 vintage，不能直接使用最新修订值。 |
| M02-Q14 | 保存 dropped-row reasons 以解释过滤并重建面板。 |
| M02-Q15 | 先查公司行动、因子方向、除息、币种和供应商文档。 |
| M02-Q16 | 只有同实体、相邻有效会话且单位口径一致时计算。 |
| M02-Q17 | 将 `available_at` 设晚于 `asof_at`，审计器应拒绝。 |
| M02-Q18 | Point-in-time 是信息集约束，不只是 SQL 写法。 |
| M02-Q19 | 至少覆盖字段、类型、时间语义、来源/许可、转换/质量规则。 |
| M02-Q20 | 合成 fixture 只能验证契约和路径，不能支持真实 alpha 结论。 |

## 风险与后续建议（Risks & Next） {#risks}

- 合成 fixture 不代表真实数据分布、供应商行为或市场可交易性。
- FRED/French 的公开入口不自动解决修订、点时、公司行动和许可问题；ALFRED/SEC/学术数据库仍需在具体项目中重新冻结。
- adjusted close 的语义因供应商而异，不能只依赖列名。
- 下一 slice G06/M03 将把这些数据字段接入 OLS/MLE/GMM/Bootstrap 估计器，并记录估计假设和标准误，而不是重新定义数据契约。

## 参考文献（References） {#references}

1. [1] Federal Reserve Bank of St. Louis, “FRED API.” [链接](https://fred.stlouisfed.org/docs/api/fred/)
2. [2] Kenneth R. French, “Data Library.” [链接](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
3. [3] Princeton University Bendheim Center for Finance, “Requirements and Core Courses.” [链接](https://bcf.princeton.edu/academic-programs/master-in-finance/requirements-core-courses/)
4. [4] Greg Wilson et al., “Good Enough Practices in Scientific Computing,” *PLOS Computational Biology*, 2017. [链接](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005510)
5. [5] ALFRED official entry；本切片核验警告：浏览器访问失败，具体字段和 vintage API 待后续复核。 [链接](https://alfred.stlouisfed.org/alfred-graph)
6. [6] SEC EDGAR API Documentation；本切片核验警告：浏览器访问被阻断，具体字段待后续复核。 [链接](https://www.sec.gov/edgar/sec-api-documentation)
