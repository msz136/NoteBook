# 渲染与审查工具

```powershell
python quant_finance/tools/render_academic.py `
  quant_finance/modules/00_orientation_and_diagnostic_notes.md

python quant_finance/tools/validate_artifact.py `
  quant_finance/modules/00_orientation_and_diagnostic_notes.md `
  quant_finance/modules/00_orientation_and_diagnostic_notes.html `
  --review quant_finance/reviews/00_orientation_and_diagnostic_notes.review.json `
  --required-sections question,background,concepts,methods,math,pipeline,comparison,risks,references `
  --question-prefix M00-D --question-count 28
```

视觉 QA 完成后，用 `--visual-status PASS --visual-evidence "..."` 重跑审查器。审查器会同步源 SHA、标题层级、MathJax 配置、公式安全、模板标记、锚点和本地链接。

运行确定性与失配负向测试：

```powershell
python quant_finance/tools/test_render_pipeline.py -v
```

报告阅读导航由 [../navigation.json](../navigation.json) 管理。打开 [../index.html](../index.html) 可从浅层入口访问全部报告；渲染器会在每个登记报告末尾生成相对路径的 `下一章节` 链接。新增报告时先把 Markdown/HTML 路径和标题加入 navigation manifest，再重渲染并检查链接。
