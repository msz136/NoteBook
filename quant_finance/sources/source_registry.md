# 首批来源登记

核验日期：2026-07-22。这里登记的是规划阶段已直接查看的入口，不代表完整书目。具体模块开始前需冻结版本、章节和可支持的主张。

| 来源 | 类型 | 当前可支持内容 | 不能据此推断 | 状态 |
|---|---|---|---|---|
| [MIT OCW 14.382 Econometrics](https://ocw.mit.edu/courses/14-382-econometrics-spring-2017/) | primary/course | 现代计量的模型、识别、估计、推断和真实数据实践课程骨架 | 不自动覆盖金融市场、资产定价和工程部署 | checked |
| [QuantEcon: Intermediate Quantitative Economics with Python](https://python.quantecon.org/) | primary/course | Python 数值经济学与可执行讲义 | 不是完整金融计量或实盘课程 | checked |
| [Bruce E. Hansen, Econometrics](https://www.ssc.wisc.edu/~bhansen/econometrics/) | primary/author | 研究生计量教材、配套数据和程序入口 | 教材正文访问需按出版社/合法渠道；不代表量化交易完整栈 | checked |
| [statsmodels 0.14.6](https://www.statsmodels.org/stable/index.html) | official-code | 统计模型、检验、数据探索和 OLS 等实现 | 单包不覆盖完整面板、回测和实盘 | checked |
| [linearmodels 7.0](https://bashtage.github.io/linearmodels/) | official-code | 面板、IV/2SLS、GMM、SUR、Fama–MacBeth 与线性因子模型 | 不等于因果识别假设已经成立 | checked |
| [arch 8.0.0](https://bashtage.github.io/arch/) | official-code | 单变量波动率、Bootstrap、单位根、协整和长程协方差 | 不覆盖全部多变量波动率或交易系统 | checked |
| [FRED API](https://fred.stlouisfed.org/docs/api/fred/) | primary/data | 圣路易斯联储 FRED 官方 API 入口 | 普通 FRED 序列不自动具备实时 vintage 安全性 | checked |
| [Kenneth R. French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) | primary/data | 公布的因子与投资组合数据、细节和历史档案入口 | 不能替代底层 CRSP/Compustat 点时数据审计 | checked |
| [Microsoft Qlib](https://github.com/microsoft/qlib) | official-code | 面向量化研究的 AI/ML 工作流、数据准备与研究管线 | README 示例不构成收益或生产可靠性证明 | checked |
| [QuantConnect LEAN](https://github.com/QuantConnect/Lean) | official-code | Python/C# 事件驱动回测与实盘引擎、模块化接口 | 回测引擎本身不能消除数据偏差和模型风险 | checked |
| [WRDS](https://wrds-www.wharton.upenn.edu/) | primary/data | 计划中的专业学术数据入口 | 当前浏览器未成功核验页面内容；订阅、数据集和许可待确认 | warning |
| [Princeton BCF Requirements and Core Courses](https://bcf.princeton.edu/academic-programs/master-in-finance/requirements-core-courses/) | primary/course | 资产定价、金融数据统计、会计、随机微积分、衍生品和金融计量的公开课程骨架 | 不是唯一的量化岗位标准，也不证明某种学习顺序适合所有人 | checked |
| [Wilson et al., Good Enough Practices in Scientific Computing](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005510) | primary/paper | 数据管理、软件、协作、项目组织、版本跟踪和可复现研究实践 | 不专门解决金融数据许可、点时数据或交易执行 | checked |
| [Carr & López de Prado, Determining Optimal Trading Rules without Backtesting](https://arxiv.org/abs/1408.1159) | primary/paper | 反复用历史模拟校准交易规则会引入回测过拟合风险这一边界 | 不支持“禁止一切回测”，也不证明任意策略在样本外有效 | checked |
| [MIT OCW 18.06 Linear Algebra](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/) | primary/course | 方程组、向量空间、行列式、特征值、相似与正定矩阵的课程骨架 | 不覆盖金融概率、统计推断或数值优化全栈 | checked |
| [MIT OCW 18.05 Introduction to Probability and Statistics](https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/) | primary/course | 组合、随机变量、分布、Bayes、检验、置信区间和线性回归入门 | 初等课程不能替代后续渐近计量、时间依赖与金融尾部风险 | checked |
| [Bruce E. Hansen, Probability and Statistics for Economists](https://www.ssc.wisc.edu/~bhansen/probability/) | primary/author | 面向经济学家的一年制博士计量序列第一卷及配套代码入口 | 正文需合法购买/图书馆渠道；不是凸优化或数值线性代数专著 | checked |
| [Boyd & Vandenberghe, Convex Optimization](https://web.stanford.edu/~boyd/cvxbook/) | primary/book | 凸集合、凸函数、对偶、最优性条件、算法与公开示例材料 | 凸方法不保证非凸金融问题的全局最优，也不解决输入估计误差 | checked |
| [NumPy `linalg.lstsq`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html) | official-code | 用最小二乘求解欠定、适定或超定线性系统及秩截断语义 | API 正确使用不自动保证模型设定、因果解释或数据质量 | checked |
| [Efron, Bootstrap Methods: Another Look at the Jackknife](https://projecteuclid.org/journals/annals-of-statistics/volume-7/issue-1/Bootstrap-Methods-Another-Look-at-the-Jackknife/10.1214/aos/1176344552.short) | primary/paper | Bootstrap 的经典原始方法、与 jackknife 的关系及示例边界 | 不证明 percentile interval 对所有统计量、依赖数据或小样本都有标称覆盖率 | checked |
| [NumPy Random Generator](https://numpy.org/doc/stable/reference/random/generator.html) | official-code | `default_rng(seed)`、Generator/BitGenerator 和 PCG64 默认接口语义 | 固定 seed 不保证跨任意未来版本或不同算法的逐位一致性 | checked |
| [ALFRED](https://alfred.stlouisfed.org/alfred-graph) | primary/data | 计划用于讨论实时 vintage/修订数据 | 2026-07-22 浏览器访问失败；本切片不直接下载或声称已验证其页面字段 | warning |
| [SEC EDGAR API Documentation](https://www.sec.gov/edgar/sec-api-documentation) | primary/data | 计划用于公司申报与 XBRL 数据边界 | 当前浏览器访问被安全策略阻断；本切片不据此写具体 API 字段承诺 | warning |

## 下一批来源冻结任务

## 经典交易策略报告：第 1 章来源冻结（2026-07-27）

| 来源 | 类型 | 修订/获取日期 | 支持的具体主张 | 不能据此推断 | 状态 |
|---|---|---|---|---|---|
| [Markowitz (1952), Portfolio Selection](https://doi.org/10.2307/1907413) | primary/paper | 1952 | 均值—方差组合、协方差与分散化的理论起点 | 不支持任意股票+黄金权重的未来表现 | checked |
| [Sharpe (1964), Capital Asset Prices](https://doi.org/10.2307/2977928) | primary/paper | 1964 | 风险—收益与基准调整的 CAPM 理论背景 | 不等于择时策略，也不消除估计误差 | checked |
| [Baur & Lucey (2010), Is Gold a Hedge or a Safe Haven?](https://doi.org/10.1016/j.frl.2010.03.001) | primary/paper | 2010 | 区分正常期 hedge 与极端下跌期 safe haven 的条件定义 | 不支持黄金在所有危机、所有窗口都避险 | checked |
| [Erb & Harvey (2013), The Golden Dilemma](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2078535) | primary/paper | 2013 | 黄金长期回报、通胀、美元和仓位讨论 | 不支持把历史样本直接外推到当前 ETF 或人民币投资者 | checked |
| [Yahoo Finance chart API](https://finance.yahoo.com/) SPY/GLD adjusted close | secondary_data_proxy/local-evidence | 2026-07-27；月频；排除 2026-07 未完成月 | 生成本章 ETF 代理的收益、CAGR、波动、零利率 Sharpe 与 MDD 示例 | 不支持无摩擦资产类长期收益、生产交易或未来预期收益；数据许可与供应商调整细节待进一步核验 | warning |

## 经典交易策略报告：第 2 章来源冻结（2026-07-27）

| 来源 | 类型 | 修订/获取日期 | 支持的具体主张 | 不能据此推断 | 状态 |
|---|---|---|---|---|---|
| [Graham & Dodd, Security Analysis](https://www.mheducation.com/highered/product/security-analysis-graham-dodd) | primary/book | 1934；版本入口待核验 | 安全边际、内在价值与价格区分的思想框架 | 不提供现代点时数据、成本或样本外统计 | warning |
| [Shiller (1981), Do Stock Prices Move Too Much...?](https://doi.org/10.2307/1802789) | primary/paper | 1981 | 估值与后续现金流关系的可预测性问题 | 不等于可直接执行的个股交易规则 | checked |
| [Fama & French (1992), Cross-Section of Expected Stock Returns](https://doi.org/10.2307/2329112) | primary/paper | 1992 | B/M、规模与横截面收益关系 | 不证明主观价值投资的净 alpha | checked |
| [Fama & French (1993), Common Risk Factors](https://doi.org/10.1016/0304-405X(93)90023-5) | primary/paper | 1993 | HML 因子定义和资产定价研究背景 | 不证明 HML 在扣成本后始终可交易 | checked |
| [Lakonishok, Shleifer & Vishny (1994)](https://doi.org/10.1111/j.1540-6261.1994.tb04772.x) | primary/paper | 1994 | 价值/增长与投资者外推偏差的研究框架 | 不保证未来价值溢价继续存在 | checked |
| [Piotroski (2000), Value Investing](https://doi.org/10.2307/2672906) | primary/paper | 2000 | 以财务强度过滤价值组合的研究范例 | 不允许把论文样本期结果直接外推 | checked |
| [Asness, Moskowitz & Pedersen (2013), Value and Momentum Everywhere](https://doi.org/10.1093/rfs/hhs107) | primary/paper | 2013 | 多资产价值与动量的联合研究框架 | 不消除交易成本、容量和制度变化 | checked |
| [Kenneth French Data Library: F-F_Research_Data_Factors_CSV.zip](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip) | primary/data/local-evidence | 2026-07-27；202605 CRSP database；SHA-256 80b88699a18ac408e2456d25b1004e340f3f7f8d41d5b476a0285bc53c6f0436 | HML 与 Mkt-RF 的月度均值、CAGR、波动、Sharpe 和 MDD 派生统计 | HML 是多空因子代理，不是主观价值基金净收益；原始文件不再分发 | checked |

## 经典交易策略报告：第 3 章来源冻结（2026-07-27）

| 来源 | 类型 | 修订/获取日期 | 支持的具体主张 | 不能据此推断 | 状态 |
|---|---|---|---|---|---|
| [Fama & Blume (1966), Filter Rules](https://doi.org/10.1086/294849) | primary/paper | 1966 | 早期过滤规则、交易成本与市场效率检验背景 | 不代表现代多资产趋势净收益 | checked |
| [Brock, Lakonishok & LeBaron (1992)](https://doi.org/10.1111/j.1540-6261.1992.tb04681.x) | primary/paper | 1992 | 移动平均与交易区间规则的统计研究 | 不消除数据窥探和样本依赖 | checked |
| [Faber (2007), Tactical Asset Allocation](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461) | primary/paper | 2007 | 10 月移动平均的公开低频规则 | 不支持当前 ETF 或成本后的普遍收益 | checked |
| [Moskowitz, Ooi & Pedersen (2012), Time Series Momentum](https://doi.org/10.1016/j.jfineco.2011.11.003) | primary/paper | 2012 | 跨资产时间序列动量研究框架 | 不等于本报告两 ETF long/cash 示例 | checked |
| [Hurst, Ooi & Pedersen (2017), A Century of Evidence](https://doi.org/10.3905/jpm.2017.44.1.015) | primary/paper | 2017 | 长历史趋势跟随与危机期讨论 | 历史回溯不构成未来承诺 | checked |
| [Fung & Hsieh (2001), Trend Followers](https://doi.org/10.1093/rfs/14.2.313) | primary/paper | 2001 | 趋势策略的非线性风险暴露框架 | 不说明任意 CTA 都有相同凸性 | checked |
| [Yahoo Finance chart API SPY/GLD](https://finance.yahoo.com/) | secondary_data_proxy/local-evidence | 2026-07-27；月频；排除 2026-07 未完成月 | SMA10/SMA12 的信号滞后、成本、CAGR、Sharpe、MDD 和换手示例 | 不支持期货 CTA、多资产生产交易或未来预期收益 | warning |

## 经典交易策略报告：第 4 章来源冻结（2026-07-27）

| 来源 | 类型 | 修订/获取日期 | 支持的具体主张 | 不能据此推断 | 状态 |
|---|---|---|---|---|---|
| [Jegadeesh & Titman (1993)](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x) | primary/paper | 1993 | 赢家—输家动量的经典形成/持有框架 | 不保证当前市场净收益 | checked |
| [Rouwenhorst (1998), International Momentum](https://doi.org/10.1111/0022-1082.95722) | primary/paper | 1998 | 国际股票动量的跨市场证据 | 不替代本地税费与执行研究 | checked |
| [Asness, Moskowitz & Pedersen (2013)](https://doi.org/10.1093/rfs/hhs107) | primary/paper | 2013 | 多资产价值与动量联合框架 | 不消除容量、拥挤和制度变化 | checked |
| [Daniel & Moskowitz (2016), Momentum Crashes](https://doi.org/10.1016/j.jfineco.2015.12.002) | primary/paper | 2016 | 动量崩溃和状态依赖风险 | 不提供无参数崩溃预测器 | checked |
| [Novy-Marx (2012), Is Momentum Really Momentum?](https://doi.org/10.1016/j.jfineco.2012.03.003) | primary/paper | 2012 | 不同形成期收益对动量信号的作用 | 不支持任意参数选择 | checked |
| [French Momentum Factor ZIP](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_CSV.zip) | primary/data/local-evidence | 2026-07-27；202605 CRSP database；SHA-256 37baf72ae4eace9715e8746413d0122334c63aa4083fd1c3cf2060fa04e4bd28 | MOM 因子的均值、CAGR、波动、Sharpe 和 MDD 派生统计 | 多空因子不等于长-only ETF 轮动；原始文件不再分发 | checked |
| [Yahoo Finance SPY/GLD/SLV/TLT](https://finance.yahoo.com/) | secondary_data_proxy/local-evidence | 2026-07-27；月频；2007-06–2026-06 策略区间 | 12 月 Top-1/Top-2 排名、10bps 成本、换手和回撤示例 | 四资产样本不能代表完整股票或期货横截面 | warning |

## 经典交易策略报告：第 5 章来源冻结（2026-07-27）

| 来源 | 类型 | 修订/获取日期 | 支持的具体主张 | 不能据此推断 | 状态 |
|---|---|---|---|---|---|
| [Engle & Granger (1987)](https://doi.org/10.2307/1913236) | primary/paper | 1987 | 协整、误差修正与两步检验框架 | 相关资产必然协整 | checked |
| [Johansen (1988)](https://doi.org/10.1016/0165-1889(88)90041-3) | primary/paper | 1988 | 多变量协整向量检验 | 小样本估计必然稳定 | checked |
| [Lo & MacKinlay (1988)](https://doi.org/10.1093/rfs/1.1.41) | primary/paper | 1988 | 随机游走检验与收益可预测性问题 | 任意均值回复规则可盈利 | checked |
| [Gatev, Goetzmann & Rouwenhorst (2006)](https://doi.org/10.1093/rfs/hhj020) | primary/paper | 2006 | 配对交易形成期/交易期经典框架 | 当前市场仍有相同净收益 | checked |
| [Elliott, van der Hoek & Malcolm (2005)](https://doi.org/10.1080/14697680500149370) | primary/paper | 2005 | 连续时间价差与配对建模 | OU 适用于所有资产关系 | checked |
| [Avellaneda & Lee (2010)](https://doi.org/10.1080/14697680903124632) | primary/paper | 2010 | PCA/ETF 因子残差统计套利框架 | 因子残差长期保持平稳 | checked |
| [Yahoo Finance GLD/SLV daily adjusted close](https://finance.yahoo.com/) | secondary_data_proxy/local-evidence | 2026-07-27；2006-05-02–2026-07-24 | 滚动 OLS、z-score、滞后、5bps 成本、交易级统计与 MDD 失败案例 | 不构成正式协整检验、现货/期货结果或未来收益 | warning |

## 经典交易策略报告：第 6 章来源冻结（2026-07-27）

| 来源 | 类型 | 修订/获取日期 | 支持的具体主张 | 不能据此推断 | 状态 |
|---|---|---|---|---|---|
| [Fama & French (1993)](https://doi.org/10.1016/0304-405X(93)90023-5) | primary/paper | 1993 | 市场、规模、价值因子框架 | 因子收益必然稳定 | checked |
| [Fama & French (2015)](https://doi.org/10.1016/j.jfineco.2014.10.010) | primary/paper | 2015 | 盈利与投资因子扩展 | 五因子模型解释所有资产/净 alpha | checked |
| [Frazzini & Pedersen (2014)](https://doi.org/10.1093/rfs/hht046) | primary/paper | 2014 | Betting Against Beta 与低 beta 风险解释 | 任意低 beta ETF 都有超额净收益 | checked |
| [Blitz & van Vliet (2007)](https://doi.org/10.3905/jpm.2007.698039) | primary/paper | 2007 | 低波动效应与实现讨论 | 不消除行业、利率和拥挤风险 | checked |
| [Novy-Marx (2013)](https://doi.org/10.1016/j.jfineco.2013.01.003) | primary/paper | 2013 | 盈利能力与价值/成长组合关系 | 质量定义唯一或跨时代稳定 | checked |
| [Asness, Frazzini & Pedersen (2019)](https://doi.org/10.1007/s11142-019-09544-0) | primary/paper | 2019 | Quality Minus Junk 研究框架 | 质量不是无风险资产 | checked |
| [Kenneth French Five Factors ZIP](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip) | primary/data/local-evidence | 2026-07-27；202605 CRSP database；SHA-256 ddc0280b2bb8ca6c4c6ea5b68923a5549c37259bde468202108c11e812bd4241 | Mkt-RF、SMB、HML、RMW、CMA 的月度统计派生结果 | 多空因子不等于长-only 产品；原始文件不再分发 | checked |
| [Yahoo Finance SPY/SPLV/QUAL/IWM](https://finance.yahoo.com/) | secondary_data_proxy/local-evidence | 2026-07-27；月频；2013-08–2026-06 | 低波动、质量、规模 ETF 代理的 CAGR、波动、Sharpe、MDD | 不支持 ETF 代理等同论文因子或未来收益 | warning |

## 经典交易策略报告：第 7 章来源冻结（2026-07-27）

| 来源 | 类型 | 修订/获取日期 | 支持的具体主张 | 不能据此推断 | 状态 |
|---|---|---|---|---|---|
| [Engle (1982), ARCH](https://doi.org/10.2307/1912773) | primary/paper | 1982 | 条件异方差、波动聚集与 ARCH 递推的理论起点 | 不保证简单 ARCH 能提前捕捉跳跃或产生收益 alpha | checked |
| [Bollerslev (1986), GARCH](https://doi.org/10.1016/0304-4076(86)90063-1) | primary/paper | 1986 | GARCH(1,1) 条件方差递推与平稳约束 | 参数估计稳定或危机期预测无偏 | checked |
| [Moreira & Muir (2017), Volatility-Managed Portfolios](https://doi.org/10.1111/jofi.12513) | primary/paper | 2017 | 以可预测波动缩放策略暴露的研究框架 | 任意资产、目标波动或成本口径都能改善净收益 | checked |
| [Maillard, Roncalli & Teïletche (2010), Equal Risk Contribution](https://doi.org/10.3905/jpm.2010.36.4.060) | primary/paper | 2010 | 风险贡献、等风险贡献组合和约束优化定义 | 风险平价必然优于固定权重或最小方差 | checked |
| [Barroso & Santa-Clara (2015), Momentum Has Its Moments](https://doi.org/10.1016/j.jfineco.2015.01.007) | primary/paper | 2015 | 动量波动管理与崩溃风险调整框架 | 波动缩放可以消除所有动量崩溃或交易成本 | checked |
| [Frazzini & Pedersen (2014), Betting Against Beta](https://doi.org/10.1093/rfs/hht046) | primary/paper | 2014 | beta、杠杆约束与低风险资产定价的理论联系 | 低风险策略不存在融资、容量和相关性跃迁风险 | checked |
| [Yahoo Finance chart API SPY/GLD](https://finance.yahoo.com/) | secondary_data_proxy/local-evidence | 2026-07-27；月频；2005-12–2026-06；12 个月滞后风险估计、10% 目标波动、1.5 杠杆上限、10bps 换手成本 | 固定 50/50、逆波动风险平价与波动目标组合的净 CAGR、实际波动、Sharpe、MDD 和换手示例 | 不支持机构风险平价、真实融资收益、生产交易或未来预期收益；数据许可与调整细节待进一步核验 | warning |

## 经典交易策略报告：第 8 章来源冻结（2026-07-27）

| 来源 | 类型 | 修订/获取日期 | 支持的具体主张 | 不能据此推断 | 状态 |
|---|---|---|---|---|---|
| [Koijen, Moskowitz, Pedersen & Vrugt (2018), Carry](https://doi.org/10.1016/j.jfineco.2017.11.002) | primary/paper | 2018 | 跨资产 carry 的统一定义与风险溢价研究框架 | 不证明任意 carry 规则在扣成本后稳定盈利 | checked |
| [Gorton, Hayashi & Rouwenhorst (2013), Fundamentals of Commodity Futures Returns](https://doi.org/10.1093/rof/rfs019) | primary/paper | 2013 | 库存、便利收益与商品期货风险溢价关系 | 不支持连续合约 proxy 等于纯库存 carry | checked |
| [Lustig, Roussanov & Verdelhan (2011), Common Risk Factors in Currency Markets](https://doi.org/10.1093/rfs/hhq138) | primary/paper | 2011 | 外汇利差/carry 的共同风险因子与崩溃边界 | 不等于无融资约束的远期点数套利 | checked |
| [Baur & Lucey (2010), Is Gold a Hedge or a Safe Haven?](https://doi.org/10.1016/j.frl.2010.03.001) | primary/paper | 2010 | 黄金正常期 hedge 与极端期 safe haven 的条件定义 | 不支持黄金存在固定票息或所有危机都避险 | checked |
| [Szymanowska et al. (2014), Anatomy of Commodity Futures Risk Premia](https://doi.org/10.1111/jofi.12146) | primary/paper | 2014 | 商品期货风险溢价分解与期限结构研究框架 | 不支持当前 ETF 或连续合约净收益外推 | checked |
| [CME Group Gold Futures Contract Specifications](https://www.cmegroup.com/markets/metals/precious/gold.contractSpecs.html) | official-data/specification | 2026-07-27 | 黄金期货合约规模、报价和交割/交易规格入口 | 不提供本地回测的历史换月、成交价或融资数据 | checked |
| [FRED](https://fred.stlouisfed.org/) DFII10 与贸易加权美元入口 | primary/data | 2026-07-27 | 实际利率、美元和宏观状态变量的官方序列入口 | 本节未进行真实 FRED 点时下载，不声称修订安全或许可已完整核验 | warning |
| [Yahoo Finance chart API：GC=F/CL=F/ZB=F/6E=F 与 GLD/USO/TLT/UUP](https://finance.yahoo.com/) | secondary_data_proxy/local-evidence | 2026-07-27；月频共同样本 2007-01–2026-06；3 个月滞后 carry proxy；10bps 成本 | basis/roll proxy、四资产 carry-proxy 排名的净 CAGR、Sharpe、MDD 和换手示例 | 不支持纯 roll yield、真实期货总收益、抵押品利息、融资、合约级换月或未来收益；连续合约规则和数据许可待核验 | warning |

## 经典交易策略报告：第 9 章来源冻结（2026-07-27）

| 来源 | 类型 | 修订/获取日期 | 支持的具体主张 | 不能据此推断 | 状态 |
|---|---|---|---|---|---|
| [MacKinlay (1997), Event Studies in Economics and Finance](https://doi.org/10.2307/2729691) | primary/paper | 1997 | 估计窗口、事件窗口、AR/CAR/AAR/CAAR 与事件研究方法 | 不提供任意事件策略的长期 CAGR 或净收益 | checked |
| [Rigobon & Sack (2004), Impact of Monetary Policy on Asset Prices](https://doi.org/10.1016/j.jmoneco.2004.02.004) | primary/paper | 2004 | 货币政策与资产价格识别、同时性和高频工具变量边界 | 不等于低频主观宏观交易可直接执行 | checked |
| [Bernanke & Kuttner (2005), Stock Market Reaction to Federal Reserve Policy](https://doi.org/10.1111/j.1540-6261.2005.00760.x) | primary/paper | 2005 | 利率意外与股票事件窗口响应，约 25bp 意外变动与约 1% 股市响应的研究结果 | 不支持把事件窗口响应年化为长期收益 | checked |
| [Glick & Leduc (2012), Central Bank Announcements and Global Markets](https://doi.org/10.1016/j.jimonfin.2012.05.001) | primary/paper | 2012 | 央行资产购买公告与全球金融/商品价格反应框架 | 不保证黄金在所有政策事件中同向变化 | checked |
| [Kuttner (2001), Monetary Policy Surprises and Interest Rates](https://doi.org/10.1016/S0304-3932(01)00055-1) | primary/paper | 2001 | 联邦基金期货提取政策意外的测量方法 | 不提供股票或黄金的无摩擦交易成本 | checked |
| [Baur & Lucey (2010), Is Gold a Hedge or a Safe Haven?](https://doi.org/10.1016/j.frl.2010.03.001) | primary/paper | 2010 | 黄金正常期 hedge 与极端期 safe haven 的条件定义 | 不支持黄金无条件避险或固定 carry | checked |
| [本地基准快照](../data/classic_strategy_baseline_snapshot.json) | local-evidence | 2026-07-27；SPY/GLD 月频至 2026-06 | 报告中的股票、黄金和 50/50 基准 CAGR、Sharpe、MDD | 不支持主观宏观/事件策略的长期 alpha；没有点时事件预期和成交账本 | warning |

## 经典交易策略报告：第 10 章来源冻结（2026-07-27）

| 来源 | 类型 | 修订/获取日期 | 支持的具体主张 | 不能据此推断 | 状态 |
|---|---|---|---|---|---|
| [Markowitz (1952), Portfolio Selection](https://doi.org/10.2307/2975974) | primary/paper | 1952 | 均值—方差、协方差与分散化组合框架 | 不支持估计收益稳定或任意优化权重未来有效 | checked |
| [DeMiguel, Garlappi & Uppal (2009), Optimal Versus Naive Diversification](https://doi.org/10.1093/rfs/hhm075) | primary/paper | 2009 | 估计误差下等权与优化组合的比较框架 | 不证明等权在所有资产和成本下最优 | checked |
| [Black & Litterman (1992), Global Portfolio Optimization](https://doi.org/10.2469/faj.v48.n5.35) | primary/paper | 1992 | 市场均衡先验、观点、置信度和后验收益 | 不证明主观观点正确或可消除协方差误差 | checked |
| [Maillard, Roncalli & Teïletche (2010), Equal Risk Contribution](https://doi.org/10.3905/jpm.2010.36.4.060) | primary/paper | 2010 | 风险预算、风险贡献和 ERC 组合性质 | 不保证风险平价优于买入并持有或无融资风险 | checked |
| [Meucci, Risk and Asset Allocation](https://doi.org/10.1007/978-3-540-27706-0) | primary/book | 2005 | 风险分配、组合构建与不确定性治理的教材框架 | 不提供本地 ETF 实验的实证收益 | checked |
| [Yahoo Finance chart API SPY/GLD](https://finance.yahoo.com/) | secondary_data_proxy/local-evidence | 2026-07-27；月频共同样本 2006-01–2026-06；12 个月滞后信号、10bps constituent 成本 | 50/50、SMA12、逆波动、波动目标及两种策略等权集成的净 CAGR、Sharpe、MDD 和换手 | 不支持真实交易成本、融资、税费、生产组合或样本外稳健性；集成层未额外扣 overlay 成本 | warning |

## G06 / M03 来源冻结（2026-07-22）

本 slice 使用上表已核验的 MIT OCW 14.382、Hansen *Econometrics*、statsmodels 官方文档与 Efron Bootstrap 原始论文。它们分别支撑计量链条、渐近估计器、实现入口和 Bootstrap 方法边界；本地合成数据与估计器脚本只作为 `local-evidence`，不支撑真实市场或因果主张。

## G07 / M04 来源冻结（2026-07-22）

本 slice 冻结 statsmodels 时间序列官方文档、arch 官方文档、MIT 14.382 与 Hansen *Econometrics* 作为 ARIMA/VAR/状态空间/波动率、识别与推断的依据。由于当前环境未安装 `statsmodels` 与 `arch`，本地执行证据限定为 NumPy 简化递推；官方包对照列为后续环境准备项。

## G08 / P1 来源冻结（2026-07-22）

本项目使用 FRED API 与 ALFRED 官方入口定义宏观序列和 realtime/vintage 边界；真实 ALFRED 字段在本环境未成功访问，因此只使用本地合成 fixture 验证 `release_at <= asof_at` 与修订差异，不声称真实数据下载或许可已核验。

## G09 / P2 来源冻结（2026-07-22）

本项目冻结 Engle (1982) ARCH、Bollerslev (1986) GARCH 原始论文和 arch 官方文档，支撑条件方差递推、参数约束与实现边界。当前本地证据为 NumPy 合成序列和简化网格 QMLE；不声称运行了未安装的 `arch` 包或取得真实市场优势。

## G10 / M05 来源冻结（2026-07-22）

本模块使用 Hansen *Econometrics*、MIT 14.382、linearmodels 官方文档，以及 Card–Krueger、Imbens–Lemieux、Abadie–Diamond–Hainmueller 的原始研究入口，支撑面板、IV、DiD、RDD 和合成控制的识别边界。本地 FE/2SLS/DiD 结果仅为已知 DGP 下的 `local-evidence`；原始论文链接未在当前环境逐页浏览复核，具体实证数字不作引用。

## G11 / M06 来源冻结（2026-07-22）

本模块冻结 Sharpe (1964) CAPM、Fama–French (1993)、Fama–MacBeth (1973) 原始文献入口与 Kenneth French Data Library，支撑 CAPM、经验因子和两步横截面回归。合成三因子实验为 `local-evidence`；未引用原始论文的具体实证数字，公开因子文件的版本/单位将在 P3 单独冻结。

## G12 / P3 来源冻结（2026-07-22）

已直接下载 Kenneth French 官方 `F-F_Research_Data_Factors_CSV.zip` 与 `25_Portfolios_5x5_CSV.zip`；SHA-256 分别为 `80b88699a18ac408e2456d25b1004e340f3f7f8d41d5b476a0285bc53c6f0436`、`afc2f6c40237d07b99ab84ab9375a08bc301e3801e3ad8d91aa90d5aa9ec6295`，文件头均为 202605 CRSP database。原始文件不进入仓库；公开访问不被解释为再分发许可。

## G13 / M07 来源冻结（2026-07-22）

本模块冻结 Black–Scholes (1973)、Merton (1973) 与 Cox–Ross–Rubinstein (1979) 原始论文入口，支撑风险中性定价、连续时间模型和二叉树。债券/期权数值结果为本地 `local-evidence`，未使用市场曲线、波动率曲面或对冲 P&L，原始论文具体实证数字不作引用。

## G14 / M08 来源冻结（2026-07-22）

本模块冻结 Markowitz (1952)、Black–Litterman (1992) 原始文献入口及 Basel 市场风险框架，支撑均值—方差、观点后验和 VaR/ES 治理边界。本地权重与风险数字来自合成数据和示例观点；未引用监管资本数值，也不支持投资建议。

## G15 / P4 来源冻结（2026-07-22）

本项目沿用 Markowitz 与 Black–Litterman 来源，冻结 120 日估计窗、20 日再平衡、10 bps 线性成本和 0.35 单次 L1 换手上限。全部结果为合成 walk-forward `local-evidence`；不引用真实市场表现或将成本模型解释为可执行报价。

## G16 / M09 来源冻结（2026-07-22）

本模块冻结 Kyle (1985) 与 Almgren–Chriss (2001) 原始研究入口，支撑价格冲击、流动性与最优执行边界。订单簿、平方根冲击参数和容量均为合成 `local-evidence`；未核验真实逐笔数据许可或声称实盘成交表现。

## G17 / M10 来源冻结（2026-07-22）

本模块冻结 Carr–López de Prado (2014)、White (2000) Reality Check 与 Brier (1950) 概率评分入口，支撑回测过拟合、多重检验和概率评估边界。purging/embargo 与消融结果来自合成 `local-evidence`；未声称真实 alpha 或运行树模型库。

## G18 / P5 来源冻结（2026-07-22）

本项目沿用 White (2000) 与 Carr–López de Prado (2014)，冻结三段切分、20 日 embargo、六候选、5 bps 成本、validation-only 选择和失败账本。Bonferroni 只覆盖登记候选；全部收益为合成 `local-evidence`，不构成 alpha 发现。

## G19 / M11 来源冻结（2026-07-22）

本模块沿用 White (2000)、Carr–López de Prado (2014)，并冻结 Qlib 与 LEAN 官方仓库作为研究工作流/事件引擎入口。引擎差异和衰减来自合成 `local-evidence`；未运行 Qlib/LEAN 或声称平台性能比较。

## G20 / P6 来源冻结（2026-07-22）

已用 `git ls-remote` 冻结 QuantConnect/Lean 官方 HEAD `153d0b7427a918063a018ec18964ddf450edc125`。本机 `LEAN_CLI_NOT_FOUND`、`DOTNET_NOT_FOUND`；因此仅验证 QCAlgorithm 骨架语法和本地订单账本，LEAN compile/backtest 明确为 `NOT RUN`。

## G21 / P7 来源冻结（2026-07-22）

已冻结 Microsoft/Qlib 官方 HEAD `d5379c520f66a39953bad76234a7019a72796fd0`；本机 `QLIB_NOT_FOUND`。五阶段哈希链和恢复测试属于自建 `local-evidence`，不声称 Qlib API、Recorder、Dataset 或生产部署已运行。

## G22 / M12 来源冻结（2026-07-22）

本模块冻结 Wilson 可复现计算规范、NIST AI RMF 1.0 与 Federal Reserve/OCC SR 11-7 作为复现、风险治理、独立验证和持续监控的依据。本地治理 JSON 与验证器只覆盖最小字段/状态/事件规则，不代表机构审批或监管合规。

## G23 / Capstone 来源冻结（2026-07-22）

Capstone 目标论文冻结为 Fama–French (1993)，公开因子/组合 URL 与 P3 已核验的两个 SHA 固定在协议 JSON；样本目标为 1963-07 至 1991-12。G23 仅冻结协议，执行状态为 `protocol_frozen_not_executed`，不提前声称复现成功。

## G24 / Capstone 执行（2026-07-22）

两个官方文件重新下载后的 SHA 与协议一致，342 个月、25 组合的时序 OLS 与 Fama–MacBeth 已执行。原论文表格机器映射、HAC 和 GRS 保持 `NOT_RUN`，最终状态为 `partial_reproduction`，不声称完全复现。

1. 为概率统计、资产定价、衍生品、固定收益、组合、微观结构和金融机器学习各选一条主教材线。
2. 核验 ALFRED、SEC EDGAR、CRSP、Compustat、TAQ 的官方文档、许可和点时字段。
3. 冻结 purged/embargo、数据窥探、多重检验与 backtest overfitting 的原始论文。
4. 为每个实践项目记录数据版本、样本期、获取方式、哈希与不可再分发字段。
