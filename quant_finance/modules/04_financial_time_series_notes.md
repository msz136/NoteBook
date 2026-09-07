---
title: 金融时间序列：ARIMA、VAR、状态空间与波动率模型
subtitle: M04 · 用时间顺序、滚动窗口和依赖结构约束预测评估
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Financial Time Series
---

# 金融时间序列：ARIMA、VAR、状态空间与波动率模型

## 问题（Question） {#question}

金融序列不是 iid 横截面：收益、利率和波动率都有滞后依赖、结构变化和预测信息集。如何在不打乱时间的前提下比较 ARIMA/VAR、状态空间和 ARCH/GARCH，并把单位根、协整与预测损失写进研究协议？

## 背景与动机（Background & Motivation） {#background}

时间序列研究必须区分描述、预测与结构解释。`statsmodels` 官方文档提供 ARIMA、VAR、状态空间和单位根检验的实现入口；`arch` 官方文档覆盖条件波动率、Bootstrap、单位根与协整工具。[1][2] 本模块先用 NumPy 合成双变量序列验证严格时间切分和基本递推，不把未安装的可选包伪装成已运行证据。

<div class="evidence"><strong>证据边界：</strong>ARIMA/VAR/状态空间/ARCH-GARCH 的模型定义来自官方文档和计量课程；本地结果只验证简化 AR(1)、VAR(1)、EWMA 与 local-level Kalman 风格滤波递推。没有真实 FRED/ALFRED 数据，因此不支持宏观预测或交易收益主张。</div>

## 基础概念与术语 {#concepts}

| 术语 | 含义 | 关键风险 |
|---|---|---|
| 平稳（stationary） | 分布或矩在时间平移下保持稳定 | 趋势/单位根会使回归和预测失真 |
| 单位根（unit root） | AR 多项式在单位圆上有根 | 水平回归可能是伪回归 |
| 协整（cointegration） | 非平稳序列的某个线性组合平稳 | 需误差修正而非任意差分 |
| ARIMA | 自回归、差分与移动平均组合 | 阶数、差分和残差诊断需冻结 |
| VAR | 多变量滞后系统 | 参数数量和稳定性随维度快速增长 |
| 状态空间 | 隐状态转移与观测方程 | 需要初始化、噪声方差和滤波设定 |
| ARCH/GARCH | 条件方差依赖过去冲击/方差 | 分布尾部、杠杆和结构变化可能未建模 |
| 滚动样本外 | 每个时点只用此前观测训练 | 随机切分会泄漏未来 |

## 方法 {#methods}

### ARIMA 与单位根 {#arima}

ARIMA\((p,d,q)\) 对差分序列建模：

\[
\phi(L)(1-L)^d y_t=c+\theta(L)\varepsilon_t,\qquad \varepsilon_t\sim(0,\sigma^2).
\]

先通过图形、ADF/KPSS 等互补证据判断差分与趋势；检验的零假设方向不同，不能只看一个 p 值。

### VAR 与协整 {#var}

VAR(1) 写为：

\[
y_t=c+A_1y_{t-1}+u_t,\qquad E[u_t\mid\mathcal F_{t-1}]=0.
\]

稳定性要求 companion matrix 的特征根在单位圆内。若变量非平稳但存在协整关系，应考虑 VECM；盲目对所有变量差分会丢失长期关系。

### 状态空间与滤波 {#state-space}

一般形式为：

\[
\alpha_t=T_t\alpha_{t-1}+R_t\eta_t,\qquad y_t=Z_t\alpha_t+\varepsilon_t.
\]

Kalman filter 用预测误差更新隐状态；初始化、缺失观测处理和噪声协方差必须进入实验记录。local-level 递推是本切片的最小可执行示例。

### ARCH/GARCH 与波动率 {#garch}

GARCH(1,1) 的条件方差为：

\[
\sigma_t^2=\omega+\alpha\varepsilon_{t-1}^2+\beta\sigma_{t-1}^2,
\qquad \omega>0,\ \alpha,\beta\ge0.
\]

通常要求 \(\alpha+\beta<1\) 以得到有限无条件方差（在标准设定下）。EWMA 是不含常数项的指数加权基线，不应称为完整 GARCH 估计。

## 数学与评估契约（Mathematical Form） {#math}

| 项目 | 契约 |
|---|---|
| 训练信息集 | 预测 \(y_t\) 只能使用 \(\{y_s:s<t\}\) |
| 损失 | RMSE/MAE 评估均值预测；QLIKE 更适合方差预测 |
| 滚动窗口 | 记录 expanding 或 fixed-width、初始训练长度和再估计频率 |
| 稳定性 | 报告单位根/特征根、残差自相关和条件方差约束 |
| 不确定性 | 使用滚动误差、Bootstrap 或预测区间；不把点预测当确定值 |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
series = load_point_in_time_series(asof_at)  # 继承 M02 时间与可用性契约
train, test = strict_time_split(series, initial=160)
for t in test:
    fit = refit_model(train)                 # ARIMA/VAR/state-space/GARCH
    forecast[t] = fit.forecast(horizon=1)
    train = append_observation(train, series[t])
score = evaluate_forecasts(forecast, metric="RMSE")
diagnose_residuals_and_stability(fit, score)
```

可执行 smoke 实验见 [`m04_time_series.py`](../tools/m04_time_series.py)，结果见 [`m04_time_series_results.json`](../data/m04_time_series_results.json)。由于环境未安装 `statsmodels`/`arch`，本切片不声称已执行其 API；后续环境准备后应增加同一数据的官方实现对照。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/tools/m04_time_series.py
python quant_finance/data/test_m04_time_series.py -v
```

本地脚本固定 seed 生成 260 期双变量序列，前 160 期训练、后 100 期滚动预测；同时输出 VAR(1) 系数、EWMA 条件方差和 local-level 过滤状态。测试验证两次运行输出逐字一致、VAR 系数矩阵形状正确、预测误差与方差为正。

## 数据契约与坏案例 {#boundary}

| 坏案例 | 为什么失效 | 修复 |
|---|---|---|
| 随机打乱 train/test | 未来观测进入训练集 | expanding/fixed rolling split |
| 先看全样本再选差分阶数 | 测试集信息泄漏 | 在每个训练窗口内选择并记录 |
| 非平稳水平回归 | 伪回归、残差不平稳 | 差分、协整/VECM 或结构模型 |
| 用对称 Gaussian 解释极端波动 | 尾部风险低估 | t 分布、skew、EVT 与压力测试 |
| EWMA 叫作 GARCH | 缺少常数项和估计的条件方差结构 | 准确标注模型并报告参数约束 |
| 忽略交易日缺失 | 滞后和年化尺度错误 | 使用 M02 日历、时区和 session_id |

## 方法对比与选择建议（Comparison） {#comparison}

| 研究问题 | 起步模型 | 追加诊断 |
|---|---|---|
| 单变量均值预测 | ARIMA/ETS | 单位根、残差、自相关、滚动误差 |
| 多变量联动 | VAR/VECM | 稳定性、协整秩、脉冲响应不确定性 |
| 隐状态/缺失观测 | 状态空间/Kalman | 初始化、噪声方差、滤波与平滑差异 |
| 波动率预测 | GARCH、EWMA 基线 | QLIKE、尾部、杠杆、样本外比较 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 通过边界 |
|---|---|---|
| M04-Q01 | 什么是弱平稳？ | 说明均值、方差和协方差只依赖滞后。 |
| M04-Q02 | 单位根为何危险？ | 能解释伪回归和差分选择。 |
| M04-Q03 | ADF 与 KPSS 零假设有何差异？ | 说清一个以单位根为零假设、一个以平稳为零假设。 |
| M04-Q04 | ARIMA 的 d 表示什么？ | 差分阶数，不是 AR 阶数。 |
| M04-Q05 | VAR 稳定性如何检查？ | 看 companion matrix 特征根。 |
| M04-Q06 | 何时使用 VECM？ | 非平稳变量存在协整关系时。 |
| M04-Q07 | 状态空间的两条方程是什么？ | 状态转移方程和观测方程。 |
| M04-Q08 | Kalman filter 更新什么？ | 用预测误差和增益更新隐状态及方差。 |
| M04-Q09 | GARCH(1,1) 参数有何约束？ | \(\omega>0,\alpha,\beta\ge0\)，通常 \(\alpha+\beta<1\)。 |
| M04-Q10 | EWMA 与 GARCH 的边界？ | EWMA 是固定衰减基线，不等于估计的 GARCH。 |
| M04-Q11 | 为什么不能随机切时间序列？ | 会把未来信息泄漏到训练。 |
| M04-Q12 | expanding 与 rolling window 差异？ | 前者样本累积，后者窗口固定。 |
| M04-Q13 | 均值预测应报告什么损失？ | 至少 RMSE/MAE 和样本外切分。 |
| M04-Q14 | 方差预测为什么常用 QLIKE？ | 对正方差预测更适合且对尺度有明确惩罚。 |
| M04-Q15 | 如何处理缺失交易会话？ | 遵循日历，不把缺失收益任意填零。 |
| M04-Q16 | 结构突变会怎样？ | 历史参数不稳定，需滚动、状态转换或分段诊断。 |
| M04-Q17 | 多步预测为何不同于一步？ | 递推误差与参数不确定性会累积。 |
| M04-Q18 | 什么时候使用 block bootstrap？ | 残差或收益存在时间依赖时。 |
| M04-Q19 | 本地 smoke 结果支持什么？ | 支持递推和时间切分实现，不支持真实市场结论。 |
| M04-Q20 | 何时暂停模型比较？ | 日历、切分、稳定性或残差诊断未通过时。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| M04-Q01 | 二阶矩只依赖滞后而不依赖绝对时间。 |
| M04-Q02 | 单位根使水平关系可能伪回归并破坏常规渐近近似。 |
| M04-Q03 | ADF 以单位根为零假设，KPSS 以平稳为零假设。 |
| M04-Q04 | d 是差分次数。 |
| M04-Q05 | companion matrix 特征根应在单位圆内。 |
| M04-Q06 | 非平稳变量有稳定长期线性组合时。 |
| M04-Q07 | 状态转移与观测方程。 |
| M04-Q08 | 用创新项按 Kalman gain 修正状态和不确定性。 |
| M04-Q09 | 非负参数，标准有限方差设定通常要求 alpha+beta 小于 1。 |
| M04-Q10 | EWMA 是固定递推基线，GARCH 还估计常数和参数。 |
| M04-Q11 | 随机切分让未来观测进入过去训练。 |
| M04-Q12 | expanding 累积样本，rolling 固定窗口。 |
| M04-Q13 | RMSE/MAE、时间切分和基准模型。 |
| M04-Q14 | QLIKE 对方差预测的尺度和正值约束更合适。 |
| M04-Q15 | 记录交易日历并保留缺失原因。 |
| M04-Q16 | 参数随时间变化，需滚动或状态转换诊断。 |
| M04-Q17 | 多步递推会积累预测和参数误差。 |
| M04-Q18 | 存在序列相关时按连续块重抽样。 |
| M04-Q19 | 只证明本地递推/切分可重放。 |
| M04-Q20 | 任一数据、切分、稳定性或残差闸门失败。 |

## 风险与后续建议（Risks & Next） {#risks}

- `statsmodels` 与 `arch` 未安装，本 slice 的官方实现对照留作环境准备项，不能标记为已完成。
- 单一合成机制无法覆盖利率、汇率、股指、跳跃和微观结构序列的全部特征。
- 下一 slice G08/P1 将冻结 FRED/ALFRED 实时 vintage 数据，比较修订值与当时可用值，重点验证时间信息集而非追求高预测分数。

## 参考文献（References） {#references}

1. [1] statsmodels developers, “Time Series Analysis,” official documentation. [链接](https://www.statsmodels.org/stable/tsa.html)
2. [2] bashtage, “arch documentation: volatility, unit root, cointegration and bootstrap.” [链接](https://arch.readthedocs.io/en/stable/)
3. [3] MIT OpenCourseWare, “14.382 Econometrics,” 2017. [链接](https://ocw.mit.edu/courses/14-382-econometrics-spring-2017/)
4. [4] Bruce E. Hansen, “Econometrics.” [链接](https://www.ssc.wisc.edu/~bhansen/econometrics/)
