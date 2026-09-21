# 〖创新应用〗新增基于QUBO的共享实验室最小扰动重排应用

参赛队伍：**youshen**。用户已确认完成官网报名。

关联 #13。目标分支：`OriginQ/pyqpanda-algorithm:develop`。

## 解决的问题

共享实验室设备临时停机后，重新安排多时隙实验，同时满足设备清洗占用、小组
互斥和工序先后，并尽量保留原预约。新增完整应用 LabReschedule，提供 JSON
输入、可解释 QUBO、PyQPanda3 CPU 量子模拟、经典认证、命令行和中文教程。

例：中等样例中一台仪器停机，应用仅移动 A-prepare，保留其他三条预约，
得到成本 4、0 个约束违反，与独立精确基线一致。

## 应用创新和数学原理

- 显式候选预约编码及停机/超时剪枝；保留候选删除原因和变量映射，
  中等样例从 14 个候选降为 12 比特。
- 将偏好与原预约变更成本结合，每任务恰选一次和各类不兼容候选对转成 QUBO。
  惩罚取 A=1+每任务最大候选成本之和，文档证明其全局最小值满足可行性。
- 复用上游 W 态、XY 交换和成本相位组件；XY 保持每任务恰选一次，
  单候选域不加混合门。提供 H/RX 的 X-QAOA 对照。
- 分开报告量子采样、精确最优认证与均匀 one-hot 基线；不以经典解替换量子结果。
  有效但不可行、输入错误和有限采样未命中分别输出不同状态及退出码。

QUBO 与 XY 算法采用已有理论，本贡献定位为场景建模及完整可复现创新应用，
不宣称发明新的量子算法或证明量子优势。已对照开放 PR #60，后者为灌溉预测与
水预算调度，本应用处理实验设备故障、清洗、前序和预约稳定性；去重快照见教程。

## 主要改动

- `pyqpanda_alg/LabScheduling/`：输入、建模、独立检查、经典穷举、QAOA、报告和 CLI。
- `example/LabScheduling/`：简单/中等/不可行 JSON，开发依赖、环境约束和实验脚本。
- `test/LabScheduling/`：数学穷举和真实 CPUQVM 回归；单独配置，不修改上游模块。
- `Tutorials/LabScheduling/`：中文建模与演示教程、验证记录、12 组原始结果和图表。
- 文档索引和聚焦 GitHub Actions；没有引入 Web、数据库、云账号或旧 pyqpanda API。

## 安装和一条命令运行

从仓库根目录，使用 Python 3.12 项目虚拟环境：

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -c pyqpanda-algorithm/example/LabScheduling/constraints-py312.txt -e ./pyqpanda-algorithm -r pyqpanda-algorithm/example/LabScheduling/requirements-dev.txt
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m pyqpanda_alg.LabScheduling pyqpanda-algorithm/example/LabScheduling/data/medium.json --output reports/medium.json
```

补充 pandas/scikit-learn 是因为当前上游包的导入链需要；依赖声明限于本应用
开发安装说明，不在本 PR 修复已有依赖问题。CPU 即可运行，无 Key 或硬件需求。

## 测试与实测结果

本地 WSL / Python 3.12.3 / PyQPanda3 0.4.1：

- 新增 56 项测试通过，应用行覆盖率 98.46%；原有有效测试 18 项全部通过。
- Ruff lint/format、Mypy（7 模块）、pip check 通过。
- wheel 构建及从 wheel 安装目录运行 medium 通过。
- simple 的 64 态和 medium 的 4096 态验证原约束/QUBO 等价；
  medium 全部 Ising 对角能量也与 QUBO 一致。
- 种子 7/19/42：XY 在 simple/medium 各三次均得到精确最优 5/4，0 违反；
  medium 的 X 对照为 8/18/13，未隐藏差距。
- 完整概率、counts、优化历史、耗时、哈希和环境版本见教程 results。

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m pytest -c test/LabScheduling/pytest.ini test/LabScheduling --cov=pyqpanda-algorithm/pyqpanda_alg/LabScheduling --cov-fail-under=95
```

远程 GitHub Actions 尚未运行，提交后等待 CI。上游初始环境的依赖/插件问题和
并发线程争用记录见 `Tutorials/LabScheduling/VALIDATION.md`。

## 已知限制

无噪声 CPU 态矢量，最多 16 个存活量子候选；精确认证最多一百万组合。
只处理非负整数成本、单位容量、确定时长和单小组任务。模拟概率训练和诊断
具有指数开销，不代表真机有限采样训练。seed 控制本地初始化和 Born 分布抽样；
不同版本可能产生不同优化轨迹。均匀 one-hot 在这些小实例也能找到最优，
经典穷举更快，未宣称量子加速。
