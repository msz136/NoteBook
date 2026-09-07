---
title: 面板与因果识别：FE/RE、IV、DiD、RDD 与合成控制
subtitle: M05 · 先写识别假设，再运行估计器与安慰剂检验
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Panel and Causal Identification
---

# 面板与因果识别：FE/RE、IV、DiD、RDD 与合成控制

## 问题（Question） {#question}

面板回归为什么不能只看固定效应系数？工具变量、双重差分、断点回归和合成控制分别依赖什么不可由软件输出自动证明的假设？本模块用合成数据验证 within-FE、2SLS 和两期 DiD 的实现，同时把 RE、RDD 和合成控制作为完整识别地图的一部分。

## 背景与动机（Background & Motivation） {#background}

Hansen 的计量教材和 MIT 14.382 提供面板、内生性和渐近推断框架；`linearmodels` 官方文档提供 Panel、IV/2SLS、GMM 与相关模型的实现入口。[1–3] Card 与 Krueger 的政策比较、Imbens 与 Lemieux 的 RDD 指南、Abadie 等人的合成控制工作分别代表准实验设计的重要入口。[4–6] 这些方法依赖研究设计，不能由显著性或拟合优度替代。

<div class="evidence"><strong>证据边界：</strong>公式和识别边界由教材、课程、官方文档和原始文献支持；本地 FE/IV/DiD 数值来自已知真值的合成数据，只验证实现和失败方向。RDD、RE、合成控制未在本 slice 声称完成真实估计。</div>

## 基础概念与术语 {#concepts}

| 方法 | 识别对象 | 核心假设 |
|---|---|---|
| 固定效应（FE） | 控制个体不随时间变化的不可观测异质性 | 严格/序列外生性、足够的组内变动 |
| 随机效应（RE） | 合并组间与组内信息 | 个体效应与解释变量不相关 |
| 工具变量（IV/2SLS） | 内生解释变量的局部结构效应 | 相关性、排除限制、独立性及解释所需条件 |
| 双重差分（DiD） | 处理组相对对照组的变化 | 平行趋势、无预期、无同时冲击 |
| 断点回归（RDD） | 阈值附近的局部处理效应 | 阈值附近连续性、不能精确操纵 running variable |
| 合成控制 | 单一/少数处理单元的反事实路径 | 处理前拟合、供体池可比、无污染 |

## 方法与数学形式（Methods & Mathematical Form） {#methods}

### FE 与 RE {#panel}

面板模型：

\[
y_{it}=x_{it}'\beta+\alpha_i+\lambda_t+u_{it}.
\]

within 变换从每个实体减去时间均值，消去 \(\alpha_i\)。若 \(x_{it}\) 几乎没有组内变化，FE 无法识别相应系数。RE 只有在 \(E[\alpha_i\mid X_i]=0\) 时更有效；Hausman 检验只是辅助证据，不会证明外生性。

### IV / 2SLS {#iv}

第一阶段与第二阶段：

\[
x_i=\pi_0+z_i'\pi+v_i,\qquad y_i=\beta\hat x_i+w_i'\gamma+u_i.
\]

工具 \(z\) 必须与内生变量相关，并满足 \(E[z_iu_i]=0\)。第一阶段强不等于排除限制成立；弱工具会使常规 2SLS 推断严重失真。

### DiD 与事件研究 {#did}

两组两期 DiD：

\[
\hat\tau_{DiD}=(\bar Y_{T,post}-\bar Y_{T,pre})-(\bar Y_{C,post}-\bar Y_{C,pre}).
\]

多期事件研究应画出处理前系数及置信区间，检查预趋势；错位采用处理下，简单 TWFE 可能混合异质处理效应，需要适当分组/队列估计器。

### RDD 与合成控制 {#rdd-scm}

Sharp RDD 估计阈值 \(c\) 两侧条件均值极限之差：

\[
\tau_{RDD}=\lim_{x\downarrow c}E[Y\mid X=x]-\lim_{x\uparrow c}E[Y\mid X=x].
\]

应报告带宽、核函数、多项式阶数、密度操纵和协变量平衡。合成控制选择非负、和为一的供体权重，使处理前特征/结果路径逼近处理单元；处理后缺口需用空间/时间安慰剂判断是否异常。

## 识别与推断契约 {#math}

| 闸门 | 必须回答 |
|---|---|
| 时间与样本 | 处理何时发生？数据当时是否可见？是否选择性进入面板？ |
| 估计对象 | ATE、ATT、LATE、局部阈值效应还是预测相关？ |
| 反事实 | 哪些单位/时期构成未处理路径？为何可比？ |
| 标准误 | 是否按处理分配层级聚类？聚类数是否足够？ |
| 安慰剂 | 假处理时间、假阈值、伪结果、伪供体是否无效？ |
| 外推 | 局部或样本内效应能否推广到其他市场/时期？ |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
panel = load_point_in_time_panel(asof_at)  # 继承 M02/P1
estimand = freeze_estimand(population, treatment, outcome, horizon)
design = choose_design(FE_or_IV_or_DiD_or_RDD_or_SCM)
assert_identification_assumptions_are_testable_or_explicit(design)
estimate = fit_with_clustered_or_robust_inference(panel, design)
placebos = run_pretrend_fake_date_fake_cutoff_and_donor_tests(panel, design)
report(estimate, placebos, failures, external_validity_boundary)
```

可执行 FE/2SLS/DiD 实验见 [`m05_causal_panel.py`](../tools/m05_causal_panel.py)，结果见 [`m05_causal_panel_results.json`](../data/m05_causal_panel_results.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/tools/m05_causal_panel.py
python quant_finance/data/test_m05_causal_panel.py -v
```

合成 FE 面板让解释变量与个体效应相关：pooled OLS 明显偏离真值，而 within-FE 接近真值。IV 实验让 \(x\) 与结构误差相关，OLS 偏误大于 2SLS；DiD 在平行趋势生成机制下接近注入的 1.5 处理效应。测试只验证这些已知机制，不证明现实研究的排除限制或平行趋势。

## 失败案例与方法选择 {#comparison}

| 失败 | 错误结论 | 修复/边界 |
|---|---|---|
| FE 后仍有时间变化混杂 | 把遗漏冲击当处理效应 | 时间 FE、趋势、设计与安慰剂 |
| RE 与 \(x\) 相关 | RE 不一致 | FE/相关随机效应并解释假设 |
| 弱或无效工具 | 2SLS 失真 | 第一阶段、弱 IV 稳健推断、排除限制论证 |
| DiD 预趋势不平行 | 反事实不可信 | 事件研究、替代对照、重新定义设计 |
| RDD 带宽挑选 | 阈值结果不稳 | 数据驱动带宽、偏差校正、敏感性图 |
| SCM 供体污染 | 合成反事实被处理影响 | 清理供体池、空间/时间安慰剂 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| M05-Q01 | FE 消去什么？ | 不随时间变化的个体效应。 |
| M05-Q02 | FE 不能解决什么？ | 时间变化混杂、反向因果和测量误差。 |
| M05-Q03 | RE 的关键附加假设？ | 个体效应与解释变量不相关。 |
| M05-Q04 | 2SLS 两阶段是什么？ | 用工具预测内生变量，再用预测值估计结果。 |
| M05-Q05 | 第一阶段强是否证明工具有效？ | 否，还需排除限制与独立性。 |
| M05-Q06 | LATE 的含义？ | 对工具影响处理的服从者局部平均效应。 |
| M05-Q07 | DiD 平行趋势是什么？ | 无处理时两组平均结果变化相同。 |
| M05-Q08 | 如何查预趋势？ | 事件研究处理前系数及联合检验。 |
| M05-Q09 | 错位处理 TWFE 有何风险？ | 异质效应下出现不当比较和权重。 |
| M05-Q10 | RDD 识别何种效应？ | 阈值附近的局部效应。 |
| M05-Q11 | RDD 如何检查操纵？ | running variable 密度和协变量平衡。 |
| M05-Q12 | 合成控制权重约束？ | 通常非负且和为一。 |
| M05-Q13 | SCM 如何做安慰剂？ | 轮流把未处理单位/时间当处理。 |
| M05-Q14 | 标准误为何按处理层级聚类？ | 处理分配与误差依赖在该层级。 |
| M05-Q15 | pooled OLS 与 FE 为什么不同？ | 个体效应和 x 相关时 pooled 有遗漏偏误。 |
| M05-Q16 | point-in-time 与因果有何关系？ | 未来信息会破坏处理/协变量的历史信息集。 |
| M05-Q17 | 安慰剂通过能证明识别吗？ | 不能，只排除特定失败模式。 |
| M05-Q18 | 局部效应能否外推？ | 需要额外可迁移性证据。 |
| M05-Q19 | 合成实验支持什么？ | 支持实现路径，不支持现实因果结论。 |
| M05-Q20 | 何时暂停因果语言？ | 反事实、时间、工具或趋势假设无法辩护时。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| M05-Q01 | 消去时间不变的 \(\alpha_i\)。 |
| M05-Q02 | 不消除时间变化混杂和内生性。 |
| M05-Q03 | \(E[\alpha_i\mid X_i]=0\)。 |
| M05-Q04 | 第一阶段投影 x，第二阶段用 x-hat。 |
| M05-Q05 | 相关性不等于排除限制。 |
| M05-Q06 | 工具诱导处理变化者的局部平均效应。 |
| M05-Q07 | 无处理反事实中两组趋势相同。 |
| M05-Q08 | 检查处理前 lead 系数和联合显著性。 |
| M05-Q09 | 早处理组可能错误充当晚处理组对照。 |
| M05-Q10 | cutoff 附近局部效应。 |
| M05-Q11 | 密度、协变量连续性和带宽敏感性。 |
| M05-Q12 | 供体权重通常非负且总和为一。 |
| M05-Q13 | 假单位、假时间重复估计缺口。 |
| M05-Q14 | 使推断匹配处理分配和误差相关结构。 |
| M05-Q15 | pooled 遗漏与 x 相关的实体效应。 |
| M05-Q16 | 所有协变量/处理必须在 asof 前可见。 |
| M05-Q17 | 只能排除被测试的伪效应模式。 |
| M05-Q18 | 需额外外部有效性/可迁移性假设。 |
| M05-Q19 | 验证代码和已知 DGP 下的方向。 |
| M05-Q20 | 核心识别假设无法陈述或证伪时。 |

## 风险与后续建议（Risks & Next） {#risks}

- 当前环境未安装 `linearmodels`，本地脚本使用 NumPy 教学实现；聚类标准误、弱 IV 稳健区间和现代 staggered DiD 估计需后续库环境。
- RDD 与合成控制只完成方法、诊断与伪代码契约，没有真实估计输出。
- 下一 slice G11/M06 将进入 CAPM/SDF、Fama–French 与 Fama–MacBeth 资产定价检验，必须继续区分预测、因果和定价误差。

## 参考文献（References） {#references}

1. [1] Bruce E. Hansen, “Econometrics.” [链接](https://www.ssc.wisc.edu/~bhansen/econometrics/)
2. [2] MIT OpenCourseWare, “14.382 Econometrics,” 2017. [链接](https://ocw.mit.edu/courses/14-382-econometrics-spring-2017/)
3. [3] linearmodels documentation. [链接](https://bashtage.github.io/linearmodels/)
4. [4] David Card and Alan B. Krueger, “Minimum Wages and Employment,” *American Economic Review*, 1994. [链接](https://www.jstor.org/stable/2118030)
5. [5] Guido W. Imbens and Thomas Lemieux, “Regression Discontinuity Designs: A Guide to Practice,” *Journal of Econometrics*, 2008. [链接](https://doi.org/10.1016/j.jeconom.2007.05.001)
6. [6] Alberto Abadie, Alexis Diamond, and Jens Hainmueller, “Synthetic Control Methods for Comparative Case Studies,” *JASA*, 2010. [链接](https://doi.org/10.1198/jasa.2009.ap08746)
