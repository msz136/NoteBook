---
title: 因子研究与金融机器学习：时序验证、概率预测与消融
subtitle: M10 · 用标签区间、purging/embargo 和失败登记阻断金融 ML 泄漏
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Factor Research and Financial ML
---

# 因子研究与金融机器学习：时序验证、概率预测与消融

## 问题（Question） {#question}

为什么普通随机交叉验证会高估金融模型？当标签覆盖未来五天时，如何按标签区间 purge 相邻训练样本并设置 embargo？正则化、树模型和概率预测如何评估，消融与多重检验怎样防止把偶然相关包装成 alpha？

## 背景与动机（Background & Motivation） {#background}

金融 ML 的困难通常不是“模型不够复杂”，而是低信噪比、非平稳、重叠标签、反复试验和交易成本。Carr 与 López de Prado 强调反复用同一历史校准规则会产生回测过拟合；White 的 Reality Check 针对数据窥探下的模型比较。[1][2] 本模块把样本时间、标签开始/结束、可用时间和实验家族写成一等字段。

<div class="evidence"><strong>证据边界：</strong>本地实验使用合成序列和手写 ridge logistic 模型，只验证 purge/embargo、概率评分和单特征消融。未运行 scikit-learn、树模型或真实市场回测，不支持真实 alpha、模型优越性或部署主张。</div>

## 研究对象与特征契约 {#concepts}

| 对象 | 必须定义 | 泄漏风险 |
|---|---|---|
| 特征时间 | `feature_time` 与 `available_at` | 修订、收盘后数据回填 |
| 标签区间 | `label_start`, `label_end` | 重叠未来收益跨过切分 |
| universe | point-in-time 成员和可交易性 | 幸存者偏差 |
| 预测对象 | 回报、方向、分位数或波动率 | 目标与交易时点不一致 |
| 实验族 | 所有特征/模型/超参尝试 | 只报告最好结果 |
| 经济映射 | 仓位、成本、容量和延迟 | 统计分数无法兑现 |

## 时序切分、Purging 与 Embargo {#validation}

若样本 \(i\) 的标签使用区间 \([t_i^{start},t_i^{end}]\)，测试区间为 \([T_0,T_1]\)，purging 删除与测试标签区间重叠的训练样本。Embargo 再删除测试边界附近的一段时间，减少相邻信息依赖。

本地契约是：

\[
label\_end_i<T_0-e,
\qquad feature\_time_j\ge T_0\quad(j\in test),
\]

其中 \(e\) 为 embargo 长度。Embargo 不是固定魔法数字，应根据持有期、标签重叠、数据生成和执行延迟确定。

## 模型与概率预测 {#models}

### 正则化线性模型 {#regularization}

Ridge logistic 最小化负对数似然与 L2 惩罚：

\[
\min_\beta -\frac1n\sum_i[y_i\log p_i+(1-y_i)\log(1-p_i)]+\lambda\|\beta\|_2^2,
\quad p_i=\sigma(x_i'\beta).
\]

正则化降低方差但不修复泄漏或标签错误；标准化参数必须只从训练窗口估计。

### 树模型与时序 ML {#trees}

随机森林、梯度提升和神经时序模型能拟合非线性，但更容易吸收制度、标识和数据处理泄漏。模型比较应共享相同 fold、样本、成本和调参预算；特征重要性需用 permutation、SHAP 或消融交叉核对，而不是把 split gain 当因果贡献。

### 概率评分与校准 {#probability}

Brier score 与 log loss：

\[
BS=\frac1n\sum_i(p_i-y_i)^2,
\qquad LL=-\frac1n\sum_i[y_i\log p_i+(1-y_i)\log(1-p_i)].
\]

方向准确率忽略置信度；概率模型还应报告 calibration curve、基准发生率和分组稳定性。交易阈值必须在验证集冻结。

## 消融、多重检验与坏案例 {#multiple-testing}

| 检查 | 要回答的问题 |
|---|---|
| 特征消融 | 删除该特征后样本外分数是否稳定恶化？ |
| 时间/市场切片 | 效果是否只存在单一制度或资产？ |
| 标签置换 | 无真实关系时流程是否仍产生高分？ |
| 负对照 | 与机制无关的特征/结果是否也显著？ |
| 多重检验 | 尝试了多少策略、特征、窗口和阈值？ |
| 失败登记 | 被否决实验是否仍可见？ |

White Reality Check、SPA、FDR、deflated Sharpe 或 PBO 解决不同问题；不能混用成一个万能校正。

## 工程与数据契约 {#math}

| 层 | 冻结内容 |
|---|---|
| 数据 | source/version/hash、point-in-time、universe、时区/日历 |
| 特征 | 公式、窗口、缺失、标准化、available_at |
| 标签 | horizon、重叠、成交价、成本和退出规则 |
| 切分 | train/validation/test 时间、purge、embargo |
| 训练 | seed、包版本、超参搜索空间和预算 |
| 评估 | Brier/log loss/IC、校准、成本、容量、失败子样本 |

## Pipeline 与伪代码（Pipeline & Pseudocode） {#pipeline}

```python
samples = build_point_in_time_features_and_interval_labels(raw_data)
folds = walk_forward_split(samples, purge_overlapping_labels=True, embargo=10)
for fold in folds:
    scaler.fit(fold.train_only)
    model.fit(fold.train_only, regularization=chosen_on_validation)
    probability = model.predict_proba(fold.test)
    record_brier_logloss_calibration_and_economic_mapping(probability)
run_feature_ablation_label_permutation_and_regime_slices()
correct_or_disclose_multiple_testing(all_attempts)
```

实现见 [`m10_financial_ml.py`](../tools/m10_financial_ml.py)，结果见 [`m10_financial_ml_results.json`](../data/m10_financial_ml_results.json)。

## 实现证据与结果（Implementation & Results） {#implementation}

```powershell
python quant_finance/tools/m10_financial_ml.py
python quant_finance/data/test_m10_financial_ml.py -v
```

实验使用 720 个时点、5 日重叠标签、10 日 embargo 和 test_start=500。最大训练标签结束时点为 489，首个测试特征时点为 500，满足隔离契约。

| 指标 | 全特征模型 | 删除信号特征 |
|---|---:|---:|
| Brier | 0.24387 | 0.25133 |
| Log loss | 0.68020 | 0.69581 |
| Accuracy | 0.54884 | 0.50698 |

删除合成信号特征后 Brier 恶化 0.00746。测试验证 purge/embargo、不重叠、消融方向和 Brier 小于 0.25；结果不能外推到真实市场。

## 方法对比与失败案例 {#comparison}

| 失败 | 虚高来源 | 修复 |
|---|---|---|
| 随机 K-fold | 未来和重叠标签进入训练 | walk-forward + purge + embargo |
| 全样本标准化 | 测试分布进入 scaler | 每 fold 只 fit train |
| 用测试集调阈值 | 样本外被污染 | validation 冻结阈值 |
| 只报 accuracy | 忽略概率质量和基准率 | Brier、log loss、校准 |
| 特征重要性当因果 | 相关性/交互被误读 | 消融、置换和因果设计 |
| 只保留最佳实验 | 数据窥探 | 完整实验账本和校正 |

## 练习与答案边界（Exercises） {#exercises}

| ID | 题目 | 达标标准 |
|---|---|---|
| M10-Q01 | 为什么随机 K-fold 不适合重叠标签？ | 训练标签区间可覆盖测试未来。 |
| M10-Q02 | Purging 删除什么？ | 与测试标签区间重叠的训练样本。 |
| M10-Q03 | Embargo 作用？ | 隔离测试边界附近依赖。 |
| M10-Q04 | 标签区间至少保存什么？ | start、end、horizon 和成交规则。 |
| M10-Q05 | scaler 在哪里 fit？ | 每个 fold 的训练集。 |
| M10-Q06 | Brier score 衡量什么？ | 概率与二元结果的平方误差。 |
| M10-Q07 | log loss 为何惩罚自信错误？ | 错误概率趋近 0 时负对数发散。 |
| M10-Q08 | accuracy 的局限？ | 忽略概率、基准率和收益幅度。 |
| M10-Q09 | 消融能证明因果吗？ | 不能，只验证模型依赖与增量。 |
| M10-Q10 | 标签置换用途？ | 检查流程是否制造虚假分数。 |
| M10-Q11 | 树模型重要性为何有偏？ | 分裂机会、相关特征和尺度。 |
| M10-Q12 | 超参预算为何要一致？ | 避免更多搜索的模型占优。 |
| M10-Q13 | 多重检验记录什么？ | 所有特征、模型、窗口和阈值尝试。 |
| M10-Q14 | 概率校准是什么？ | 预测概率与经验发生率一致。 |
| M10-Q15 | IC 高是否可交易？ | 还需成本、换手、容量和执行。 |
| M10-Q16 | regime slice 为什么重要？ | 检查结构稳定和单制度依赖。 |
| M10-Q17 | point-in-time 特征要求？ | `available_at <= feature_time`。 |
| M10-Q18 | 特征仓库需版本什么？ | 公式、代码、数据、窗口和 hash。 |
| M10-Q19 | 合成实验支持什么？ | 支持切分、概率评分和消融路径。 |
| M10-Q20 | 何时暂停 ML 结论？ | 标签、切分、实验账本或经济映射失败。 |

## 答案索引（Answer Boundary） {#answer-boundary}

| ID | 答案边界 |
|---|---|
| M10-Q01 | 重叠持有期让训练目标包含测试期间信息。 |
| M10-Q02 | 删除 label interval 与测试重叠的训练行。 |
| M10-Q03 | 在测试边界留出依赖缓冲区。 |
| M10-Q04 | 起止时点、horizon、价格和退出规则。 |
| M10-Q05 | 仅训练子集。 |
| M10-Q06 | \(n^{-1}\sum(p-y)^2\)。 |
| M10-Q07 | \(-\log p_{true}\) 对接近零概率很大。 |
| M10-Q08 | 不反映置信度、收益大小或交易成本。 |
| M10-Q09 | 不能；只是预测增量证据。 |
| M10-Q10 | 构造无信号基准测试全流程偏差。 |
| M10-Q11 | 高基数/相关变量会扭曲 split importance。 |
| M10-Q12 | 搜索次数本身提供选择优势。 |
| M10-Q13 | 记录整个实验家族而非最终模型。 |
| M10-Q14 | 预测 0.7 的样本约 70% 发生。 |
| M10-Q15 | 不能；还需经济与执行闭环。 |
| M10-Q16 | 暴露制度依赖和结构变化。 |
| M10-Q17 | 特征发布时间不晚于样本决策时点。 |
| M10-Q18 | 定义、代码、源数据、窗口、版本和 hash。 |
| M10-Q19 | 验证 purge/embargo、概率指标和消融。 |
| M10-Q20 | 任一标签、切分、多重检验或经济闸门失败。 |

## 风险与后续建议（Risks & Next） {#risks}

- 单次固定切分不等于完整 walk-forward 交叉验证；下一项目需多 fold 与冻结验证/测试层。
- 手写 logistic 未与 scikit-learn、树模型或校准器对照。
- 下一 slice G18/P5 将实施无泄漏 Alpha 研究，冻结训练/验证/测试、完整实验账本、多重检验和失败策略。

## 参考文献（References） {#references}

1. [1] Peter Carr and Marcos López de Prado, “Determining Optimal Trading Rules without Backtesting,” 2014. [链接](https://arxiv.org/abs/1408.1159)
2. [2] Halbert White, “A Reality Check for Data Snooping,” *Econometrica*, 2000. [链接](https://doi.org/10.1111/1468-0262.00152)
3. [3] Glenn W. Brier, “Verification of Forecasts Expressed in Terms of Probability,” *Monthly Weather Review*, 1950. [链接](https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2)
