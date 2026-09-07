---
title: 量化研究的数学、概率、统计与优化基础
subtitle: M01 · 从线性代数到稳定数值实现的最小推导链
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Mathematical Foundations
---

# 量化研究的数学、概率、统计与优化基础

## 问题（Question） {#question}

后续的 OLS、GMM、因子模型、时间序列、衍生品、组合优化和机器学习为什么反复出现投影、条件期望、协方差、梯度、Hessian、凸性与数值条件数？本模块建立一条够用且可检验的基础链：先理解对象和假设，再推导公式，最后映射到稳定代码。

完成 M01 后，学习者应能解释而非背诵关键公式；能检查矩阵形状、随机变量条件和优化约束；能说明什么时候只应做数值求解而不显式求逆；并能完成 24 道手算、解释与代码设计题。完整 Monte Carlo 与 Bootstrap 实验属于下一 slice G04/P0，本模块不伪造尚未运行的实验结果。

## 背景与动机（Background & Motivation） {#background}

MIT 18.06 把线性方程组、向量空间、特征值与正定矩阵列为可迁移到其他学科的线性代数核心。[1] MIT 18.05 从随机变量与分布推进到 Bayesian inference、假设检验、置信区间和线性回归。[2] Hansen 将概率统计作为一年制博士计量序列的第一卷，再进入 Econometrics。[3] 这三条来源共同支持“先建立数学对象与抽样不确定性，再学习计量估计”的顺序。

优化侧，Boyd 与 Vandenberghe 的公开教材系统覆盖凸集合、凸函数、对偶、最优性条件与算法，并提供 CVX/CVXPY 等示例入口。[4] 数值实现侧，NumPy 官方 `linalg.lstsq` 直接求解欠定、适定或超定线性系统，并通过小奇异值截断处理秩判断。[5] 因此本模块强调 `solve/lstsq`、SVD 与条件数，而不是把数学推导机械翻译为矩阵求逆。

<div class="evidence"><strong>证据边界：</strong>本模块的定义与标准结论来自上述课程/教材。哪些内容“最适合量化先学”以及练习顺序是资料库的教学性综合。示例不包含真实资产数据，不能支持任何收益结论。</div>

## 基础概念与术语 {#concepts}

### 对象、维度和三种不确定性 {#objects-and-uncertainty}

| 层 | 关键对象 | 量化中的例子 | 常见错误 |
|---|---|---|---|
| 线性代数 | 向量、矩阵、子空间、投影、谱 | 特征矩阵、因子暴露、协方差 | 维度虽然能广播，经济含义却错误 |
| 微积分 | 梯度、Jacobian、Hessian、Taylor 展开 | 损失敏感度、Delta/Gamma、优化更新 | 把局部近似当全局结论 |
| 概率 | 随机变量、条件分布、期望、协方差 | 收益、状态、违约、订单流 | 把一次观测当分布参数 |
| 统计 | 估计量、抽样分布、区间、检验 | 均值、回归、风险参数 | 把样本内估计当已知真值 |
| 优化 | 决策变量、目标、约束、对偶 | 组合权重、对冲、执行计划 | 忽略估计误差与不可行性 |
| 数值计算 | 条件数、舍入、迭代误差、容差 | 近共线回归、大协方差矩阵 | 显式求逆或只看程序未报错 |

数据不确定性（未来随机）、参数不确定性（有限样本）和模型不确定性（设定可能错）不可互换。更多数据可能降低抽样误差，却不会自动修复错误目标、未来泄漏或结构变化。

### 学习依赖图 {#dependency-map}

```text
向量/矩阵形状 → 内积/范数 → 投影/最小二乘 → 回归与因子模型
        ↓             ↓             ↓
  特征值/SVD → PSD/协方差 → 条件数/正则化 → 稳定数值实现

概率空间 → 条件期望 → LLN/CLT → 估计量/区间 → 计量推断
    ↓          ↓          ↓            ↓
 联合分布 → 协方差   抽样分布      MLE/GMM/Bootstrap

微分 → 梯度/Hessian → 凸性 → KKT/对偶 → 组合与模型训练
```

## 线性代数：从数据矩阵到投影 {#methods}

### 向量、矩阵和形状 {#shapes}

令 \(X\in\mathbb R^{n\times k}\) 为特征矩阵，\(n\) 是样本数，\(k\) 是特征数；\(\beta\in\mathbb R^k\) 为参数向量，则线性预测为：

\[
\hat y=X\beta\in\mathbb R^n.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>第 \(i\) 个预测是第 \(i\) 行特征与 \(\beta\) 的内积。NumPy 中应检查 `X.shape == (n, k)`、`beta.shape == (k,)`；能广播成功不等于维度语义正确。</div>

### 内积、范数和投影 {#projection}

最小二乘把 \(y\) 投影到 \(X\) 的列空间。满列秩时的一阶条件为：

\[
X^\top(y-X\hat\beta)=0,
\qquad
\hat\beta=(X^\top X)^{-1}X^\top y.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>残差与每一列特征正交。右侧闭式解用于推导；代码应优先 `np.linalg.lstsq(X, y)` 或分解求解，避免显式构造 \((X^\top X)^{-1}\)，因为正规方程会放大条件数。[5]</div>

### 协方差矩阵与半正定性 {#covariance-psd}

随机向量 \(R\) 的协方差矩阵为 \(\Sigma=\mathbb E[(R-\mu)(R-\mu)^\top]\)。对任意权重 \(w\)：

\[
w^\top\Sigma w
=\operatorname{Var}(w^\top R)\ge 0.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>\(w^\top\Sigma w\) 是线性组合的方差，因此协方差矩阵应为半正定（positive semidefinite, PSD）。样本误差、缺失值处理或不一致数据可能产生数值上的小负特征值；修复前要先定位数据与估计原因。</div>

### 特征值、SVD 与条件数 {#svd-conditioning}

奇异值分解（Singular Value Decomposition, SVD）写为 \(X=U\operatorname{diag}(s_1,\ldots,s_r)V^\top\)。二范数条件数为：

\[
\kappa_2(X)=\frac{s_{\max}}{s_{\min}},
\]

其中分母取非零最小奇异值。

<div class="note"><strong>变量、直觉与实现映射：</strong>条件数大表示输入的微小扰动可能造成解的大变化。`np.linalg.lstsq` 的 `rcond` 通过相对阈值把很小的奇异值视为零；这改变有效秩，必须记录而不能当实现细节忽略。[5]</div>

## 微积分：从局部变化到优化 {#math}

### 梯度、Hessian 与 Taylor 展开 {#gradient-hessian}

对二次函数 \(q(w)=\tfrac12w^\top A w-b^\top w\)，梯度为：

\[
\nabla q(w)=\frac{A+A^\top}{2}w-b.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>当 \(A\) 对称时化为 \(Aw-b\)，Hessian 为 \(A\)。协方差矩阵理论上对称，但代码中仍应检查并用 `(A + A.T) / 2` 处理纯数值非对称，而不是掩盖严重数据错误。</div>

二阶 Taylor 近似为：

\[
f(x+\Delta)\approx f(x)+\nabla f(x)^\top\Delta
+\frac12\Delta^\top\nabla^2 f(x)\Delta.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>一阶项给局部方向敏感度，二阶项给曲率；期权 Delta/Gamma 与损失函数二阶方法都使用这种局部结构。步长过大或函数不光滑时近似会失效。</div>

### 链式法则与梯度检查 {#chain-rule}

复合函数 \(L(\theta)=\ell(f_\theta(x),y)\) 的梯度由链式法则连接模型 Jacobian 与损失梯度。实现后可用中心有限差分检查第 \(j\) 维：

\[
\frac{\partial L}{\partial\theta_j}
\approx\frac{L(\theta+h e_j)-L(\theta-h e_j)}{2h}.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>\(e_j\) 是第 \(j\) 个基向量，\(h\) 是小步长。太大的 \(h\) 有截断误差，太小会受浮点抵消影响；梯度检查用于调试，不替代解析/自动微分训练。</div>

## 概率：条件信息与极限定理 {#probability}

### 条件期望和迭代期望 {#conditional-expectation}

条件期望 \(\mathbb E[Y\mid X]\) 是给定信息 \(X\) 后对 \(Y\) 的均方误差最优预测。迭代期望定律为：

\[
\mathbb E[Y]=\mathbb E\!\left[\mathbb E[Y\mid X]\right].
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>先在每个信息状态内平均，再对状态平均，得到总体均值。金融预测中必须明确 \(X\) 的信息时点；把未来修订放入 \(X_t\) 会破坏条件信息定义。[2][3]</div>

全方差公式为：

\[
\operatorname{Var}(Y)
=\mathbb E[\operatorname{Var}(Y\mid X)]
+\operatorname{Var}(\mathbb E[Y\mid X]).
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>总不确定性分为状态内噪声与状态间可解释差异。这是风险分解和层级模型的重要直觉，但不能把第二项自动解释为因果贡献。</div>

### LLN 与 CLT {#lln-clt}

在独立同分布且一阶矩存在等典型条件下，大数定律（Law of Large Numbers, LLN）说明：

\[
\bar X_n=\frac1n\sum_{i=1}^nX_i\xrightarrow{p}\mu.
\]

在方差有限等条件下，中心极限定理（Central Limit Theorem, CLT）给出：

\[
\sqrt n\,\frac{\bar X_n-\mu}{\sigma}\xrightarrow{d}\mathcal N(0,1).
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>LLN回答样本均值是否靠近总体均值，CLT描述标准化误差的近似分布。金融序列常有依赖、异方差和厚尾，不能无条件套用 iid 版本；后续模块会更换相应条件与标准误。[2][3]</div>

### 协方差不等于独立 {#dependence}

协方差 \(\operatorname{Cov}(X,Y)=\mathbb E[(X-\mu_X)(Y-\mu_Y)]\) 只测线性共同变化。独立通常推出零协方差（矩存在时），反向不成立。例如令 \(X\) 关于零对称且 \(Y=X^2\)，可有零协方差但显然依赖。

## 统计推断：估计量是随机对象 {#statistics}

### 偏差、方差与均方误差 {#bias-variance}

对参数 \(\theta\) 的估计量 \(\hat\theta\)，均方误差分解为：

\[
\mathbb E[(\hat\theta-\theta)^2]
=\operatorname{Var}(\hat\theta)
+\operatorname{Bias}(\hat\theta)^2.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>无偏不是唯一目标；小幅偏差可能换来更低方差。回测比较模型时必须在冻结的未来样本上评估整体损失，不能只比较训练拟合。</div>

### 置信区间与检验 {#intervals-tests}

若估计量近似满足 \((\hat\theta-\theta)/\widehat{\operatorname{se}}(\hat\theta)\approx\mathcal N(0,1)\)，常见双侧近似区间为：

\[
\hat\theta\pm z_{1-\alpha/2}\widehat{\operatorname{se}}(\hat\theta).
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>区间的覆盖解释来自重复抽样协议，不是参数的频率学派后验概率。时间依赖、异方差、聚类和模型选择都会改变标准误与覆盖率，需在后续计量模块处理。</div>

### MLE 与对数似然 {#mle}

给定密度或概率质量函数 \(p_\theta(x)\)，最大似然估计（Maximum Likelihood Estimation, MLE）为：

\[
\hat\theta_{\mathrm{MLE}}
=\arg\max_{\theta}\sum_{i=1}^n\log p_\theta(X_i).
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>使用对数把乘积变为求和并提高数值稳定性；零概率、极端 logits 和约束参数需要稳定函数，如 `log1p`、`logsumexp` 或受约束参数化。似然写错时，优化得再精确也没有统计意义。[2][3]</div>

### Bootstrap 的正确边界 {#bootstrap-preview}

Bootstrap 用经验分布重采样近似估计量的抽样分布。iid 行重采样不适用于所有金融时间序列；依赖数据可能需要 block bootstrap 等结构化方案。G04/P0 将运行覆盖率与有限样本实验，本节只冻结概念与失败条件。

## 凸优化：目标、约束与最优性 {#optimization}

### 标准形式与凸性 {#convexity}

一个凸优化问题可写为：

\[
\min_x f_0(x)
\quad\text{s.t.}\quad
f_i(x)\le0,\; i=1,\ldots,m,
\quad Ax=b,
\]

其中目标和不等式函数为凸函数，等式约束为仿射。[4]

<div class="note"><strong>变量、直觉与实现映射：</strong>凸性使局部最优也是全局最优，并允许使用成熟求解器；这不表示输入均值、协方差或约束就是准确的。求解器状态、容差和不可行证明必须记录。</div>

### Lagrangian 与 KKT {#kkt}

Lagrangian 为 \(\mathcal L(x,\lambda,\nu)=f_0(x)+\sum_i\lambda_i f_i(x)+\nu^\top(Ax-b)\)。在适当正则条件下，KKT 条件包括原始可行、对偶可行、互补松弛和驻点：

\[
\nabla_x\mathcal L(x^*,\lambda^*,\nu^*)=0,
\qquad
\lambda_i^*f_i(x^*)=0,
\qquad
\lambda_i^*\ge0.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>乘子衡量约束边际放宽的影子价格；互补松弛说明不活跃约束的乘子为零。代码中应同时检查目标值、约束残差和求解状态，而不只读取权重向量。[4]</div>

### 组合二次目标作为接口示例 {#portfolio-interface}

均值—方差型接口可写为：

\[
\min_w\;\frac{\gamma}{2}w^\top\Sigma w-\mu^\top w
\quad\text{s.t.}\quad\mathbf 1^\top w=1,\; l\le w\le u.
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>\(w\) 是权重，\(\mu\) 是预期收益估计，\(\Sigma\) 是协方差，\(\gamma\) 是风险厌恶系数，\(l,u\) 是持仓边界。该式只展示数学接口；估计误差、换手、成本和容量将在 M08/P4 进入，不能据此宣称可投资。</div>

## Pipeline 与伪代码 {#pipeline}

```python
def solve_and_audit_least_squares(X, y, rcond=None):
    # 1. 检查样本维、特征维、有限值与目标长度，避免“能广播但语义错”。
    assert X.ndim == 2 and y.ndim == 1
    assert X.shape[0] == y.shape[0]
    assert np.isfinite(X).all() and np.isfinite(y).all()

    # 2. 用 SVD 驱动的 lstsq 求解；不要显式计算 inv(X.T @ X)。
    beta, residuals, rank, singular_values = np.linalg.lstsq(X, y, rcond=rcond)

    # 3. 记录有效秩与条件数；程序成功返回不代表问题数值稳定。
    positive = singular_values[singular_values > 0]
    condition_number = positive.max() / positive.min()

    # 4. 验证一阶正交条件，并把容差、版本和输入哈希写入实验记录。
    error = y - X @ beta
    orthogonality = np.linalg.norm(X.T @ error)
    return beta, rank, condition_number, orthogonality
```

该伪代码映射 NumPy 官方 `lstsq` 的输出语义。[5] 它不完成统计推断：是否加入截距、误差是否相关、标准误如何计算和参数如何解释属于 M03。

## 实现证据与数值坏案例 {#implementation}

### 不要用显式逆解决最小二乘 {#no-explicit-inverse}

```python
# 不推荐：正规方程会平方条件数，还显式构造矩阵逆。
beta_bad = np.linalg.inv(X.T @ X) @ X.T @ y

# 推荐起点：直接最小二乘，返回残差、秩和奇异值供审计。
beta, residuals, rank, singular_values = np.linalg.lstsq(X, y, rcond=None)
```

### 稳定计算 Bernoulli 对数似然 {#stable-loglik}

```python
def bernoulli_loglik_from_logits(logits, y):
    # log(sigmoid(z)) = -logaddexp(0, -z)，避免大正/负 logits 上溢。
    log_p = -np.logaddexp(0.0, -logits)
    log_one_minus_p = -np.logaddexp(0.0, logits)
    return np.sum(y * log_p + (1 - y) * log_one_minus_p)
```

### 中心差分梯度检查 {#gradient-check-code}

```python
def central_difference(loss_fn, theta, index, step=1e-5):
    # 复制参数，避免原地修改污染下一次函数计算。
    plus, minus = theta.copy(), theta.copy()
    plus[index] += step
    minus[index] -= step
    return (loss_fn(plus) - loss_fn(minus)) / (2.0 * step)
```

## 练习：24 题验收 {#exercises}

### A. 线性代数与数值稳定性 {#exercise-a}

| ID | 题目 |
|---|---|
| M01-Q01 | 写出 \(X\in\mathbb R^{200\times12}\)、\(\beta\in\mathbb R^{12}\) 时 \(X\beta\) 与 \(X^\top X\) 的形状。 |
| M01-Q02 | 从最小二乘目标推导正规方程，并解释残差正交于哪个空间。 |
| M01-Q03 | 证明协方差矩阵为 PSD；说明样本矩阵出现明显负特征值时先查什么。 |
| M01-Q04 | 两个奇异值为 100 与 0.001，计算条件数并解释风险。 |

### B. 微积分 {#exercise-b}

| ID | 题目 |
|---|---|
| M01-Q05 | 推导 \(\tfrac12w^\top A w-b^\top w\) 的梯度。 |
| M01-Q06 | Hessian 半正定与凸性有什么关系？严格凸还需要什么？ |
| M01-Q07 | 写出一元函数二阶 Taylor 展开及余项成立所需的光滑性直觉。 |
| M01-Q08 | 为 \(L(\theta)=(a^\top\theta-y)^2\) 推导梯度，并设计数值检查。 |

### C. 概率 {#exercise-c}

| ID | 题目 |
|---|---|
| M01-Q09 | 用迭代期望计算两状态混合分布的总体均值。 |
| M01-Q10 | 解释全方差公式两项各对应什么不确定性。 |
| M01-Q11 | 区分 LLN 与 CLT 的结论、缩放和用途。 |
| M01-Q12 | 构造零协方差但不独立的例子。 |

### D. 统计推断 {#exercise-d}

| ID | 题目 |
|---|---|
| M01-Q13 | 写出 MSE 的偏差—方差分解，并说明无偏为何不是唯一目标。 |
| M01-Q14 | 正确解释 95% 频率学派置信区间。 |
| M01-Q15 | 对 iid Bernoulli 样本推导 MLE。 |
| M01-Q16 | 为什么 iid 行重采样 Bootstrap 可能不适合日收益序列？ |

### E. 凸优化 {#exercise-e}

| ID | 题目 |
|---|---|
| M01-Q17 | 区分凸集合与凸函数，并各给一个例子。 |
| M01-Q18 | 列出 KKT 四类条件并解释互补松弛。 |
| M01-Q19 | 比较 L1 与 L2 正则的几何与解特征。 |
| M01-Q20 | 给均值—方差问题加入总杠杆与换手约束，只写数学接口。 |

### F. 实现与审计 {#exercise-f}

| ID | 题目 |
|---|---|
| M01-Q21 | 为什么 `lstsq` 通常优于显式 `inv(X.T @ X)`？ |
| M01-Q22 | 写出防止 Bernoulli log-likelihood 数值溢出的实现思路。 |
| M01-Q23 | 随机种子、包版本和输入哈希分别控制什么复现边界？ |
| M01-Q24 | 中心差分的步长太大与太小分别导致什么误差？ |

## 练习答案与评分边界 {#answers}

### A 答案 {#answer-a}

| ID | 通过边界 |
|---|---|
| M01-Q01 | \(X\beta\) 为 \((200,)\)，\(X^\top X\) 为 \((12,12)\)；能说明内维匹配。 |
| M01-Q02 | 对 \(\|y-X\beta\|_2^2\) 求导得 \(X^\top X\hat\beta=X^\top y\)；残差与 \(X\) 列空间正交。 |
| M01-Q03 | 对任意 \(w\)，\(w^\top\Sigma w=\operatorname{Var}(w^\top R)\ge0\)；先查缺失、不同步、非对称和估计/拼接错误。 |
| M01-Q04 | \(\kappa=100/0.001=100000\)；小扰动可能被放大，参数对数据和舍入敏感。 |

### B 答案 {#answer-b}

| ID | 通过边界 |
|---|---|
| M01-Q05 | \(\nabla q=(A+A^\top)w/2-b\)，对称时为 \(Aw-b\)。 |
| M01-Q06 | Hessian PSD 是二次可微函数凸性的条件；正定通常给严格凸，但需结合定义域。 |
| M01-Q07 | \(f(x+h)=f(x)+f'(x)h+f''(x)h^2/2+o(h^2)\)；需邻域内足够可微/连续。 |
| M01-Q08 | 梯度为 \(2a(a^\top\theta-y)\)；用多个维度的中心差分与解析梯度比较相对误差。 |

### C 答案 {#answer-c}

| ID | 通过边界 |
|---|---|
| M01-Q09 | 写出 \(\sum_s P(S=s)\mathbb E[Y\mid S=s]\)，并代入题设状态概率/均值。 |
| M01-Q10 | 第一项是给定状态后的平均残余方差，第二项是状态条件均值之间的方差。 |
| M01-Q11 | LLN 给平均的概率收敛；CLT 给 \(\sqrt n\) 标准化误差的分布收敛，用于近似推断。 |
| M01-Q12 | 对称 \(X\) 且 \(Y=X^2\)；\(Y\) 由 \(X\) 决定但可有 \(\operatorname{Cov}(X,Y)=0\)。 |

### D 答案 {#answer-d}

| ID | 通过边界 |
|---|---|
| M01-Q13 | MSE=方差+偏差平方；允许小偏差换取更低总误差，并说明必须样本外评价。 |
| M01-Q14 | 重复按同一程序构造的区间约 95% 覆盖固定真参数；不是本次区间的后验概率。 |
| M01-Q15 | 对数似然求导得到 \(\hat p=\bar X\)，并检查 \(p\in[0,1]\) 与边界样本。 |
| M01-Q16 | 时间依赖、波动聚集和重叠标签会被行重采样破坏；应使用保留依赖结构的方法并验证条件。 |

### E 答案 {#answer-e}

| ID | 通过边界 |
|---|---|
| M01-Q17 | 凸集合闭合于线段；凸函数满足 Jensen 不等式。例：仿射子空间与平方范数。 |
| M01-Q18 | 原始可行、对偶可行、互补松弛、驻点；不活跃不等式约束对应乘子为零。 |
| M01-Q19 | L2 球光滑、倾向收缩；L1 球有轴向尖角、常产生稀疏解，但结论依赖设计与目标。 |
| M01-Q20 | 可写 \(\|w\|_1\le L\) 与 \(\|w-w_{prev}\|_1\le\tau\)，同时保留预算与持仓边界。 |

### F 答案 {#answer-f}

| ID | 通过边界 |
|---|---|
| M01-Q21 | 显式逆更慢且数值差，正规方程平方条件数；`lstsq` 用分解并返回秩/奇异值供审计。[5] |
| M01-Q22 | 从 logits 用 `logaddexp`/softplus 形式计算 `log(sigmoid)` 与 `log(1-sigmoid)`，避免先算极端概率。 |
| M01-Q23 | 种子冻结伪随机路径，版本冻结实现语义，输入哈希冻结数据字节；三者都不能替代实验协议。 |
| M01-Q24 | 步长大有 Taylor 截断误差，步长小有浮点抵消/舍入误差；应扫描步长并比较相对误差。 |

## 方法对比与选择建议 {#comparison}

| 场景 | 首选工具/思路 | 避免 | 原因 |
|---|---|---|---|
| 线性系统 | `solve`、QR、SVD、`lstsq` | 显式矩阵逆 | 稳定性与秩信息更好 |
| 高条件数 | 标准化、SVD、正则化、重新定义特征 | 只增加小数位 | 问题来自信息几何，不只是显示精度 |
| 有限样本推断 | 报告估计量、标准误、区间与条件 | 只报点估计 | 参数估计本身是随机对象 |
| 时间依赖数据 | 使用与依赖结构匹配的极限定理/重采样 | 默认 iid | 金融数据常违背独立同分布 |
| 凸问题 | 成熟求解器 + KKT/残差审计 | 手写不受控梯度下降 | 可利用全局结构和可靠状态 |
| 非凸问题 | 多起点、基准、敏感性与失败登记 | 把单次收敛当全局最优 | 局部解和初始化依赖显著 |

## 风险与后续建议 {#risks}

- 本模块覆盖“后续够用”的最小基础，不替代完整数学专业课程。
- LLN、CLT、置信区间和 Bootstrap 的结论都依赖条件；金融厚尾、依赖与结构变化会要求更专门的版本。
- 凸优化能保证数学问题的全局结构，不能保证输入估计、交易成本或目标函数符合现实。
- 代码片段是接口示例，尚未运行系统性的覆盖率、有限样本和数值压力实验；这些由 G04/P0 执行并保存结果。
- 学习者只有在 24 题中至少 20 题通过，且 A、C、F 三组各不少于 3 题通过后，才建议进入 P0；否则按错题回补对应章节。

## 参考文献（References） {#references}

1. [1] Gilbert Strang, “18.06 Linear Algebra,” MIT OpenCourseWare, Spring 2010. [链接](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/)
2. [2] Jeremy Orloff and Jonathan Bloom, “18.05 Introduction to Probability and Statistics,” MIT OpenCourseWare, Spring 2022. [链接](https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/)
3. [3] Bruce E. Hansen, *Probability and Statistics for Economists*, Princeton University Press, 2022；作者代码入口. [链接](https://www.ssc.wisc.edu/~bhansen/probability/)
4. [4] Stephen Boyd and Lieven Vandenberghe, *Convex Optimization*, Cambridge University Press, 2004；作者公开网页与材料. [链接](https://web.stanford.edu/~boyd/cvxbook/)
5. [5] NumPy Developers, “numpy.linalg.lstsq,” NumPy Reference, 核验于 2026-07-22. [链接](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html)
6. [6] Thomas J. Sargent and John Stachurski, *Intermediate Quantitative Economics with Python*, QuantEcon. [链接](https://python.quantecon.org/)
