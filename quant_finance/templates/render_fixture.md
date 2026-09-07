---
title: ARIS 学术渲染基线测试
subtitle: 覆盖公式、表格、代码、锚点和响应式布局的最小样例
date: 2026-07-22
evidence_cutoff: 2026-07-22
topic: Quant Finance · Render Fixture
---

# ARIS 学术渲染基线测试

## 问题（Question） {#question}

这份 fixture 只验证渲染契约：Markdown 是唯一内容源；HTML 与审查记录必须同步 SHA-256。返回[数学公式](#formula-safety)，或查看[资料库入口](../README.md)。

## 公式安全（Math Safety） {#formula-safety}

行内收益率使用 $r_t = (P_t-P_{t-1})/P_{t-1}$，Markdown 强调仍应保持为**独立语义**，LaTeX 下划线不能变成 `<em>`。

令 \(\hat{\bar a}_{b,h,j}\) 表示样本 (b)、预测步 (h)、维度 (j) 的预测量，展示公式为：

\[
\ell\!\left(\hat{\bar a}_{b,h,j},\bar a_{b,h,j}\right)
= \left(\hat{\bar a}_{b,h,j}-\bar a_{b,h,j}\right)^2
\]

<div class="note"><strong>变量、直觉与实现映射：</strong>损失逐元素比较预测与标签；代码中对应形状为 <code>[batch, horizon, feature]</code> 的张量，然后按有效 mask 聚合。本式仅用于验证公式保护，不支持任何投资收益主张。</div>

## 表格与横向溢出 {#table-check}

| 检查项 | 预期行为 | 失败信号 |
|---|---|---|
| 表格 | 深蓝表头、纸色斑马纹、窄屏内部滚动 | 页面整体出现横向滚动 |
| 代码 | atom-one-light 兼容配色、蓝色左规则 | 代码撑破正文列 |
| 公式 | `.formula` 学术表面、内部滚动 | LaTeX 被 Markdown 转成强调标签 |

## 代码与 MathJax 跳过规则 {#code-check}

```python
def simple_return(price_t, price_tm1):
    # 代码里的 $not_math$ 和 latex_{index} 不应交给 MathJax。
    return (price_t - price_tm1) / price_tm1
```

## 方法对比与选择建议 {#comparison}

本基线选择“规范 CSS + 确定性 Python 渲染 + 独立审查器”。它比手工编辑生成 HTML 更容易保持源文件、SHA 和审查状态同步。

## 参考文献（References） {#references}

1. [MathJax 3 Documentation](https://docs.mathjax.org/)。
2. [markdown-it-py Documentation](https://markdown-it-py.readthedocs.io/)。
