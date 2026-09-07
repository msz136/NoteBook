---
title: P2 波动率预测实验：EWMA 与 GARCH 的滚动样本外比较
subtitle: 用正值方差预测、QLIKE 与严格时间切分评估条件波动率模型
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Volatility Forecasting
---

# P2 波动率预测实验：EWMA 与 GARCH 的滚动样本外比较

## 问题（Question） {#question}

历史波动率、EWMA 与 GARCH 如何在样本外预测未来收益平方？为什么均方误差不是唯一选择，QLIKE 如何约束方差预测必须为正？本项目用带波动聚集的合成收益，冻结训练/测试边界并比较两个一阶条件方差模型。

## 背景与动机（Background & Motivation） {#background}

Engle 的 ARCH 工作和 Bollerslev 的 GARCH 扩展把条件方差建模为过去冲击与过去方差的函数。[1][2] `arch` 官方文档提供金融波动率、分布和预测接口；本环境未安装该包，因此本地脚本使用 NumPy 网格拟合 Gaussian quasi-likelihood，明确标为简化实现。[3] 本实验不把合成序列的相对排名推广为真实市场优势。

<div class="evidence"><strong>证据边界：</strong>模型公式和 QLIKE 目标来自文献/官方文档；本地结果仅支持固定数据生成机制、切分和递推实现。参数网格、样本量和 seed 是教学协议，不是生产模型选择。</div>

## 概念与数据契约 {#concepts}

| 概念 | 定义 | 检查 |
|---|---|---|
| 条件方差 | \(Var(r_t\mid\mathcal F_{t-1})\) | 预测必须为正 |
| 波动聚集 | 大冲击后大波动持续 | 观察平方收益的自相关/簇状图 |
| EWMA | 固定衰减的历史平方收益递推 | \(\lambda\) 在训练前冻结 |
| GARCH(1,1) | 常数、过去冲击和过去方差的递推 | \(\omega>0,\alpha,\beta\ge0\) |
| QLIKE | \(v_t/\hat v_t-\log(v_t/\hat v_t)-1\) 的平均值 | 只比较正的方差预测 |
| 样本外 | 测试观测从未参与参数拟合 | 仅使用时间之前的数据 |

## 方法与数学形式（Methods & Mathematical Form） {#methods}

EWMA：

\[
\hat v_{t+1}=\lambda\hat v_t+(1-\lambda)r_t^2,\qquad 0<\lambda<1.
\]

GARCH(1,1)：

\[
v_t=\omega+\alpha r_{t-1}^2+\beta v_{t-1},
\qquad \omega>0,\;\alpha,\beta\ge0.
\]

标准有限无条件方差设定通常要求 \(\alpha+\beta<1\)。本脚本在训练段用小网格最小化 Gaussian quasi-likelihood，再递推测试段的一步方差；测试段收益不回流到参数选择。

QLIKE 对实现方差 \(v_t=r_t^2\) 和预测 \(\hat v_t\) 定义为：

\[
L_{QLIKE,t}=\frac{v_t}{\hat v_t}-\log\left(\frac{v_t}{\hat v_t}\right)-1.
\]

它对正预测和比例误差敏感；零收益需要数值下限或更合适的 realized-volatility proxy。

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
returns = load_point_in_time_returns(asof_at)  # 继承 M02/P1 时间契约
train, test = strict_time_split(returns, initial=360)
ewma = fit_ewma(train, lambda_=0.94)
garch = fit_garch_qmle(train, constraints=[omega > 0, alpha >= 0, beta >= 0])
for r_t in test:
    forecast_ewma.append(ewma.one_step())
    forecast_garch.append(garch.one_step())
    ewma.update(r_t); garch.update(r_t)
compare_qlike_and_stability(test**2, forecast_ewma, forecast_garch)
```

实现见 [`p2_volatility_forecast.py`](p2_volatility_forecast.py)，结果见 [`p2_volatility_forecast_results.json`](p2_volatility_forecast_results.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/projects/p2_volatility_forecast/p2_volatility_forecast.py
python quant_finance/projects/p2_volatility_forecast/test_p2_volatility_forecast.py -v
```

实验生成 520 期带波动聚集的收益，前 360 期用于拟合，后 160 期严格样本外评估。结果 JSON 记录 EWMA 与 GARCH 的 QLIKE、GARCH 参数和正值检查；两次运行输出逐字一致。QLIKE 的相对排名只对该合成机制成立。

## 失败案例与稳健性边界 {#comparison}

| 风险 | 影响 | 处理 |
|---|---|---|
| 用收益 MSE 代替 QLIKE | 低估方差尺度错误 | 同时报告 QLIKE 与预测分布诊断 |
| 测试集调参 | 样本外优势虚高 | 冻结训练段、另留验证段 |
| \(\hat v_t\le0\) | QLIKE 无定义/数值爆炸 | 参数约束和正值下限 |
| 波动率代理噪声 | 真实方差不可观测 | 使用 realized measure 或 QLIKE 边界说明 |
| 结构突变/杠杆效应 | GARCH(1,1) 失配 | EGARCH/GJR、滚动重估与压力期分析 |
| 高频微观结构噪声 | realized variance 偏差 | 交易日历、采样频率和清洗契约 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| P2-Q01 | 写出 EWMA 递推。 | 正确说明 lambda 与上一期平方收益权重。 |
| P2-Q02 | GARCH 参数为何需约束？ | 保证方差正且通常有限。 |
| P2-Q03 | QLIKE 为什么要求正预测？ | 比值和对数需要正分母。 |
| P2-Q04 | 严格样本外是什么意思？ | 测试观测不参与参数和超参选择。 |
| P2-Q05 | 为什么波动率预测不能随机切分？ | 时间依赖和未来泄漏。 |
| P2-Q06 | EWMA 与 GARCH 的差异？ | 固定衰减 vs 估计常数/冲击/持久性。 |
| P2-Q07 | 如何处理杠杆效应？ | 考虑 GJR/EGARCH 等非对称模型。 |
| P2-Q08 | realized variance 是真方差吗？ | 是代理，受采样和微观结构影响。 |
| P2-Q09 | 合成实验能证明策略盈利吗？ | 不能，只证明实现与协议。 |
| P2-Q10 | 何时需要 block bootstrap？ | 残差/收益存在时间依赖时。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| P2-Q01 | \(v_{t+1}=\lambda v_t+(1-\lambda)r_t^2\)。 |
| P2-Q02 | \(\omega>0,\alpha,\beta\ge0\)，通常 alpha+beta<1。 |
| P2-Q03 | QLIKE 含 \(v/\hat v\) 与 log 比值。 |
| P2-Q04 | 参数选择只用训练时点之前的信息。 |
| P2-Q05 | 随机切分打破信息集并泄漏未来。 |
| P2-Q06 | EWMA 无估计常数项，GARCH 估计递推参数。 |
| P2-Q07 | 使用非对称条件方差模型并做样本外比较。 |
| P2-Q08 | realized measure 是观测代理，不是真实潜在方差。 |
| P2-Q09 | 合成机制不提供市场、成本或容量证据。 |
| P2-Q10 | 按连续块而不是独立行重抽样。 |

## 风险与后续建议（Risks & Next） {#risks}

- 当前环境未安装 `arch`，本项目的 GARCH 是教学用网格 QMLE，不是官方包对照。
- 单一 QLIKE 排名不能替代预测区间、尾部风险、参数稳定性和经济价值评估。
- 下一 slice G10/M05 将进入面板与因果识别，需把本项目的时间切分和数据可见性继续作为前置条件。

## 参考文献（References） {#references}

1. [1] Robert F. Engle, “Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation,” *Econometrica*, 1982. [链接](https://doi.org/10.2307/1912773)
2. [2] Tim Bollerslev, “Generalized Autoregressive Conditional Heteroskedasticity,” *Journal of Econometrics*, 1986. [链接](https://doi.org/10.1016/0304-4076(86)90063-1)
3. [3] arch documentation, “Volatility Modeling.” [链接](https://arch.readthedocs.io/en/stable/univariate/univariate_volatility_modeling.html)
