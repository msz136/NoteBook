# OPD（On-Policy Distillation）领域算法调研报告

## 问题（Question）

**原始问题：** 了解 OPD 领域算法，检索论文与研究报告，针对以下方法给出详细的学术性技术报告：Rethinking OPD、Veto、OPSD、Lightning OPD、Prefix OPD、Video-OPD / VLA-OPD / X-OPD，以及 OPD 中需要关注哪些指标、指标如何反映 OPD 的状态。

**问题重述：** 本报告系统梳理在策略蒸馏（On-Policy Distillation, OPD）的核心数学框架，以及当前主流方法的算法细节、理论动机、实验证据与适用场景。同时总结 OPD 训练中应监控的关键指标体系及其诊断意义。

## 背景与动机（Background & Motivation）

OPD 是介于监督微调（Supervised Fine-Tuning, SFT）与带可验证奖励的强化学习（Reinforcement Learning with Verifiable Rewards, RLVR）之间的后训练范式：

- **SFT**：监督密集但离策略（off-policy），存在暴露偏差（exposure bias）
- **RLVR**：在策略（on-policy）但奖励稀疏，信用分配困难
- **OPD**：同时具有"在策略状态分布"和"密集 token 级监督"

OPD 的核心思想是：学生模型在自己的生成轨迹上采样，教师模型在学生实际访问的状态上给出密集的词元级监督。这减少了 SFT/KD 的暴露偏差，同时提供比 RLVR 更连续、密集的训练信号。

## OPD 的基本数学形式

设 $D$ 是提示（prompt）分布，$x \sim D$ 是输入问题，$\pi_\theta$ 是参数为 $\theta$ 的学生策略，$\pi_T$ 是教师策略，$y = (y_1, \dots, y_T)$ 是学生从 $\pi_\theta(\cdot|x)$ 采样出的完整回答。第 $t$ 步状态记为 $s_t = (x, y_{<t})$。

**前向 KL 形式的 OPD 目标：**

$$\mathcal{L}_{\text{OPD}}(\theta) = \mathbb{E}_{x \sim D,\, y \sim \pi_\theta(\cdot|x)} \left[ \sum_{t=1}^{T} D_{\text{KL}}\left( \pi_T(\cdot|x, y_{<t}) \,\|\, \pi_\theta(\cdot|x, y_{<t}) \right) \right]$$

其中 KL 散度（Kullback-Leibler Divergence）定义为：

$$D_{\text{KL}}(p \| q) = \sum_{v \in \mathcal{V}} p(v) \log \frac{p(v)}{q(v)}$$

$\mathcal{V}$ 是词表，$v$ 是候选 token，$p(v)$ 是教师概率，$q(v)$ 是学生概率。

**关键点：** $y \sim \pi_\theta$ — 训练轨迹来自学生而非教师或静态数据集。

**KL 方向的选择：**

| 方向 | 倾向 | 优点 | 缺点 |
|------|------|------|------|
| 前向 KL $D_{\text{KL}}(\pi_T \| \pi_\theta)$ | 模式覆盖（mode-covering） | 信息完整 | 学生对教师高概率 token 赋近零概率时梯度爆炸 |
| 反向 KL $D_{\text{KL}}(\pi_\theta \| \pi_T)$ | 模式寻找（mode-seeking） | 稳定、果断 | 可能牺牲多样性，模���坍缩 |

---

## 方法详述

### 1. Rethinking OPD — 重新思考在策略蒸馏

**论文：** "Rethinking On-Policy Distillation of Large Language Models: Phenomenology, Mechanism, and Recipe" [1]

#### 核心结论

OPD 是否成功主要受两个条件控制：

1. 学生和教师应具有**相容的思维模式**（compatible thinking patterns）
2. 教师必须提供学生训练中未见过的**真实新增能力**（genuinely new capabilities），而非同族大模型的重复知识

论文用弱到强反向蒸馏（weak-to-strong reverse distillation）验证了同族 1.5B 与 7B 教师在学生视角下可能分布上不可区分。

#### 算法机制

OPD 的有效梯度定位到学生访问状态上的高概率重叠词元。设学生 top-k token 集合为 $S_k(s_t)$，教师 top-k token 集合为 $T_k(s_t)$，重叠集合为：

$$O_k(s_t) = S_k(s_t) \cap T_k(s_t)$$

**关键发现：**
- 成功 OPD 中，重叠比例（overlap ratio）随训练上升，熵差缩小
- 共享 top-k token 集中约 97%–99% 的概率质量
- 失败运行中这些指标基本停滞

Support ablation 实验表明：只在 overlap top-k 区域优化几乎可恢复完整 OPD 收益；只优化 non-overlap 区域则明显弱。OPD 的主要作用是在学生与教师都认为重要的高概率区域内重新分配概率质量。

#### 实用配方（Recipe）

- **离策略冷启动（off-policy cold start）：** 先用教师生成轨迹做 SFT 缩小思维模式差距
- **教师对齐提示选择（teacher-aligned prompt selection）：** 选择更接近教师训练分布的 prompt，混合 OOD prompt 防止熵坍缩

#### 有效性证据

- 成功运行中 overlap ratio 从约 72% 上升到 91%
- Overlap tokens 承载 97%–99% 概率质量
- 辅助指标（policy loss、gradient norm、extreme-advantage token probability differences）均显示成功运行有持续梯度

---

### 2. Veto — 否决式稳定在策略蒸馏

**论文：** "Stable On-Policy Distillation through Adaptive Target Reformulation" [2]

#### 问题动机

早期学生与强教师差距过大时的优化不稳定：前向 KL 在学生对教师偏好 token 赋近零概率时产生病态梯度（pathological gradients），反向 KL 可能过早模式坍缩。

#### 数学形式

Veto 在 logit 空间构造教师与学生之间的中间目标分布（intermediate target distribution）。设教师 logits 为 $z_T(v)$，学生 logits 为 $z_S(v)$，Veto 构造带参数 $\beta$ 的中间分布：

$$Q_\beta(v) \propto \exp(z_T(v)) \cdot \exp(\beta \cdot z_S(v))$$

其中 $\beta \geq 0$ 控制学生当前置信度对目标分布的"否决权"：

- 若学生对某 token 极不确定（$\pi_\theta(v|s_t)$ 很小），$Q_\beta(v)$ 不会像纯教师目标那样强行给出巨大梯度
- 若 $\beta \to 0$，目标退回更接近教师分布

$\beta$ 的双重解释：
- **自适应梯度否决器（Adaptive Gradient Veto）：** 抑制低置信 token 的有害梯度
- **果断性旋钮（Decisiveness Knob）：** 调节性能与输出多样性

#### 算法流程

1. 采样 prompt，学生 on-policy 生成轨迹
2. 对每个 token 取教师与学生 logits
3. 用 $\beta$ 构造重构目标（reformulated target）
4. 前向 KL → Veto 目标抑制梯度爆炸；反向 KL → $\beta$ 调节 mode-seeking 强度
5. 训练中可让 $\beta$ 线性衰减到 0（早期稳定，后期接近强教师）

#### 有效性证据

| 基准 | Veto | On-policy KD |
|------|------|-------------|
| GSM8K accuracy | 39.9 | 35.1 |
| HumanEval pass@1 | 29.0 | 22.9 |
| DialogSum win-rate | 56.5 | 54.3 |

---

### 3. OPSD — 在策略自蒸馏

**论文：** "Self-Distilled Reasoner: On-Policy Self-Distillation for Large Language Models" [3]

#### 核心思想

不使用外部大教师，让同一个模型在不同上下文下扮演教师与学生：

- **学生分布：** $\pi_\theta^S(\cdot|x, y_{<t})$ — 只看问题 $x$
- **教师分布：** $\pi_\theta^T(\cdot|x, c, y_{<t})$ — 额外看到特权信息（privileged information）$c$

二者**共享同一组参数 $\theta$**，但条件上下文不同。特权信息 $c$ 可以是已验证推理轨迹或标准解。

#### 训练流程

1. 学生采样 $y \sim \pi_\theta^S(\cdot|x)$
2. 教师在同一个学生前缀上给出 token 分布
3. 最小化逐 token 散度，梯度只回传到学生 logits

#### 四个关键性质

同时满足：在策略数据、密集学习信号、低采样成本、无外部教师。

#### 有效性证据

- 多个数学推理基准上优于 RLVR 与 off-policy distillation
- 相对 GRPO 约 4–8× 的 token 效率

#### 注意事项

后续研究 "The Many Faces of OPD" 指出：OPSD 在实例特异特权信息缺失于测试时的任务上可能失败；当特权信息表示共享潜在规则（如系统提示或偏好规则）时更有效。

---

### 4. Lightning OPD — 闪电式离线在策略蒸馏

**论文：** "Lightning OPD: Efficient Post-Training for Large Reasoning Models with Offline On-Policy Distillation" [4]

#### 问题动机

标准 OPD 需要训练时持续运行在线教师服务（live teacher server）计算教师 log-probability，基础设施成本高。

#### 核心发现：教师一致性（Teacher Consistency）

SFT 阶段生成训练轨迹的教师，必须与 OPD 阶段提供 token 级分布的教师**相同**。若不一致，会引入梯度偏差（gradient bias），离线版本受影响更严重。

#### 两阶段算法

**阶段一：** 选定教师 $T$，用它生成 SFT 轨迹并把 base model 微调到参考策略 $\pi_{\text{ref}}$

**阶段二：** 从 $\pi_{\text{ref}}$ 采样固定 rollouts，用同一个教师 $T$ 预计算每个 token 的 $\log \pi_T(y_t|s_t)$；训练阶段只读取缓存的教师 log-probability，不再部署教师服务

#### 理论保证

- 教师一致性成立时，Lightning OPD 与标准 OPD 共享相同不动点（fixed point）
- 梯度差异有界
- 离线目标带有隐式正则化（implicit regularization）抑制策略漂移

#### 有效性证据

- Qwen3-8B-Base：30 GPU 小时内达到 AIME 2024 的 69.9%，训练效率约为标准 OPD 的 4 倍
- 单个 8×H100 节点：Qwen3-30B-A3B 达到 AIME 2024 的 71.0%、LiveCodeBench v5 的 60.8%
- 教师一致性消融：8B 规模下，从 Qwen3-32B SFT 教师错配到 QwQ-32B OPD 教师会下降约 6.8 个点

---

### 5. Prefix OPD — 前缀在策略蒸馏

**论文：** "Fast and Effective On-policy Distillation from Reasoning Prefixes" [5]

#### 核心观察

长推理回答中，OPD 的有效训练信号往往集中在前缀部分；一个短教师前缀有时足以把学生带入正确推理路径。

#### 数学形式

设完整回答长度为 $T$，Prefix OPD 选择前缀长度 $L \ll T$：

$$\mathcal{L}_{\text{prefix}}(\theta) = \mathbb{E}_{x,\, y \sim \pi_\theta} \left[ \sum_{t=1}^{L} D\left( \pi_T(\cdot|x, y_{<t}),\, \pi_\theta(\cdot|x, y_{<t}) \right) \right]$$

其中 $D$ 可以是前向 KL、反向 KL 或 token-level reward 形式。

#### 工程收益

1. 不生成后缀 → 减少采样成本（sampling cost）
2. 不对后缀调用教师 → 减少教师推理成本（teacher inference cost）

#### 前缀长度调度（Prefix Scheduling）

训练早期用短 $L$，后期逐步增加。先学习"走上正确推理轨道"的早期策略，再逐渐覆盖更长的推理结构。

#### 有效性证据

- 在 AI-for-Math 和 OOD 基准上接近完整 OPD 性能
- 训练 FLOPs 降低 **2×–47×**

---

### 6. Video-OPD — 视频在策略蒸��

**论文：** "Video-OPD: Efficient Post-Training of Multimodal Large Language Models for Temporal Video Grounding via On-Policy Distillation" [6]

#### 任务与动机

时序视频定位（Temporal Video Grounding, TVG）：给定视频与自然语言查询，输出相关时间片段。GRPO 在该任务中奖励稀疏且多 rollout 重复编码长视频上下文，计算成本高。

#### 方法

学生策略直接生成定位轨迹，固定前沿教师（frontier teacher）只对学生轨迹提供 token 级反向 KL 监督，将回合级稀疏奖励转为逐步密集信号。

#### TVDF（Teacher-Validated Disagreement Focusing）

用 ground-truth 时序标注做验证信号（非直接监督目标）：
1. 用标注验证教师在某个 video-query 对上是否可靠
2. 优先训练教师-学生分歧大的轨迹（分歧由聚合 reverse KL 衡量）

样本既"教师可靠"又"对学生信息量大"。

#### 有效性证据

- Charades-TimeLens、ActivityNet-TimeLens、QVHighlights-TimeLens 上平均提升超过 17%（GRPO 约 12%）
- 在 TempCompass、MVBench、Video-MME 等更广泛视频理解基准上表现出泛化能力
- Qwen3-VL-8B 部分指标从 GRPO 的 72.7/44.4/27.6 提升到 73.1/45.8/32.4

---

### 7. VLA-OPD — 视觉-语言-动作在策略蒸馏

**论文：** "VLA-OPD: Bridging Offline SFT and Online RL for Vision-Language-Action Models via On-Policy Distillation" [7]

#### 问题动机

VLA（Vision-Language-Action）模型用于机器人操作：
- Offline SFT → 分布偏移 + 灾难性遗忘
- Online RL → 奖励稀疏、样本效率低

#### 为何选择反向 KL

机器人动作空间中，教师在 OOD 状态可能有高认知不确定性（epistemic uncertainty）：

| 目标 | 问题 |
|------|------|
| 前向 KL | 强迫学生覆盖教师长尾不确定性 → 熵爆炸 |
| Hard-CE | 只追教师 argmax → 过早熵坍缩 |
| **反向 KL** | 有界模式寻找，过滤教师长尾不确定性，保留主模式内动作多样性 |

#### 算法流程

1. 从 1-trajectory SFT 初始化学生
2. 每个 prompt 采样一组学生轨迹
3. 对每个时间步查询学生和教师 logits
4. 计算负反向 KL 作为内在奖励（intrinsic reward）
5. 用基于组的策略梯度（group-based policy gradient）更新学生

#### 有效性证据

- LIBERO-Object：约 10 步内达到 >90% 成功率
- LIBERO-Long：约 50 步接近 80% 成功率（baseline GRPO 约需 150 步，约 3× 加速）
- 与 GRPO 结合可突破单纯蒸馏上限（Object >95%、Long >90%）
- 在策略对齐能保留泛化能力（seen-unseen trade-off）

---

### 8. X-OPD — 跨模态在策略蒸馏

**论文：** "X-OPD: Cross-Modal On-Policy Distillation for Capability Alignment in Speech LLMs" [8]

#### 问题动机

端到端语音模型延迟低、能保留副语言信息，但复杂指令、逻辑推理、知识问答常弱于文本 LLM。标准 SFT 与 RL 不能充分关闭模态差距（modality gap）。

#### 方法设计

1. 构造语音-文本平行提示（parallel speech-text prompts），要求语义不变
2. 学生语音模型在语音与文本模态上进行 on-policy rollouts
3. 文本教师在同步文本输入上提供 token 级评分
4. 引入**模态内优势**（in-modal advantage）稳定文本域能力
5. 用**跨模态优势**（cross-modal advantage）把文本教师逻辑迁移到语音条件输出
6. 最终损失 = 模态内损失 + 跨模态损失的加权和

#### 鲁棒多采样轨迹（Robust Multi-Sampling Rollout）

每个输入采样多条候选轨迹，通过边际化多个路径的梯度降低单样本更新方差。语音输入本身引入声学扰动，单次 rollout 随机性更高。

#### 有效性证据

在 Qwen3-Omni-A3B-Instruct 上：

| 方法 | Avg. Drop (指标1/指标2) |
|------|------------------------|
| 基础模型 | 11.29% / 5.51% |
| SFT | 22.76% / 17.49% |
| Offline KD | 19.62% / 15.02% |
| GKD Forward KL | 20.23% / 15.81% |
| **X-OPD** | **3.43% / 0.97%** |

X-OPD 用约 27k 样本实现较强的样本效率与能力保持。

---

## OPD 关键指标体系

### 第一类：任务效果指标

| 领域 | 指标 |
|------|------|
| 数学推理 | accuracy、pass@k、avg@k |
| 代码 | HumanEval pass@1/pass@10、LiveCodeBench 通过率 |
| 机器人 VLA | success rate（任务成功率） |
| 视频 TVG | temporal IoU、mIoU、Recall@IoU |
| 语音 X-OPD | benchmark score、modality drop |

**注意：** 蒸馏可能产生指标外损失（off-metric losses），包括校准退化、推理轨迹质量侵蚀和分布收窄。

### 第二类：教师-学生分布对齐指标

- Forward KL / Reverse KL
- Teacher-student log-prob gap
- Token advantage
- **Top-k overlap ratio** — 成功 OPD 中从约 72% 上升到 91%
- **Overlap mass** — 成功 OPD 中共享 top-k token 承载 97%–99% 概率质量
- Entropy gap

**诊断：** KL 稳定下降 + overlap ratio 上升 + 熵差缩小 → 有效对齐；overlap 停滞 + 熵长期不匹配 → 可能失败。

### 第三类：优化稳定性指标

- Gradient norm — 持续为零说明教师信号不可用；尖峰频繁说明前向 KL 爆炸
- Policy loss
- Advantage distribution — 被重复 token 主导可能进入长度膨胀
- Clip fraction
- Learning rate sensitivity
- Loss spike

### 第四类：生成退化指标

来自 "Demystifying OPD" 的发现：

- **突发长度膨胀（abrupt length inflation）**
- **截断坍缩（truncation collapse）**
- **重复饱和（repetition saturation）**

应监控：average length、EOS rate、truncation rate、repetition rate、compression-based repetition。

**诊断：** 截断率突然接近 1 + 重复率飙升 + 验证准确率下降 → 学生在"利用"教师 likelihood 信号，进入自强化重复循环。

### 第五类：多样性与校准指标

- **多样性：** entropy、distinct-n、self-BLEU、mode coverage
- **校准：** ECE（Expected Calibration Error）、Brier score、confidence-accuracy curve

前向 KL 过强 → 熵过高、策略不果断；反向 KL / Hard-CE 过强 → 熵坍缩。

### 第六类：效率指标

- Teacher queries（教师调用次数）
- Teacher serving GPU hours
- Training FLOPs
- Generated tokens per update
- Wall-clock time
- Convergence steps

### 第七类：泛化、遗忘与模态保持指标

- LLM 推理：in-domain 与 OOD 同时表现
- VLA：seen/unseen task 成功率（评估灾难性遗忘）
- X-OPD：语音与文本模态性能差距 + 原有声学能力保持

---

## 方法对比与选择建议

| 场景 | 推荐方法 | 理由 |
|------|----------|------|
| 理解 OPD 是否会成功 | Rethinking OPD | 给出机制解释：思维模式相容 + 教师有新能力 + overlap 动态 |
| 训练早期不稳定 | Veto | 目标函数层面重构，抑制病态梯度 |
| 教师部署成本是瓶颈 | Lightning OPD | 预计算教师 log-prob，去掉在线教师服务（需保证教师一致性） |
| 长推理成本过高 | Prefix OPD | 前缀截断，FLOPs 降低 2×–47× |
| 无外部教师/自举 | OPSD | 同一模型自蒸馏（需确认特权信息是共享规则而非实例答案） |
| 视频时序定位 | Video-OPD | 密集信号 + TVDF 聚焦高信息量样本 |
| 机器人 VLA | VLA-OPD | 反向 KL 内在奖励 + 环境交互保持在策略 |
| 语音跨模态对齐 | X-OPD | 模态内 + 跨模态优势联合优化 |

---

## 参考文献（References）

[1] "Rethinking On-Policy Distillation of Large Language Models: Phenomenology, Mechanism, and Recipe", 2025.

[2] "Stable On-Policy Distillation through Adaptive Target Reformulation (Veto)", 2025.

[3] "Self-Distilled Reasoner: On-Policy Self-Distillation for Large Language Models", 2025.

[4] "Lightning OPD: Efficient Post-Training for Large Reasoning Models with Offline On-Policy Distillation", 2025.

[5] "Fast and Effective On-policy Distillation from Reasoning Prefixes", 2025.

[6] "Video-OPD: Efficient Post-Training of Multimodal Large Language Models for Temporal Video Grounding via On-Policy Distillation", 2025.

[7] "VLA-OPD: Bridging Offline SFT and Online RL for Vision-Language-Action Models via On-Policy Distillation", 2025.

[8] "X-OPD: Cross-Modal On-Policy Distillation for Capability Alignment in Speech LLMs", 2025.

[9] "The Many Faces of OPD" (OPD 的多面性), 2026 综述.

[10] "Demystifying OPD" (解构 OPD), 2025/2026.

[11] verl 文档 — OPD 模块说明. [GitHub: volcengine/verl](https://github.com/volcengine/verl)
