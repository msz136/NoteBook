# P0 统计模拟实验

冻结协议见 `config.json`。运行：

```powershell
python quant_finance/projects/p0_statistical_simulation/run_experiments.py
python quant_finance/projects/p0_statistical_simulation/validate_results.py
python quant_finance/projects/p0_statistical_simulation/test_experiments.py -v
```

输出：

- `results/summary.json`：协议、环境、代码/config SHA 与全部数值结果；
- `results/summary.svg`：四面板结果图；
- `results/validation.json`：确定性结果契约检查；
- `p0_statistical_simulation_report.md/.html`：实验报告的规范源与渲染产物。

报告入口：[P0 统计模拟实验报告](p0_statistical_simulation_report.html)。

修改协议必须更改 `protocol_version`，不得用同一版本号覆盖不同实验设计。
