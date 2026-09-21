# 2026 本源杯：LabReschedule 约束调度应用

## 调研与定题（2026-09-21）

- 工作目录最初为空；已克隆官方仓库，以 `upstream/develop`
  `5f973efccb84bc193157d1ccebe32137e307293b` 创建
  `contest/qubo-scheduling-app`。不推送、不创建 PR，最终由用户确认。
- 阅读 develop 的 README、CONTRIBUTING、QUBO/QAOA 源码、测试和 CI，
  并核对 main 的贡献指南。新增内容沿用 `pyqpanda_alg`、`example`、
  `test`、`Tutorials` 结构，不重构上游模块。
- [赛题 #13](https://github.com/OriginQ/pyqpanda-algorithm/issues/13)
  明确允许完整创新应用，参与期 4 月 10 日至 9 月 30 日，PR 基分支 develop，
  标题 `〖创新应用〗+简要描述`。按用户目标于 9 月 28 日前备妥。
- [贡献指南](https://github.com/OriginQ/pyqpanda-algorithm/blob/main/CONTRIBUTING.md)
  要求测试、用户文档及索引；本地完成后经个人 fork 提交。
- [比赛主页](https://qcloud.originqc.com.cn/learning/zh/2026ccf) 为 JavaScript
  页面，初次抓取仅得到启用 JavaScript 提示，不能据此声称已核实平台报名细则。
- 查阅 [PyQPanda3 AI 参考](https://github.com/OriginQ/pyqpanda3-skill)：
  使用整数比特编号、CPUQVM、PyQPanda3 API；以安装版本和实际测试核对参考代码。
- GitHub 匿名 REST API 限流，改读 GitHub HTML；逐页读取开放 PR 第 1–3 页，
  第 4 页为空；另查已关闭 PR、开放 Issues #8/#13/#38 和 develop 源码。
  未发现考试/实验室重排同题。最接近
  [PR #60](https://github.com/OriginQ/pyqpanda-algorithm/pull/60)
  是小麦灌溉预测和水预算调度，已阅读其正文；本项目不做水预算、预测或农业应用。
  开放 PR #45/#69 涉及 QUBO 默认参数和多项式解析，避免依赖其修复或重复提交。
  去重是当前快照结论，提交前须再查。

## 选题与范围

**LabReschedule：设备停机后的共享实验室预约最小扰动重排。**
面向校园小组实验：每项实验选择一个允许的设备/开始时刻候选，持续多个时隙；
考虑设备停机、清洗占用、小组互斥、工序先后。目标权衡时刻偏好与原预约变更。
输入显式候选而非全时间网格，消除停机候选，减少比特数并保留剪枝原因。

1. 严格 JSON 校验，清晰报告错误输入与有效但不可行的问题。
2. 稀疏候选一位有效编码，目标及约束转为二次项；给出有证明的惩罚上界。
3. PyQPanda3 CPU 上运行 QAOA，复用 pyqpanda_alg 相位线路和 XY 混合器组件。
   XY 保持每项任务的选择数；X 混合器提供消融对照。
4. 独立任务候选笛卡尔积穷举，认证可行性与最优值；不向量子求解器传入最优解。
5. 固定种子参数初始化与模拟概率采样，仅从真实采样集合选择量子候选；
   输出违反明细、目标、概率质量、耗时、最优差距及模型规模。
6. 简单、中等、不可行数据；一条命令运行；多种子实验、数学恒等式测试、
   位序/单候选/空候选/错误输入/采样失败测试；中文教程和演示流程。

不引入 Web、数据库、云服务或真实硬件。小规模端到端正确性优先；
默认量子规模限制为 16 比特，经典认证限制候选组合数，明确指数复杂度。
不声称量子加速或获奖保证。

## 风险与应对

- 上游测试配置缺 `[pytest]` 节；依赖声明可能缺 pandas/scikit-learn。
  先记录原始失败，再用外部配置运行，不修改无关上游问题。
- 原库量子算法接口与技能示例可能不一致：用真实线路小测试确认，
  显式比特映射，绕开符号名字排序和常数多项式边界。
- QAOA 可能找不到可行或最优解：保留原始结果，不静默修复/替换；
  可行概率、均匀抽样基线及经典认证分别展示。
- XY 只保持恰选一次，不能保证设备/小组/先后约束，仍需惩罚和独立检查。
- 主页面平台细则、个人报名信息和 GitHub fork 未核实；准备提交材料，
  不伪造个人信息，外部发布前由用户确认。

## 实施与验收顺序

1. 环境：项目 `.venv`，Python 3.12；开发依赖和原始测试基线。
2. 模型：输入、候选剪枝、独立校验、QUBO、经典认证与数学测试。
3. 量子：CPUQVM + 上游组件、种子控制、采样报告和 CLI。
4. 打磨：多规模/多种子/混合器对照、质量检查、中文教程与实验归档。
5. 提交：逻辑拆分本地 commits、diff/秘密/缓存检查、PR 描述、
   `SUBMISSION_CHECKLIST.md`，呈现成果后等待 push/PR/平台提交确认。

每阶段实际结果追加到本文件及实验验证报告。

## 阶段结果

- 调研完成：直接读取官方主页前端资源，补充核实开源赛道报名和 PR 均截至
  9 月 30 日；未登录核实个人报名。70 项开放 PR 完整标题快照见
  `Tutorials/LabScheduling/research_pr_snapshot.json`，相关差异见 `RESEARCH.md`。
- 环境完成：Python 3.12.3，项目 `.venv`；PyQPanda3 0.4.1，editable
  pyqpanda_alg 2.0.0；没有全局安装。开发环境约束已锁定。
- 上游基线：初始缺 Allure 插件，且 import 缺 pandas；在应用开发依赖补齐
  pandas/scikit-learn/Allure。原配置虽然缺节标题，当前 pytest 9 能解析，
  不把该事实错误报告为必然配置崩溃。独立配置下原有 18 项有效测试全部通过。
  多数其他测试文件已被上游注释，不计作通过。详见验证报告。
- 实现完成：输入、剪枝、QUBO/Ising、CPUQVM QAOA、XY/X、独立精确基线、
  均匀 one-hot 基线、采样证据、CLI、多种子基准与静态图表。
- 测试与打磨：应用数学模型与 Ising 对角能量逐状态验证；种子 7/19/42
  在 simple/medium 的默认 XY 均采到经典最优，X 对照在 medium 有非零差距。
  不宣称量子优势；原始 JSON/CSV、中文教程、聚焦 CI 与验证说明随项目提交。
- 交付与提交信息：详见 `SUBMISSION_CHECKLIST.md` 和 `PR_DESCRIPTION.md`。
  尚未推送、创建 PR 或向平台提交，按用户要求保留最终确认步骤。

## 发布授权更新（2026-09-21）

用户已批准推送至个人 fork 并向官方 develop 创建 PR，确认官网报名完成，
队伍名称 `youshen`。上述“等待确认/尚未发布”为最初交付阶段的历史记录；
当前执行进度以 `SUBMISSION_CHECKLIST.md` 为准。

## 发布结果（2026-09-21）

以 GitHub 账号 `youshen2025` 发布个人 fork 功能分支，创建官方 develop 的
[正式 PR #92](https://github.com/OriginQ/pyqpanda-algorithm/pull/92)，队伍 `youshen`。
初版发布时远程与本地提交一致，GitHub 报告可合并。Actions 已触发，但等待上游维护者
批准运行，不能计作 CI 通过。官网报名由用户确认；比赛平台 PR 链接与回执仍待核对。

## 2026-09-21 增强实施

用户批准按独立复审继续。实现 XY 恒零 one-hot 相位删除（完整 QUBO 保留）、
单候选传播/严格独立冲突分量/原变量回填、原始输入 MILP 与 CSV 预约窗口导入。
采用 12 个冻结合成评价实例 × 10 个优化种子；保留三个不可行实例和量子退化种子。
增强报告 schema 2，与旧归档结果区分。证明、接口和结果见
[Tutorials/LabScheduling/ENHANCEMENTS.md](Tutorials/LabScheduling/ENHANCEMENTS.md)。

增强完成时先保留本地提交供用户审阅；用户随后批准继续，现已推送增强版并更新 PR #92。
发布前刷新 upstream/develop，仍为 `5f973ef`；PR 为 Open、非草稿、目标 develop，
GitHub 报告可合并。增强提交 `9c23ddb` 的 Actions 运行 `35576581365` 等待维护者批准，
尚未执行远程测试。未操作比赛平台，提交回执仍待核对。
官网奖项归属的复核和原始建议见 [AWARD_REVIEW.md](AWARD_REVIEW.md)。

## 第二轮优化（2026-09-21，用户批准继续）

保持核心算法不变，补齐业务与评价代表性、逐步对照和审阅体验。
先以 `94efa84` 冻结 36 个异构输入（每格 4 数据种子），再完成 360 条配对运行，
其中 24 可行、12 不可行；不删除退化种子或纯经典传播情形。
三单取舍案例将全部决策留在 8 比特组件，实际量子样本成本 12，独立认证最优；
高价备用设备对照成本 14。逐阶段资源与全部原始可行集合均经过核验。
第二次完整重放完全复现非计时字段；76 应用测试通过，覆盖率 98.44%。
独立 fork CI 将使用同一 workflow，不能替代上游批准或比赛平台回执。
用户本轮批准优化与后续发布，继续更新现有 PR，不另开重复贡献。
