# 验证与复现记录

本文前半保留初版历史记录；当前增强版状态与验证见文末。

日期：2026-09-21。基线：`upstream/develop@5f973ef`。
环境：WSL2 Linux x86_64，Python 3.12.3，PyQPanda3 0.4.1，
pyqpanda_alg 2.0.0（本地源码），NumPy 2.5.3，SciPy 1.18.1。
完整包版本见 [constraints-py312.txt](../../pyqpanda-algorithm/example/LabScheduling/constraints-py312.txt)。

## 上游基线

1. 官方 requirements 安装后，初始 `pytest test` 因未安装 Allure 插件拒绝
   `--alluredir` 参数；`import pyqpanda_alg` 也因未声明的 pandas 依赖失败。
2. 依据实际导入和测试所需，在应用专属 requirements-dev 中补充
   pandas/scikit-learn/allure-pytest。没有修改全局 Python 或上游依赖文件。
3. `test/pytest.ini` 没有 `[pytest]` 节，当前 pytest 9 仍能读取；使用独立配置
   固定本次收集规则。有效测试是 **18 项**；其他多个文件主体为注释，不能算作测试通过。
4. 独立运行原有测试得到 18 passed（35.99 s）。之后并发模拟压力下的重复检查
   触发一个 20 秒超时且产生线程争用，该轮中止，不将它当成功结果。
   固定 OMP/BLAS 单线程后完整复核 **18 passed，9.08 s**。

最终基线命令（在仓库根目录）：

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MPLBACKEND=Agg .venv/bin/python -m pytest \
  -c test/LabScheduling/pytest.ini \
  test/QAOA test/QAlgBase test/QPCA test/QSVM test/QARM \
  -o 'python_files=Test_*.py' --timeout=60 -q
```

## 新增应用测试

**56 passed，覆盖率 98.46%（455 条可执行语句，7 条未命中）**。
`model.py` 和 `classical.py` 行覆盖为 100%。命令见主教程第 8 节；
聚焦 CI 设置 95% 最低覆盖率，保留真实量子模拟测试。

- 对 simple 的 64 态、medium 的 4096 态逐一验证
  `QUBO = 原始成本 + A*(恰选一次平方罚分 + 冲突对数)`。
- 对 medium 全部 4096 态验证 Ising 对角值与 QUBO 能量，覆盖 qubit 10/11，
  避免 `x10` 字符串排序把映射改变。
- 对真实 CPUQVM 做非对称位序测试，对 X 线路做独立 NumPy 态矢量交叉验证。
- 对不同层数和角度验证 XY 域内单激发守恒，以及零角度均匀 one-hot 概率。
- 同 seed 重复求解验证参数、counts、最佳样本一致；最佳结果必须出现在 counts。
- 分别验证语义不可行、空域、零任务、单候选、同对多原因冲突、清洗与停机边界、
  原预约变更成本、参数错误、重复键/未知字段、NaN 和规模保护。
- 使用可行 simple + X + 1 shot 的真实模拟验证“未采到可行解”与“问题不可行”
  的区别，并验证 CLI 退出码 0/2/3/4。

覆盖工具注意：`--cov` 传**源码目录路径**。本机 coverage 对包含二进制导入链的
包名预加载触发 NumPy 重复导入错误；路径模式正常工作。没有为通过覆盖率而
mock 量子库。覆盖率未包含子进程执行的 CLI 分支，实际子进程命令另有断言验证。

## 代码质量与安装

- Ruff：E/F/I/UP/B 检查通过，格式检查通过，配置范围仅新增应用和测试。
- Mypy：7 个模块检查通过；仅跳过 PyQPanda3 不完整的二进制导出类型定义。
- `pip check`：无依赖冲突。
- 构建 wheel 成功；用 `--no-deps --target .venv/wheel-check` 安装到项目内目录，
  从该安装目录导入运行 medium，得到目标值 4、0 违反、差距 0。
- `git diff --check`、新增 Python 公开函数标注/文档字符串、相对文档链接、
  缓存/密钥/旧 pyqpanda API 检查在最终提交前完成。
- 新增 GitHub Actions workflow 的等价命令已本地运行；远程 Actions 尚未触发，
  不声称已经通过 GitHub CI。

## 多规模、多种子实验

统一预算：p=1，shots=512，restarts=2，COBYLA maxiter=60；种子 7、19、42。
采用 `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`，CPU 无噪声模拟。
按独立函数定义分别计时，`quantum.runtime_seconds` 包含量子训练、采样及诊断，
`exact.runtime_seconds` 包含全组合枚举和原始约束检查，不含公共建模和解释器导入。
`report.runtime_seconds` 包含读入、建模和三种求解流程，也不含解释器导入。
这些指标不是硬件量子执行耗时。

| 实例/方法 | seed 7 可行概率 | seed 19 | seed 42 | 最佳目标（对应三种子） |
|---|---:|---:|---:|---|
| simple / XY | 0.384406 | 0.688144 | 0.420494 | 5 / 5 / 5 |
| simple / X | 0.013176 | 0.013175 | 0.013176 | 5 / 5 / 5 |
| medium / XY | 0.393214 | 0.221515 | 0.130439 | 4 / 4 / 4 |
| medium / X | 0.002105 | 0.002105 | 0.002105 | 8 / 18 / 13 |

全部上述最佳样本可行，违反数为 0；X 在 medium 的最优差距为 4/14/9。
XY 在 simple 的模拟求解计时约 0.10–0.11 s，medium 约 0.30–0.34 s；
实际端到端还需解释器导入和建模。具体逐次耗时见
[summary.csv](results/summary.csv)，不是稳定性能阈值。

同预算均匀 one-hot 抽样在所有这些小实例也命中经典最优值。
XY simple 两个种子的可行概率低于均匀 one-hot，不能称为普遍优势。
三个种子不足以推导统计显著性或可扩展性；精确基线在此规模明显更快。
可行概率提升展示约束编码的作用，不能推出实用量子加速。

[每次完整 JSON](results/)包含输入 SHA-256、环境、QUBO 系数/映射、剪枝与
冲突原因、counts、优化历史、终止状态、排程、精确认证和均匀基线。
所有种子均纳入结果，没有以最佳种子替代均值。

默认一层线路资源也经 PyQPanda3 `QProg.depth()` / `count_ops()` 实测：

| 场景/混合器 | 原生门深度 | CNOT 数 |
|---|---:|---:|
| simple / XY | 36 | 34 |
| simple / X | 23 | 22 |
| medium / XY | 45 | 78 |
| medium / X | 32 | 54 |

这些数值含初态、相位与混合器，未做真实芯片映射，不代表硬件编译后资源。

最终完整重放：再次运行 12 组实验，将每份 JSON 递归删除 `runtime_seconds`
后与归档比较，全部完全一致（包括参数、概率、counts、排程和诊断）。
最终再次 fetch 的 develop 仍为 `5f973ef`；刷新开放 PR 仍为 70 项，无新增标题。

## 增强版验证（2026-09-21，已更新 PR #92）

以上 56 项和 12 份结果为增强前的历史基线。当前新增模块后实测：
**71 passed，98.44% 行覆盖率（771 条语句，12 条未命中），6.11 s**；
原有有效测试再次运行 **18 passed，8.22 s**。Ruff lint/format 全部通过，
Mypy **11 个模块**通过。`bookings.py`、`reduction.py`、`milp.py` 在本轮覆盖为 100%。
覆盖率是辅助指标；核心证据是独立建模、可行集合等价和真实 CPU 线路测试。

- 100 个随机小问题：对全部可行排程集合进行化简/回填一一比对，验证固定成本，
  原始输入 MILP 的可行性及最优值与穷举一致。
- simple/medium 每例 30 组随机参数，p=1/2/3，full 与 auto 相位概率误差 <1e-10；
  另测单候选混合域，X 分支保持完整相位。未声称两个优化轨迹必然一致。
- 业务 CSV：故障重排成本 6、3 张改约、0 违反，量子组件 4 比特；无故障对照成本 0。
- `--reduce` 最大组件资源上限实测退出 5，量子评价次数 0；没有静默经典替换。
- MILP 限时状态、带 incumbent 的限时、错误/非整数 incumbent 等防御逻辑单独测试；
  正常求解使用真实 HiGHS。故障返回模拟仅用于不易稳定触发的状态分支测试。
- 12 个新合成评价实例 × 10 个优化种子全部保存；9 可行、3 不可行，两经典基线一致。
  120 个已训练参数上的 full/auto 最大概率差 2.220446049250313e-16。
  整次评测约 49.06 秒；峰值进程 RSS 269832 KiB，包含 Python、依赖、MILP 和模拟器。
  这不是单个线路内存或硬件耗时承诺。
- 两次完整 120 训练的参数、counts、分布指标及独立抽样结果在排除耗时后完全相同。
  所有输入/核心源码哈希与归档 provenance 一致，最佳位串均真实出现在 counts。
- 公开 Python API 的参数/返回类型及 docstring 经 AST 扫描无遗漏。

原始实验记录与源代码指纹：[增强结果目录](results/enhanced/)。
评测协议在首次评价前冻结，详见 [BENCHMARK_PROTOCOL.md](BENCHMARK_PROTOCOL.md)。

远程状态说明：用户批准后，增强提交 `9c23ddb` 已推送至 PR #92，完整 PR 描述已更新。
对应 [Actions 运行](https://github.com/OriginQ/pyqpanda-algorithm/actions/runs/35576581365)
状态为 `action_required`，jobs 数量为 0，等待上游维护者批准。
此前“尚未触发”表述仅适用于首次本地验证时；没有远程 CI 通过的证据，
本地测试不可替代上游审核。后续发布记录提交不改变应用代码及本地验证结论。

### 增强版全新 wheel 安装复核

使用 `.venv/bin/python -m pip wheel --no-deps --no-build-isolation ./pyqpanda-algorithm`
构建 wheel，然后在项目内新建 `.venv/enhanced-clean`，按相同 constraints 和
requirements-dev 安装 wheel 及依赖。确认导入来自该新环境的 site-packages，
而非 editable 源码；`pip check` 无依赖冲突。
新环境中 **71 项测试通过（4.70 s）**，CSV 连锁改约/无故障对照与 medium CLI
均成功，分别保持成本 6/0/4，0 约束违反。
最初尝试 `python -m build` 时环境未安装 build，改用现有 pip 的 wheel 构建流程，
没有全局安装包或跳过构建验证。

## 第二批评测与审阅优化（2026-09-21）

冻结提交 `94efa84` 先于评价执行。新增 36 个异构实例/360 条配对种子记录，
以及三项预约决策全部留在 8 比特组件的业务演示；核心应用源码未修改。

- 当前完整应用测试 **76 passed，6.95 s**，覆盖率 **98.44%**；
  包含全部 36 个输入的控制排程、可行集合/成本证明和独立 MILP 一致性。
- Ruff lint/format（29 文件）、Mypy（11 个核心模块）、pip check 全部通过。
- 已有纯 wheel 隔离环境再次运行当前 76 项测试：**76 passed，5.45 s**；
  新业务演示实际得到成本 12、零违反，全部决策仍由量子组件求解。
  因本轮核心包未修改，复用已验证 wheel，不将示例修改称作新算法版本。
- 第二次完整重放只剔除键名以 `_seconds` 结尾的时间字段后，36 份实例结构记录、
  360 份配对训练记录完全一致；源码/输入哈希均匹配，实际最佳位串来自 counts。
- 业务案例全部 9 个可行选择公开；高价备用设备方案成本 14，三单后移成本 12。
- 新增独立 fork 的分支 push CI 入口，运行与 PR 相同的 Python 3.12 安装、质量检查、
  CPU 测试和三类演示；其结果与上游维护者批准状态分开记录。

结果入口：[异构评测分析](EVALUATION_V2.md)、[审阅路线](REVIEW_GUIDE.md)。
个人 fork 的 [Actions 35583744393](https://github.com/youshen2025/pyqpanda-algorithm/actions/runs/35583744393)
已在提交 `198ddfb` 上返回 **success**：Ubuntu / Python 3.12 新安装、Ruff/Mypy、
76 项真实 CPU 测试、medium CLI、CSV 连锁改约及新增取舍演示均通过。
官方 PR 对应运行 `35583752436` 仍为 `action_required`，等待上游维护者批准。
fork CI 成功不等于上游 CI 成功或 PR 合并；后续补录记录仅修改文档，
不改变已验证代码、数据、测试和工作流。

## 同总预算补充评价（2026-09-21）

- 协议先以 `eb9c5c3` 冻结；运行实现 `b140dab`。核心包与旧归档均未修改。
- **82 passed，7.86 s，核心行覆盖率 98.44%**；Ruff lint/format（32 文件）、
  Mypy（11 个核心模块）、pip check 均通过。
- 重新运行全部 36 实例 × 十种子，四条路径保留原始 counts 与状态；总训练评价
  上限 120、采样上限 512。首轮 90.81 s，第二轮 90.55 s，非计时字段完全一致。
- 第二轮 360 条直接 QAOA 记录还与旧 V2 归档一致（仅忽略计时），没有修改旧基准。
- 两次运行源码/输入/环境指纹一致，归档前源码哈希匹配，采样来源与预算上限复核通过。
- 22 个仍需量子的可行实例中：直接/分量 QAOA 最优 217/220、220/220；
  两个随机对照均为 220/220。低 shots 条件曲线包含分量 QAOA 低于随机的实例。
- 新增测试涵盖预算守恒、不足时停止、单分量与直接路径完全一致、分量回填、
  实际 CPU 样本来源、不可行域和重放比较器拒绝篡改 counts。

完整解释与复现命令见 [MATCHED_BUDGET.md](MATCHED_BUDGET.md)，原始记录见
[results/matched](results/matched/)。此处本地验证不代替当前提交的远程 CI。

本轮发布提交 `a3716ed` 的独立 fork
[Actions 35586823475](https://github.com/youshen2025/pyqpanda-algorithm/actions/runs/35586823475)
实际返回 **success**：Ubuntu / Python 3.12.14 全新安装，Ruff/Mypy，
**82 passed，16.32 s，覆盖率 98.44%**，三类演示全部通过，取舍示例成本 12。
上游运行 `35586829560` 仍为 `action_required`。最终补录仅修改文档，
保留该成功运行验证过的代码、测试与数据不变。

## 输入快照与报告完整性修复（2026-09-21）

本轮在临时目录先复现两处实际问题：`--output` 同输入时覆盖原文件；输入在
求解后被修改时，报告哈希对应新文件而非求解数据。改为读取一次原始字节快照，
同一快照解析与哈希；`parse_problem(text)` 复用严格 JSON 校验。CLI 在求解前
检查同路径/符号链接/硬链接，报告写完同目录临时文件后才替换目标。

- 本地 **92 passed，9.39 s，核心覆盖率 98.87%**；新增十项 I/O 回归。
- Ruff lint/format（33 文件）、Mypy（11 模块）、pip check 全部通过。
- 原有 **18 passed，7.75 s**。首次误用应用 `*.test.py` 规则未收集到上游测试；
  显式采用上游 `Test_*.py` 规则后执行，未把空收集计为通过：

  ```bash
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m pytest -c test/LabScheduling/pytest.ini -o 'python_files=Test_*.py' test --ignore=test/LabScheduling --timeout=60
  ```

- 重新构建 wheel 并强制安装到已有 `.venv/enhanced-clean` 隔离环境，确认实际
  导入 site-packages。**92 passed，5.60 s**，取舍演示成本 12、最优差距 0。
- 写入/替换故障用 I/O 层故障注入验证；数据修改/删除测试仍运行真实 CPU 求解。
  CRLF 原字节哈希、有效输出符号链接保留、临时文件清理也已检查。

量子线路、优化器、QUBO 与冻结实验数据未改。旧归档中的源码指纹保留为对应
历史提交的记录（同预算归档为 `a3716ed`），不重写成修复后的源码指纹。
普通写入失败保护不等于断电持久性或多写入进程事务保证，接口说明见主教程。

发布提交 `36adc9f` 的个人 fork
[CI 35588841891](https://github.com/youshen2025/pyqpanda-algorithm/actions/runs/35588841891)
全部通过：全新安装、质量检查、**92 passed，17.03 s，覆盖率 98.87%**、
三类 CPU 演示成功，取舍样本与证书仍为成本 12。上游 `35588846744` 仍待
维护者批准；最后补录 CI 的提交仅改变文档。

## 可选无支持候选化简（2026-09-21）

范围与边界数据先在 `086840d` 提交；默认模式保留，增加 `--reduce --pruning arc`。
实现采用确定性 AC-3，记录完整对方域及逐对冲突原因，不增加依赖或新量子变体。

- 本地 **102 passed，13.91 s，核心覆盖率 98.92%**（831 行，9 行未覆盖）；
  reduction.py 的 128 条可执行语句全部覆盖。
- 200 个固定种子小问题、全部既有 36 个 V2 输入和一个专门构造的边界案例，
  逐一核对原始语义全部可行集合、成本、回填映射与删除依据。
- 40 个输入的默认化简审计与上一发布 `f64a7ad` 完全相同；旧归档未改。
- 18 比特单组件降至 12 比特，无预先固定项；seed 7/19/42 均实际采到最优成本 3。
  V2 中仅 5/36 最大组件缩小，全部结果与无收益/不可行实例保留。
- 第二次完整评价与第一次所有非 `_seconds` 字段完全一致；14 项源码/协议指纹
  和全部 37 项输入指纹核对通过。没有用旧归档源码指纹替换当前指纹。
- Ruff lint/format（35 文件）、Mypy（11 核心模块）、pip check 通过。
- 原有 **18 passed，8.75 s**，使用此前记录的 `Test_*.py` 收集方式。
- 最新 wheel 构建并重新安装至项目内 `.venv/enhanced-clean`，确认来自 site-packages；
  最终完整 **102 passed，9.00 s**，包含新增模式真实 CPU 演示与全记录重放。
  wheel SHA-256：`d4cd80c87c604e0cedaf48b93e5200564e601d7e579b3658a5f044be7d2237aa`。
- 增加端到端 CLI 的聚焦 CI 步骤；源码/数据路径、相对文档链接、公开函数注解与
  文档字符串、Git diff 均已检查。

新评价脚本在初次运行中暴露输出目录未创建、内存 tuple 与 JSON list 比较问题，
均在归档前修复；新增命令级真实 CPU 重放测试，最终记录来自修复后的两次完整运行。
数学证明、经典算法出处、局部一致性不保证全局可行的反例及复现命令见
[ARC_PRUNING.md](ARC_PRUNING.md)。新模式的远程 CI 状态在发布后另行记录。
