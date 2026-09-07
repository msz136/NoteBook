# 计量金融与量化资料库

本目录是计量金融（Financial Econometrics）与量化研究（Quantitative Research）的独立资料库。后续相关教材笔记、技术报告、数据说明、实验、代码和审查记录均放在这里，不再写入仓库主目录。

快速入口：打开 [index.html](index.html)；它把所有报告集中到浅层导航中，并且每个报告末尾都提供下一章节相对链接。

## 当前状态

- 阶段：G00–G24 完成；M00–M12、P0–P7 与 Capstone 执行材料已生成（本报告 HTML 与总 PDF 已完成视觉复核）。
- 总计划：见 [PLAN.md](PLAN.md)。
- 已核验来源：见 [sources/source_registry.md](sources/source_registry.md)。
- 渲染工具：见 [tools/README.md](tools/README.md)。
- 学术模板与 fixture：见 [templates/README.md](templates/README.md)。
- 经典交易策略模型报告规划：见 [strategy_models_report_plan.md](strategy_models_report_plan.md)。
- 经典交易策略模型最终报告：[HTML](classic_trading_strategy_models_report.html)；[总 PDF](../output/pdf/classic_trading_strategy_models_report.pdf)。
- 当前状态：资料库 G03–G24 slices 已逐个完成；Capstone 最终状态为 `partial_reproduction`，未运行项已登记。

## 模块列表

- [M00：领域导航、问题分类与能力诊断](modules/00_orientation_and_diagnostic_notes.html)（[Markdown 源](modules/00_orientation_and_diagnostic_notes.md)｜[审查记录](reviews/00_orientation_and_diagnostic_notes.review.json)）
- [M01：数学、概率、统计与优化基础](modules/01_mathematical_foundations_notes.html)（[Markdown 源](modules/01_mathematical_foundations_notes.md)｜[审查记录](reviews/01_mathematical_foundations_notes.review.json)）
- [M02：金融数据契约、收益口径与 Point-in-Time](modules/02_financial_data_contract_notes.html)（[Markdown 源](modules/02_financial_data_contract_notes.md)｜[审查记录](reviews/02_financial_data_contract_notes.review.json)）
- [M03：OLS、MLE、GMM、稳健推断与 Bootstrap](modules/03_core_econometrics_notes.html)（[Markdown 源](modules/03_core_econometrics_notes.md)｜[审查记录](reviews/03_core_econometrics_notes.review.json)）
- [M04：ARIMA、VAR、状态空间与波动率模型](modules/04_financial_time_series_notes.html)（[Markdown 源](modules/04_financial_time_series_notes.md)｜[审查记录](reviews/04_financial_time_series_notes.review.json)）
- [M05：FE/RE、IV、DiD、RDD 与合成控制](modules/05_panel_and_causal_identification_notes.html)（[Markdown 源](modules/05_panel_and_causal_identification_notes.md)｜[审查记录](reviews/05_panel_and_causal_identification_notes.review.json)）
- [M06：CAPM、SDF、因子模型与 Fama–MacBeth](modules/06_asset_pricing_notes.html)（[Markdown 源](modules/06_asset_pricing_notes.md)｜[审查记录](reviews/06_asset_pricing_notes.review.json)）
- [M07：固定收益、衍生品与随机过程](modules/07_fixed_income_derivatives_notes.html)（[Markdown 源](modules/07_fixed_income_derivatives_notes.md)｜[审查记录](reviews/07_fixed_income_derivatives_notes.review.json)）
- [M08：组合优化、Black–Litterman 与 VaR/ES](modules/08_portfolio_and_risk_notes.html)（[Markdown 源](modules/08_portfolio_and_risk_notes.md)｜[审查记录](reviews/08_portfolio_and_risk_notes.review.json)）
- [M09：市场微观结构、执行与容量](modules/09_market_microstructure_execution_notes.html)（[Markdown 源](modules/09_market_microstructure_execution_notes.md)｜[审查记录](reviews/09_market_microstructure_execution_notes.review.json)）
- [M10：因子研究、时序验证与金融机器学习](modules/10_factor_research_financial_ml_notes.html)（[Markdown 源](modules/10_factor_research_financial_ml_notes.md)｜[审查记录](reviews/10_factor_research_financial_ml_notes.review.json)）
- [M11：回测统计、引擎语义与策略衰减](modules/11_backtest_statistics_decay_notes.html)（[Markdown 源](modules/11_backtest_statistics_decay_notes.md)｜[审查记录](reviews/11_backtest_statistics_decay_notes.review.json)）
- [M12：研究复现与模型治理](modules/12_reproducibility_model_governance_notes.html)（[Markdown 源](modules/12_reproducibility_model_governance_notes.md)｜[审查记录](reviews/12_reproducibility_model_governance_notes.review.json)）

## Capstone

- [Fama–French (1993) 复现协议](projects/capstone_fama_french_1993/capstone_protocol.html)（[协议 JSON](projects/capstone_fama_french_1993/capstone_protocol.json)｜[项目 README](projects/capstone_fama_french_1993/README.md)｜[审查记录](reviews/capstone_fama_french_1993_protocol.review.json)）
- [Fama–French (1993) 执行与答辩材料](projects/capstone_fama_french_1993/capstone_execution_report.html)（[执行结果](projects/capstone_fama_french_1993/capstone_execution_results.json)｜[执行脚本](projects/capstone_fama_french_1993/execute_capstone.py)｜[审查记录](reviews/capstone_fama_french_1993_execution.review.json)）

## 项目列表

- [P0：LLN、CLT、区间覆盖率与 Bootstrap 统计模拟](projects/p0_statistical_simulation/p0_statistical_simulation_report.html)（[项目 README](projects/p0_statistical_simulation/README.md)｜[机器结果](projects/p0_statistical_simulation/results/summary.json)｜[审查记录](reviews/p0_statistical_simulation_report.review.json)）
- [P1：FRED/ALFRED Vintage 泄漏对照实验](projects/p1_macro_vintage/p1_macro_vintage_report.html)（[项目 README](projects/p1_macro_vintage/README.md)｜[机器结果](projects/p1_macro_vintage/p1_macro_vintage_results.json)｜[审查记录](reviews/p1_macro_vintage_report.review.json)）
- [P2：EWMA/GARCH 波动率滚动预测实验](projects/p2_volatility_forecast/p2_volatility_forecast_report.html)（[项目 README](projects/p2_volatility_forecast/README.md)｜[机器结果](projects/p2_volatility_forecast/p2_volatility_forecast_results.json)｜[审查记录](reviews/p2_volatility_forecast_report.review.json)）
- [P3：French 三因子与 25 个 Size–B/M 组合复现](projects/p3_factor_pricing/p3_factor_pricing_report.html)（[项目 README](projects/p3_factor_pricing/README.md)｜[机器结果](projects/p3_factor_pricing/p3_factor_pricing_results.json)｜[审查记录](reviews/p3_factor_pricing_report.review.json)）
- [P4：估计误差、换手、成本与压力敏感性实验](projects/p4_portfolio_risk/p4_portfolio_risk_report.html)（[项目 README](projects/p4_portfolio_risk/README.md)｜[机器结果](projects/p4_portfolio_risk/p4_portfolio_risk_results.json)｜[审查记录](reviews/p4_portfolio_risk_report.review.json)）
- [P5：冻结切分、实验账本与无泄漏 Alpha 研究](projects/p5_leakage_free_alpha/p5_leakage_free_alpha_report.html)（[项目 README](projects/p5_leakage_free_alpha/README.md)｜[机器结果](projects/p5_leakage_free_alpha/p5_leakage_free_alpha_results.json)｜[审查记录](reviews/p5_leakage_free_alpha_report.review.json)）
- [P6：LEAN 事件驱动订单生命周期重建](projects/p6_lean_event_backtest/p6_lean_event_backtest_report.html)（[项目 README](projects/p6_lean_event_backtest/README.md)｜[机器结果](projects/p6_lean_event_backtest/p6_lean_event_results.json)｜[审查记录](reviews/p6_lean_event_backtest_report.review.json)）
- [P7：数据—特征—训练—回测—报告生产管线](projects/p7_research_pipeline/p7_research_pipeline_report.html)（[项目 README](projects/p7_research_pipeline/README.md)｜[Manifest](projects/p7_research_pipeline/pipeline_manifest.json)｜[审查记录](reviews/p7_research_pipeline_report.review.json)）

## 目录契约

```text
quant_finance/
├── PLAN.md                 # 可续建总计划与里程碑状态
├── sources/                # 来源登记、版本、访问条件和证据边界
├── modules/                # 课程模块：Markdown 源 + HTML 学习页
├── projects/               # 可复现实验、研究项目与回测项目
├── reviews/                # *.review.json 审查记录
├── templates/              # 学术 HTML 模板与渲染约定
├── tools/                  # 渲染、链接、公式、SHA 与数据审计工具
└── data/                   # 仅保存数据说明/小样本；大数据不进入 Git
```

## 生成规则

1. 每个模块先写 `*.md`，再生成同名 `*.html`；Markdown 是唯一内容源。
2. HTML 写入 Markdown 的完整 SHA-256；同名 `*.review.json` 同步记录该 SHA。
3. 每次只完成一个模块或一个紧密耦合的小项目，经过来源、数学、代码、链接与视觉检查后再进入下一项。
4. 数据必须登记来源、授权、获取日期、频率、时区、交易日历、复权、幸存者偏差与点时（point-in-time）属性。
5. 教学代码与研究代码分离；任何收益结论必须同时报告成本、滑点、容量、样本外和多重检验边界。

## 关于投资结论

本资料库用于教育与研究，不构成投资建议。示例回测不能等同于可实现的未来收益。
