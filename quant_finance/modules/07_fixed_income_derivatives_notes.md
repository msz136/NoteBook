---
title: 固定收益、衍生品与随机过程：定价、数值方法与对冲边界
subtitle: M07 · 从现金流贴现到风险中性期望，并交叉验证解析解、树和 Monte Carlo
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Fixed Income and Derivatives
---

# 固定收益、衍生品与随机过程：定价、数值方法与对冲边界

## 问题（Question） {#question}

债券价格、久期和收益率曲线如何连接？为什么 Black–Scholes 的风险中性定价不等于真实世界收益预测？二叉树与 Monte Carlo 如何用同一欧式期权交叉验证，何时还必须报告离散对冲误差、波动率微笑和信用/流动性风险？

## 背景与动机（Background & Motivation） {#background}

Black 与 Scholes、Merton 建立了连续交易和无套利下的期权定价框架；Cox–Ross–Rubinstein 二叉树提供离散时间复制与数值逼近。[1–3] 固定收益定价则从未来现金流和期限结构开始。教材公式只有在计息、日计数、曲线、波动率和交易规则被精确定义时才能进入生产。

<div class="evidence"><strong>证据边界：</strong>理论公式来自经典文献；本地结果验证固定收益现金流、Black–Scholes、600 步二叉树和 antithetic Monte Carlo 的数值一致性。未使用市场期权链、收益率曲线或交易成本，不能支持校准、套利或对冲 P&amp;L 主张。</div>

## 基础概念与术语 {#concepts}

| 概念 | 定义 | 实践边界 |
|---|---|---|
| 折现因子 | \(P(0,T)\)：T 时点一单位现金流的现值 | 需明确曲线来源、币种、抵押和插值 |
| 即期利率 | 单一到期零息现金流的利率 | 与 YTM、远期利率不同 |
| 久期 | 价格对收益率一阶敏感度 | 大变动需凸性；非平行移位需 key-rate duration |
| 风险中性测度 | 贴现资产价格为鞅的定价测度 | 不等于真实概率或收益预测 |
| 隐含波动率 | 使模型价格等于市场价格的波动率 | 微笑/曲面表明常数波动率失配 |
| Delta 对冲 | 用标的局部抵消期权一阶价格风险 | 离散交易、跳跃、成本会留下误差 |

## 固定收益方法 {#fixed-income}

债券现金流现值：

\[
B_0=\sum_{j=1}^{n}CF_jP(0,t_j).
\]

若用固定到期收益率 \(y\) 和每年 \(m\) 次复利：

\[
B(y)=\sum_{j=1}^{n}\frac{CF_j}{(1+y/m)^j}.
\]

Macaulay 久期与 modified duration：

\[
D_M=\frac{\sum_j t_jPV(CF_j)}{B},\qquad D_{mod}=\frac{D_M}{1+y/m},\qquad \frac{\Delta B}{B}\approx-D_{mod}\Delta y.
\]

YTM 是单一内部收益率，并不是完整期限结构；曲线构建需处理存款/OIS/期货/互换或国债报价、日计数、支付日历、插值和 bootstrap 顺序。

## 随机过程与风险中性定价 {#stochastic}

Black–Scholes 假设下标的遵循几何布朗运动：

\[
dS_t=\mu S_tdt+\sigma S_tdW_t.
\]

风险中性测度下漂移替换为无风险利率 \(r\)，欧式看涨期权：

\[
C=S_0N(d_1)-Ke^{-rT}N(d_2),
\quad d_1=\frac{\log(S_0/K)+(r+\sigma^2/2)T}{\sigma\sqrt T},\quad d_2=d_1-\sigma\sqrt T.
\]

该价格依赖连续交易、无摩擦、常数波动率等假设。风险中性定价消去可复制风险的真实漂移，不意味着资产真实期望收益等于 \(r\)。

## 数值方法 {#methods}

### 二叉树 {#tree}

CRR 树取 \(u=e^{\sigma\sqrt{\Delta t}}, d=1/u\)，风险中性概率：

\[
q=\frac{e^{r\Delta t}-d}{u-d}.
\]

从到期 payoff 反向递推；美式期权每个节点还要比较立即执行价值。

### Monte Carlo {#mc}

欧式 payoff 的风险中性估计：

\[
\hat C=e^{-rT}\frac1N\sum_{i=1}^N(S_T^{(i)}-K)^+.
\]

标准误按 \(O(N^{-1/2})\) 收敛；antithetic variates、control variates、quasi-Monte Carlo 可降方差。路径依赖和提前执行需要更专门算法。

## 数据与实现契约 {#math}

| 项目 | 必须冻结 |
|---|---|
| 固收 | 现金流、日计数、结算、票息频率、曲线、插值、信用/流动性 |
| 期权 | 标的、行权价、期限、分红、利率、波动率曲面、期权类型 |
| 数值 | 网格/步数、随机 seed、路径数、误差容忍、收敛对照 |
| 对冲 | 再平衡频率、成本、跳跃、流动性、保证金和融资 |
| 估值 | market/model input 时间戳和 `available_at <= asof_at` |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
curve = bootstrap_discount_curve(instruments, conventions, asof_at)
bond = present_value(cashflows, curve)
duration = finite_difference_or_analytic_sensitivity(bond, curve)
option_bs = black_scholes_call(S, K, r, sigma, T)
option_tree = crr_tree_call(S, K, r, sigma, T, steps=600)
option_mc, se = monte_carlo_call(S, K, r, sigma, T, antithetic=True)
assert_abs(option_tree - option_bs) < tolerance
assert_abs(option_mc - option_bs) < 4 * se
```

实现见 [`m07_pricing_methods.py`](../tools/m07_pricing_methods.py)，结果见 [`m07_pricing_methods_results.json`](../data/m07_pricing_methods_results.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/tools/m07_pricing_methods.py
python quant_finance/data/test_m07_pricing_methods.py -v
```

| 项目 | 结果 |
|---|---:|
| 5 年、4% 票息、4.5% YTM 债券价格 | 97.7834 |
| Macaulay duration | 4.5753 |
| Modified duration | 4.4747 |
| Black–Scholes call | 9.4134 |
| 600 步二叉树 | 9.4101 |
| Antithetic Monte Carlo | 9.4065 |
| Monte Carlo 标准误 | 0.03148 |

二叉树绝对误差约 0.0033；Monte Carlo 与解析解差异小于四倍模拟标准误。测试还验证债券价格为正且 Macaulay duration 大于 modified duration。

## 方法对比与失败案例 {#comparison}

| 方法 | 优点 | 主要边界 |
|---|---|---|
| 解析 Black–Scholes | 快、可算 Greeks | 常数波动率、欧式、连续对冲假设 |
| 二叉树 | 直观、可处理美式执行 | 步数和树参数影响收敛 |
| Monte Carlo | 适合多因子/路径依赖 | 收敛慢、提前执行困难 |
| 久期/凸性 | 快速利率敏感度 | 默认局部/特定曲线冲击 |
| 完整重估 | 捕获非线性 | 依赖完整市场和模型输入 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| M07-Q01 | 折现因子是什么？ | T 时点一单位现金流的现值。 |
| M07-Q02 | YTM 与即期曲线区别？ | 单一 IRR vs 各期限零息利率。 |
| M07-Q03 | modified duration 如何解释？ | 收益率小变动下价格相对敏感度。 |
| M07-Q04 | 为什么需要凸性？ | 久期是一阶近似，大变动有曲率。 |
| M07-Q05 | 风险中性概率是真实概率吗？ | 不是，是无套利定价测度。 |
| M07-Q06 | Black–Scholes 的 d1/d2 是什么？ | 能写出含 S、K、r、sigma、T 的公式。 |
| M07-Q07 | CRR 风险中性概率？ | \((e^{r\Delta t}-d)/(u-d)\)。 |
| M07-Q08 | 美式树多哪一步？ | 节点比较继续持有与立即执行。 |
| M07-Q09 | Monte Carlo 标准误速率？ | \(N^{-1/2}\)。 |
| M07-Q10 | antithetic 作用？ | 用负相关路径降低方差。 |
| M07-Q11 | 隐含波动率是什么？ | 反解使模型价等于市场价的 sigma。 |
| M07-Q12 | 波动率微笑说明什么？ | 常数波动率模型与市场截面不符。 |
| M07-Q13 | Delta 对冲为何仍有误差？ | 离散、成本、跳跃和模型错设。 |
| M07-Q14 | 曲线 bootstrap 需登记什么？ | 工具、日计数、结算、插值和顺序。 |
| M07-Q15 | key-rate duration 用途？ | 非平行期限结构冲击。 |
| M07-Q16 | MC 能直接处理美式期权吗？ | 不能直接，需 LSM 等方法。 |
| M07-Q17 | 价格交叉验证为什么重要？ | 检查公式、索引、概率和单位错误。 |
| M07-Q18 | point-in-time 如何进入估值？ | 所有曲线/波动率输入必须在 asof 前可见。 |
| M07-Q19 | 本地实验支持什么？ | 支持数值一致性，不支持市场校准。 |
| M07-Q20 | 何时暂停估值结论？ | 合约、曲线、单位或收敛闸门失败时。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| M07-Q01 | \(P(0,T)\) 是未来单位现金流现值。 |
| M07-Q02 | YTM 是单一 IRR，即期曲线按期限变化。 |
| M07-Q03 | \(\Delta B/B\approx-D_{mod}\Delta y\)。 |
| M07-Q04 | 二阶价格—收益率曲率修正一阶误差。 |
| M07-Q05 | 风险中性是定价测度，不是真实分布。 |
| M07-Q06 | 正确写出对数 moneyness、r、sigma 和 T。 |
| M07-Q07 | \(q=(e^{r\Delta t}-d)/(u-d)\)。 |
| M07-Q08 | 每节点取继续价值和立即执行价值最大值。 |
| M07-Q09 | 标准误随路径数平方根倒数下降。 |
| M07-Q10 | z 与 -z 配对降低 payoff 均值方差。 |
| M07-Q11 | 从市场价反解模型 sigma。 |
| M07-Q12 | 不同行权价/期限需要不同隐含波动率。 |
| M07-Q13 | 连续复制假设在现实中不成立。 |
| M07-Q14 | 报价工具、惯例、插值、顺序和 asof。 |
| M07-Q15 | 衡量局部期限点的曲线风险。 |
| M07-Q16 | 需回归继续价值等提前执行算法。 |
| M07-Q17 | 独立实现应在误差容忍内收敛。 |
| M07-Q18 | 输入满足 `available_at <= asof_at`。 |
| M07-Q19 | 只验证公式和数值方法。 |
| M07-Q20 | 合约/输入/单位/收敛任一失败。 |

## 风险与后续建议（Risks & Next） {#risks}

- 固定平坦收益率不是真实曲线；未覆盖信用利差、可赎回、浮息、抵押和多曲线框架。
- Black–Scholes 实验未覆盖分红、随机波动率、跳跃、微笑校准和 Greeks 对冲 P&L。
- 下一 slice G14/M08 将进入组合优化、Black–Litterman、因子风险、VaR/ES 和压力测试，并使用本模块的非线性重估边界。

## 参考文献（References） {#references}

1. [1] Fischer Black and Myron Scholes, “The Pricing of Options and Corporate Liabilities,” *Journal of Political Economy*, 1973. [链接](https://doi.org/10.1086/260062)
2. [2] Robert C. Merton, “Theory of Rational Option Pricing,” *Bell Journal of Economics and Management Science*, 1973. [链接](https://www.jstor.org/stable/3003143)
3. [3] John C. Cox, Stephen A. Ross, and Mark Rubinstein, “Option Pricing: A Simplified Approach,” *Journal of Financial Economics*, 1979. [链接](https://doi.org/10.1016/0304-405X(79)90015-1)
