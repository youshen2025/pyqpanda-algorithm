# 本源杯提交检查表

交付日期：2026-09-21；用户目标 9 月 28 日前备妥，比赛截止 9 月 30 日。
当前工作分支：`contest/qubo-scheduling-app`；目标：`upstream/develop`。

## 已完成的本地工作

- [x] 核对比赛主页、赛题 #13、README、main/develop 贡献指南。
- [x] 逐页检查开放 PR、开放 Issues、develop 源码；记录 70 项开放 PR 快照。
- [x] 区分最近的灌溉应用 #60，采用共享实验室故障重排题目。
- [x] PLAN.md 写明范围、数学风险和实施结果。
- [x] 项目内 `.venv`，Python 3.12.3；无全局依赖安装。
- [x] 固定依赖版本、种子、线程设置；无 Key、Token 或真实硬件要求。
- [x] JSON 输入、严格错误处理、简单/中等/不可行三个数据集。
- [x] QUBO 完整公式、变量映射、惩罚系数证明、Ising 转换及位序说明。
- [x] PyQPanda3 CPUQVM 实际运行，复用 pyqpanda_alg 线路组件。
- [x] 独立精确基线、均匀 one-hot 对照、XY/X 对照；量子结果只来自采样。
- [x] 输出目标、原始成本、违反数/原因、耗时、采样证据及最优差距。
- [x] 新增 56 测试通过；覆盖率 98.46%；原有 18 有效测试通过。
- [x] Ruff、格式、Mypy、pip check；wheel 构建及安装目录运行成功。
- [x] 中文评委教程、几分钟演示流程、12 组实验 JSON/CSV 和静态 SVG。
- [x] 提供 PR 标题、完整描述、develop 目标和聚焦 CI。
- [x] 按建模、量子应用、文档证据整理本地提交；工作区最终保持干净。
- [x] Git diff/相对链接/公开 API/缓存/秘密/旧版 API 检查。

## 发布进度

- [x] 用户已审阅并明确批准 push/创建 PR（2026-09-21）。
- [x] 用户已确认官网报名完成，队伍名称 **youshen**（2026-09-21）。
- [x] 发布准备时再次刷新开放 PR 和 upstream/develop；与初始快照一致。
- [ ] 在用户个人 GitHub 空间 fork 官方仓库，配置 `origin`（当前只有 `upstream`）。
- [x] upstream/develop 仍为 `5f973ef`，无需合并，代码和测试结论不变。
- [ ] 推送功能分支，通过个人 fork 向官方 develop 创建 PR。
- [ ] 使用 `PR_DESCRIPTION.md` 第一行标题及其正文，关联 #13，确认远程 CI。
- [ ] 按比赛平台要求补充队伍/PR 链接并保存提交回执，不以本地提交代替报名。
- [ ] 9 月 28 日前完成 PR 准备/提交；最迟 9 月 30 日前完成规定平台流程。

批准后使用的分支推送目标应是个人 fork，不能直接推到官方仓库：

```bash
# 将 YOUR_GITHUB_USER 替换为自己的 GitHub 账户名；先创建个人 fork。
git remote add origin https://github.com/YOUR_GITHUB_USER/pyqpanda-algorithm.git
git push -u origin contest/qubo-scheduling-app
```

PR 标题：`〖创新应用〗新增基于QUBO的共享实验室最小扰动重排应用`。
审阅入口：[中文教程](Tutorials/LabScheduling/README.md)、
[验证报告](Tutorials/LabScheduling/VALIDATION.md)、[PR 描述](PR_DESCRIPTION.md)。
合并、评奖和平台审核结果由主办方决定；本清单不把尚未发生的审核标为完成。

当前发布阻碍（2026-09-21）：GitHub 连接账号为 `youshen2025`，访问
`youshen2025/pyqpanda-algorithm` 返回 404；当前连接没有创建 fork 的接口。
已请用户提供可访问的个人 fork 链接。尚未推送或创建 PR；这是能力/访问问题，
不需要再次批准已授权的发布操作。
