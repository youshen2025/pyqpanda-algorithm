# 共享实验室最小扰动重排

完整中文教程、输入规范、QUBO 推导、结果和演示流程：
[LabReschedule](../../../Tutorials/LabScheduling/README.md)。

在**仓库根目录**安装本地包和应用依赖后运行：

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m pyqpanda_alg.LabScheduling pyqpanda-algorithm/example/LabScheduling/data/medium.json --output reports/medium.json
```

默认 XY / seed 7：中等样例目标值 4、违反数 0、经典最优差距 0。
数据为合成数据；不需要 API Key、GPU 或真实量子硬件。

增强演示（CSV 预约→连锁改约→4 比特 CPU 求解→双经典认证→变更表/甘特图）：

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MPLBACKEND=Agg .venv/bin/python pyqpanda-algorithm/example/LabScheduling/booking_demo.py
```

[增强教程与全部实验](../../../Tutorials/LabScheduling/ENHANCEMENTS.md)解释安全传播、
组件回填、XY 相位精简、MILP、12 实例 × 10 种子评测及已知失败。
