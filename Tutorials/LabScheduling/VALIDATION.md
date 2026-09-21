# 验证与复现记录

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
