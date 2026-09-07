# M02 金融价格面板数据契约

这是一个可再分发的合成 fixture，不是交易所或供应商数据。它只用来测试字段语义、时间和收益计算。

## 必需字段

| 字段 | 类型/约束 | 语义 |
|---|---|---|
| `symbol` | 非空字符串 | 证券/资产标识；不能仅用当前仍存续资产回填历史 |
| `session_date` | ISO 日期、实体内严格递增 | 交易会话日期，不等价于文件下载日期 |
| `observed_at` | UTC 时间戳 | 观测或收盘记录发生的时间 |
| `available_at` | UTC 时间戳，必须明确发布语义 | 研究管线可以看到该字段的最早时间；必须满足 `available_at <= asof_at` 才能进入特征 |
| `asof_at` | UTC 时间戳 | 本次研究快照/特征构造的时间；它不是观测发生时间 |
| `close_raw` | 正数 | 未做拆股/分红调整的收盘价，适合描述价格但不能直接跨公司行动计算总收益 |
| `close_adjusted` | 正数 | 经过明确规则处理的可比价格；必须登记供应商/转换规则 |
| `cash_dividend` | 非负每股金额 | 现金分配；需注明 ex-date/pay-date 口径 |
| `split_factor` | 正数 | 拆股比例；本 fixture 只用于提醒跨 split 的 raw price 不可直接比较 |
| `source_id` / `license_class` | 非空 | 来源和再分发边界；真实数据必须带许可证明或链接 |

## 时间与 point-in-time 规则

给定研究时点 `asof_at`，只允许连接 `available_at <= asof_at` 的记录。`available_at` 晚于 `observed_at` 并不自动是错误：收盘观测可能先发生、供应商稍后发布。`event_date <= asof_at` 不能单独替代可用时间，因为财报、因子和分类可能在事件日后才发布，也可能被后续修订。FRED/ALFRED、SEC、CRSP/Compustat 等来源的字段与许可必须在具体 slice 中重新冻结；当前 fixture 不代表它们的字段契约。

## 收益口径

不含分红的价格收益：

\[
R^{price}_t=\frac{P^{raw}_t}{P^{raw}_{t-1}}-1.
\]

在没有拆股且现金分红 \(D_t\) 已按同一每股口径记录时，总收益可写为：

\[
R^{total}_t=\frac{P^{raw}_t+D_t}{P^{raw}_{t-1}}-1.
\]

含拆股或供应商复权时，应使用明确的 `close_adjusted` 或公司行动转换，而不是把 raw price 的跳变当作经济收益。任何调整都必须保存转换版本、输入字段、因子方向和验证样例。

## 审计门槛

1. CSV 字段齐全且类型可解析；
2. 每个 `symbol` 的 `session_date` 严格递增且无重复；
3. 时间戳带 UTC `Z`，`available_at` 不晚于该行 `observed_at`；
4. 价格、调整价格、拆股因子满足正值约束，分红非负；
5. 价格收益与总收益只在同一实体、相邻交易会话和明确口径下计算；
6. `license_class` 不为 `unknown` 时也不能推断有公开再分发权，仍需保留许可证来源。
