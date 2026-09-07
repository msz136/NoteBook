---
title: 核心计量：OLS、MLE、GMM、稳健推断与 Bootstrap
subtitle: M03 · 把数据契约接到估计器，并把假设、标准误与识别边界一起报告
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Core Econometrics
---

# 核心计量：OLS、MLE、GMM、稳健推断与 Bootstrap

## 问题（Question） {#question}

给定 M02 的点时价格/收益面板，如何估计线性关系、量化不确定性，并避免把“估计得到”误写成“因果成立”？本模块用一个可重复的异方差合成数据集对照手写 OLS、Gaussian MLE、恰好识别 GMM 与个体 Bootstrap；IV 只作为下一阶段的识别入口。

## 背景与动机（Background & Motivation） {#background}

MIT 14.382 将模型、识别、估计和推断作为现代计量的连续链条；Hansen 的计量教材提供研究生层面的渐近理论与估计器框架。[1][2] `statsmodels` 提供 OLS、协方差估计和诊断的官方实现入口，但软件输出不能替代研究者检查数据时间语义、函数形式和误差结构。[3] Efron 的经典论文奠定 Bootstrap 的重抽样方法，同时明确其覆盖率依赖统计量与数据依赖结构。[4]

<div class="evidence"><strong>证据边界：</strong>方法定义和 API 能由课程、教材及官方文档支持；数值结果是本地合成 fixture 的可复现实验，不支持任何真实资产的 alpha 或因果结论。异方差只在本地数据生成机制中注入，稳健标准误的实现契约在本模块冻结，非对所有金融时间序列自动有效。</div>

## 先修知识与术语 {#concepts}

| 术语 | 定义 | 本模块中的边界 |
|---|---|---|
| 普通最小二乘（Ordinary Least Squares, OLS） | 最小化残差平方和的线性估计器 | 需要外生性才能作因果解释；线性投影本身不保证因果 |
| 最大似然（Maximum Likelihood, MLE） | 选择使观测样本似然最大的参数 | 分布设定错时，点估计/标准误解释会改变 |
| 广义矩估计（Generalized Method of Moments, GMM） | 令样本矩逼近理论矩的估计方法 | 矩条件必须有经济/统计依据；恰好识别时与 OLS 可重合 |
| 异方差稳健协方差（heteroskedasticity-robust covariance） | 不强制误差方差恒定的渐近协方差估计 | 不是自动修复内生性、时间依赖或小样本问题 |
| Bootstrap | 从观测样本重抽样近似估计量分布 | 序列相关数据通常需要 block/bootstrap 变体 |
| 工具变量（Instrumental Variable, IV） | 用与解释变量相关但与结构误差正交的工具识别参数 | 本模块只冻结入口，不声称存在有效工具 |

## 方法与假设 {#methods}

### OLS 与稳健标准误 {#ols}

线性模型写为 (y=Xeta+u)。OLS 为：

\[
\hat\beta_{OLS}=(X'X)^{-1}X'y,
\qquad \hat u_i=y_i-x_i'\hat\beta.
\]

同方差协方差使用 \(\hat\sigma^2(X'X)^{-1}\)；异方差稳健（sandwich）形式则为：

\[
\widehat{\operatorname{Var}}(\hat\beta)=
(X'X)^{-1}\left(\sum_i x_ix_i'\hat u_i^2\right)(X'X)^{-1}.
\]

稳健协方差改变不确定性估计，不会让相关性、反向因果或遗漏变量消失。金融日收益还可能有时间聚类、重叠观测或横截面相关，需要 HAC、cluster 或双向 cluster 的额外契约。

### Gaussian MLE {#mle}

若假设 \(u_i\overset{iid}{\sim}N(0,\sigma^2)\)，对数似然为：

\[
\ell(\beta,\sigma^2)=-\frac n2\log(2\pi\sigma^2)-\frac{1}{2\sigma^2}(y-X\beta)'(y-X\beta).
\]

在该设定下，\(\hat\beta_{MLE}=\hat\beta_{OLS}\)，\(\hat\sigma^2=n^{-1}\sum_i\hat u_i^2\)。这是一条模型等价性，不是“正态分布已被数据证明”。

### GMM 与识别 {#gmm}

给定矩条件 \(E[g(z_i,\theta)]=0\)，GMM 最小化：

\[
Q_n(\theta)=\bar g_n(\theta)'W_n\bar g_n(\theta),\qquad
\bar g_n(\theta)=n^{-1}\sum_i g(z_i,\theta).
\]

恰好识别且使用线性矩 \(g_i=x_i(y_i-x_i'\beta)\) 时，\(\bar g=0\) 等价于 OLS 正规方程；过度识别时应报告权重矩阵、J 检验与矩条件的经济含义。GMM 的灵活性来自矩条件，而不是免除识别假设。

### Bootstrap 与 IV 入口 {#bootstrap-iv}

个体 Bootstrap 对 \((y_i,x_i)\) 成对重抽样，重复估计并用经验分位数形成区间。若收益有明显序列相关，应改用 moving-block 或 stationary bootstrap，并在实验记录中写明块长选择。IV/2SLS 需要第一阶段相关性、排除限制和单调性等问题；在没有可信工具时，报告相关性不应升级为因果效应。

## 数学、诊断与实现映射 {#math}

| 检查 | 数学对象 | 实现证据 |
|---|---|---|
| 秩 | \(\operatorname{rank}(X)=k\) | `np.linalg.lstsq` 返回的解与设计矩阵列数 |
| 残差 | \(\hat u=y-X\hat\beta\) | 估计器输出可重算 RSS |
| 外生性 | \(E[x_i u_i]=0\) | 需要研究设计或工具支持，不能由 OLS 输出证明 |
| 异方差 | \(E[u_i^2\mid x_i]\) 随 \(x_i\) 变化 | fixture 按 \(0.35+0.65|x_i|\) 缩放噪声 |
| Bootstrap 区间 | \(q_{.025},q_{.975}\) | 固定 seed、400 次重抽样、分位数记录 |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
rows = load_point_in_time_panel(asof_at)       # 继承 M02 的 available_at <= asof_at
y, X = make_design(rows, target="total_return_raw")
beta_ols = solve_least_squares(X, y)
se_hc = sandwich_covariance(X, y - X @ beta_ols)
beta_mle, sigma2 = gaussian_mle(X, y)
beta_gmm = solve_moment_equations(X, y)
bootstrap_ci = resample_pairs_and_refit(X, y, seed=20260722)
report_assumptions_and_failures(beta_ols, se_hc, beta_mle, beta_gmm, bootstrap_ci)
```

本切片的可执行实现见 [`m03_core_estimators.py`](../tools/m03_core_estimators.py)，结果见 [`m03_estimator_comparison.json`](../data/m03_estimator_comparison.json)。实现刻意只使用合成数据，避免把受限市场数据混入仓库。

## 实现证据与结果（Implementation & Results） {#implementation}

运行：

```powershell
python quant_finance/tools/m03_core_estimators.py
python quant_finance/data/test_m03_core_estimators.py -v
```

固定 seed 的本地结果验证三个不变量：Gaussian MLE 与 OLS 的 \(\hat\beta\) 差异小于 \(10^{-12}\)，恰好识别线性 GMM 与 OLS 差异小于 \(10^{-12}\)，Bootstrap 恰好执行 400 次并输出两个参数的 95% percentile 区间。结果只说明实现路径一致，不说明正态性、外生性或市场可交易性成立。

## 数据契约与坏案例 {#boundary}

| 风险 | 失效表现 | 必须记录/修复 |
|---|---|---|
| 未来信息 | 用 `observed_at` 或修订值替代 `available_at` | 继承 M02 point-in-time join 和快照时间 |
| 异方差 | 同方差 SE 过窄、显著性虚高 | HC/HAC/cluster 选择与小样本修正 |
| 内生性 | OLS 系数有预测相关但无因果含义 | 设计识别策略；可信时再进入 IV |
| 弱工具 | 2SLS 不稳定、有限样本偏误 | 第一阶段诊断、弱 IV 稳健区间 |
| 序列相关 Bootstrap | 区间覆盖率失真 | block 长度、重抽样单位和时间切分 |
| 多重检验 | 反复试规格后偶然显著 | 预注册、校正或完整失败登记 |

## 方法对比与选择建议（Comparison） {#comparison}

| 目标 | 首选 | 不能替代的工作 |
|---|---|---|
| 线性预测基线 | OLS + 稳健 SE | 不能替代样本外时间切分 |
| 明确分布模型 | MLE | 需诊断分布错设和边界参数 |
| 经济矩条件/资产定价 | GMM | 需解释矩条件、权重和过度识别 |
| 小样本不确定性探索 | Bootstrap | 依赖重抽样单位与数据依赖结构 |
| 因果识别 | IV/2SLS（下一模块深入） | 不能凭相关性自动构造工具 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 通过边界 |
|---|---|---|
| M03-Q01 | 推导 OLS 正规方程。 | 能从 RSS 对 \(\beta\) 求导并说明满秩条件。 |
| M03-Q02 | OLS 何时有因果解释？ | 说明外生性/识别设计，而非只说拟合优度。 |
| M03-Q03 | MLE 与 OLS 何时重合？ | 给出 iid Gaussian 误差及 \(\sigma^2\) 估计条件。 |
| M03-Q04 | 为什么 robust SE 不修复内生性？ | 区分方差估计与系数识别。 |
| M03-Q05 | 写出 sandwich 协方差三部分。 | 面、肉、面及残差平方项位置正确。 |
| M03-Q06 | GMM 的矩条件是什么？ | 说明理论矩为零且样本矩被最小化。 |
| M03-Q07 | 恰好识别 GMM 为什么可等于 OLS？ | 连接线性矩方程与正规方程。 |
| M03-Q08 | 过度识别时应报告什么？ | 权重矩阵、J 检验和矩条件经济含义。 |
| M03-Q09 | Bootstrap 重抽样什么单位？ | iid 观测成对重抽样；时间依赖需 block。 |
| M03-Q10 | percentile 区间的边界？ | 说明小样本、偏态和依赖结构下覆盖率不保证。 |
| M03-Q11 | 如何检测设计矩阵病态？ | 看秩、条件数和尺度，不能静默求逆。 |
| M03-Q12 | M02 的 `available_at` 如何进入估计？ | 先按 `asof_at` 过滤，再形成 \(y,X\)。 |
| M03-Q13 | 异方差为何常见于金融收益？ | 条件波动随状态/规模变化，不能假定恒定。 |
| M03-Q14 | HAC 与 HC 的差异？ | HAC 处理时间相关，HC 主要放松横截面同方差。 |
| M03-Q15 | IV 的排除限制是什么？ | 工具只能通过内生解释变量影响结果。 |
| M03-Q16 | 弱工具会怎样？ | 2SLS 有限样本分布异常，需专门诊断。 |
| M03-Q17 | 固定 seed 能保证什么？ | 保证本脚本同环境重放；不承诺所有未来版本逐位一致。 |
| M03-Q18 | 为什么不能从合成 fixture 宣称 alpha？ | 数据生成机制不是市场证据，也没有交易成本。 |
| M03-Q19 | 估计报告至少列哪些信息？ | 样本、变量、估计器、SE、切分、假设和失败项。 |
| M03-Q20 | 何时暂停解释显著系数？ | 数据契约、识别、诊断或稳健性闸门未通过时。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| M03-Q01 | RSS 求导为零得到 \(X'X\hat\beta=X'y\)，需满列秩。 |
| M03-Q02 | 需要外生性或明确识别设计；高 \(R^2\) 不够。 |
| M03-Q03 | iid 正态误差下均值参数的 MLE 与 OLS 重合。 |
| M03-Q04 | robust 只估计协方差，不能消除 \(E[xu]\ne0\)。 |
| M03-Q05 | \((X'X)^{-1}\)、残差加权的中间项、右侧 \((X'X)^{-1}\)。 |
| M03-Q06 | 选择 \(\theta\) 使 \(\bar g_n(\theta)'W\bar g_n(\theta)\) 最小。 |
| M03-Q07 | 线性矩为零即 OLS 正规方程。 |
| M03-Q08 | 记录权重、J 检验和矩条件是否有经济依据。 |
| M03-Q09 | iid 时成对重抽样；序列相关时用 block。 |
| M03-Q10 | 依赖统计量、样本量和数据依赖，非无条件标称覆盖。 |
| M03-Q11 | 检查 rank/condition number，并报告数值稳定性。 |
| M03-Q12 | 只使用 `available_at <= asof_at` 的记录构造样本。 |
| M03-Q13 | 金融条件波动、规模和状态常使条件方差变化。 |
| M03-Q14 | HAC 同时允许滞后相关；HC 主要针对异方差。 |
| M03-Q15 | 工具与内生变量相关、与结构误差正交。 |
| M03-Q16 | 第一阶段弱时估计不稳定，需弱 IV 方法。 |
| M03-Q17 | 固定本脚本 seed 的重放，不等于跨版本逐位保证。 |
| M03-Q18 | 合成数据不能验证真实市场收益、成本或容量。 |
| M03-Q19 | 至少列数据版本、样本、估计、SE、假设、切分与失败。 |
| M03-Q20 | 任一数据、识别、诊断或稳健性闸门失败都应暂停强解释。 |

## 风险与后续建议（Risks & Next） {#risks}

- 本模块未实现完整 HC/HAC/cluster 数值库，只冻结其公式、选择边界和报告要求；生产研究应与 `statsmodels` 输出交叉核对。
- 合成数据不含交易成本、非同步交易、缺失会话和退市机制，不能用于策略收益结论。
- 下一 slice G07/M04 将处理 ARIMA/VAR、状态空间、单位根、协整和 ARCH/GARCH；需要把 M02 的会话与时间切分继续保留。

## 参考文献（References） {#references}

1. [1] MIT OpenCourseWare, “14.382 Econometrics,” 2017. [链接](https://ocw.mit.edu/courses/14-382-econometrics-spring-2017/)
2. [2] Bruce E. Hansen, “Econometrics,” 2022. [链接](https://www.ssc.wisc.edu/~bhansen/econometrics/)
3. [3] statsmodels developers, “Statsmodels documentation.” [链接](https://www.statsmodels.org/stable/index.html)
4. [4] Bradley Efron, “Bootstrap Methods: Another Look at the Jackknife,” *Annals of Statistics*, 1979. [链接](https://projecteuclid.org/journals/annals-of-statistics/volume-7/issue-1/Bootstrap-Methods-Another-Look-at-the-Jackknife/10.1214/aos/1176344552.short)
