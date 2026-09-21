# 〖创新应用〗新增基于QUBO的共享实验室最小扰动重排应用

参赛队伍：**youshen**，已完成官网报名。关联 #13；目标分支 develop。

## 解决的问题与应用贡献

设备临时停机后，如何重排实验、满足清洗/小组互斥/工序前序，同时降低原预约
变更成本？新增完整离线应用 LabReschedule，从 JSON 或 CSV 预约窗口生成
可追溯 QUBO，在 PyQPanda3 CPU 上求解，再由原始输入 MILP 与小规模穷举核验。

完整取舍示例：烘箱故障后，三个实验可整体后移（成本 12、改约三单），也可
付费使用备用设备（成本 14、改约一单）。三项决策全部留在 8 比特组件，
没有预处理固定项；默认实际量子样本得到成本 12、零违反，随后由双经典基线认证。
原有 CSV 连锁传播案例也保留，展示被迫改约的删除原因链。

建议从[审阅路线](https://github.com/youshen2025/pyqpanda-algorithm/blob/contest/qubo-scheduling-app/Tutorials/LabScheduling/REVIEW_GUIDE.md)开始，按路线定位核心代码、
数学证明、关键测试及实验记录；数据与图表占 diff 的大部分。

贡献集中在可证明的资源节省与可审计求解：

- 原始候选日历剪枝、单候选传播、严格独立冲突分量、固定成本和原变量回填；
  不启发式冻结“未直接受故障影响”的预约，不静默截断或以经典解替代量子样本。
- XY 线路中删去可达子空间上恒零的 one-hot 罚项，保留完整 QUBO 审计和原缩放。
  medium 的原生 CNOT 从 78 降至 54，深度 45 降至 35；相同参数分布等价。
- 独立原始输入 MILP 不使用 QUBO 的剪枝表或冲突图；区分最优证书、不可行、
  限时 incumbent、量子抽样失败和组件超限，记录所有失败。
- 第一批 12 个实例 × 10 个种子保留；第二批独立冻结 36 个异构实例，每格 4 个
  数据种子、每例 10 个优化种子，比较日历剪枝/传播/分解/相位精简各阶段。

QUBO、XY、传播和 MILP 均来自已有理论；本贡献是应用建模、编译、验证与复现流程，
不声称发明新的通用量子算法或量子加速。题目区别于开放灌溉应用 #60；
已有调研快照和 scope 在 PLAN.md 与教程中说明。

## 数学与架构

每个候选一个二进制变量，成本为偏好加原预约变更费用。完整 QUBO 为
`Q = sum(c_i*x_i) + A*sum_t(sum_Dt(x_i)-1)^2 + A*sum_conflicts(x_i*x_j)`。
对非负成本取 `A=1+各任务最大存活候选成本之和`；存在可行解时，任一不可行
位串能量高于所有可行解。`x=(I-Z)/2` 转为 Ising，成本相位按同一 A 缩放。
W 初态与域内 XY 交换保持每任务单激发，故可只在 XY 相位中删除 one-hot 罚项。
X/H/RX 对照仍保留完整罚项。原生 CRY 与 CNOT 分别报告，不作硬件分解计数承诺。

传播只删与必选候选冲突的选择；组件无跨界禁止对，回填与原可行排程一一对应，
成本等于固定偏移加组件成本。近似组件求解没有全局最优保证。

主要改动集中于 `pyqpanda_alg/LabScheduling/`、`example/LabScheduling/`、
`test/LabScheduling/`、`Tutorials/LabScheduling/` 及文档索引/聚焦 CI。
复用上游 W 态、XY 交换与成本相位组件，未修改上游算法或进行无关重构。

## 安装与演示

在仓库根目录使用 Python 3.12 虚拟环境：

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -c pyqpanda-algorithm/example/LabScheduling/constraints-py312.txt -e ./pyqpanda-algorithm -r pyqpanda-algorithm/example/LabScheduling/requirements-dev.txt
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MPLBACKEND=Agg .venv/bin/python pyqpanda-algorithm/example/LabScheduling/tradeoff_demo.py
```

普通 JSON CLI：

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m pyqpanda_alg.LabScheduling pyqpanda-algorithm/example/LabScheduling/data/medium.json --reduce --output reports/medium.json
```

输出到项目 reports；不需要 Key、GPU、真机、Web 或数据库。pandas/scikit-learn
补充项用于上游导入链，声明限定在应用开发依赖内。

## 测试与实测证据

WSL / Python 3.12.3 / PyQPanda3 0.4.1：

- 当前 76 项应用测试通过，行覆盖率 98.44%；核心算法未变，原有 18 项有效测试的通过记录保留。
- Ruff lint/format、Mypy 11 模块通过；真实 CPUQVM 测试，无模拟器 mock。
- wheel 全新隔离环境安装，确认 site-packages 导入，71 项测试及两类 CLI 演示通过。
- 原有 64/4096 态 QUBO/约束等价与 4096 态 Ising 验证保留。
- 100 个随机小问题核对化简前后全部可行集合和回填成本，再与原始 MILP 比较。
- simple/medium 各 30 组 p=1/2/3 随机角度验证 XY 相位精简；单候选混合域另测。
- 12 个冻结评价实例含 9 个可行、3 个不可行，穷举和 MILP 结论全部一致。
  可行实例 86/90 个训练种子的单次最优概率高于均匀 one-hot，4 个退化，全部保留。
  原始/精简线路在相同已训练参数上的最大概率差为 2.23e-16 以下。
- 120 次训练再次复现，除耗时外参数、counts、分布指标和独立采样结果完全一致。
- 20/35/50 任务的合成链仅运行经典 MILP，目标 40/71/100；明确标记未执行量子求解。
- 第二批支持 2–4 候选、1–3 时隙时长、0–2 清洗时间和三类故障；36 个原排程
  均验证无故障时合法。故障后 24 可行、12 不可行，全部原始可行集合与回填成本一致。
- 第二批 240 个可行训练种子有 206 个最优概率高于均匀、34 个退化；一个实例连
  种子均值也退化，均保留。分解可能增加总训练/采样预算，不作同预算优势声明。
- 360 条配对求解记录完整重放，除耗时外完全一致；其中纯经典传播明确标注。

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m pytest -c test/LabScheduling/pytest.ini test/LabScheduling --cov=pyqpanda-algorithm/pyqpanda_alg/LabScheduling --cov-fail-under=95
```

证明、接口、协议、全部失败记录、资源与命中曲线见
`Tutorials/LabScheduling/ENHANCEMENTS.md`；安装及 CI 实际状态见 VALIDATION.md。
旧 schema 1 开发基线独立保留，新版为 schema 2，默认使用精简 XY。

个人 fork 的 [Ubuntu / Python 3.12 CI](https://github.com/youshen2025/pyqpanda-algorithm/actions/runs/35583744393)
已在提交 `198ddfb` 上全部通过：安装、质量检查、76 项真实 CPU 测试和三类演示。
官方 PR 工作流仍为 `action_required`，等待上游维护者批准；fork CI 不代替上游审批。
后续仅补录发布与 CI 记录，不修改被验证的代码、数据、测试或工作流。

## 限制

每个量子组件最多 16 比特，总编译候选最多 256；精确枚举最多一百万组合，
超限报告跳过并由 MILP 尝试认证。MILP 最多 2048 个原始候选，限时不冒充最优。
只处理非负整数成本、确定时长、单位容量、单小组任务。训练与概率诊断为
指数复杂度的无噪声模拟；训练后的 shots 命中曲线不是端到端加速。
第一批每格一个数据种子，第二批每格四个，仍是小规模合成证据，没有实际实验室用户验证。
经典基线在此规模更快，量子效果并非每个种子改善，硬件噪声下不保证相位精简等价。
