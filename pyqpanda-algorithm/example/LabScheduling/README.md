# 共享实验室最小扰动重排

完整中文教程、输入规范、QUBO 推导、结果和演示流程：
[LabReschedule](../../../Tutorials/LabScheduling/README.md)。

在**仓库根目录**安装本地包和应用依赖后运行：

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m pyqpanda_alg.LabScheduling pyqpanda-algorithm/example/LabScheduling/data/medium.json --output reports/medium.json
```

默认 XY / seed 7：中等样例目标值 4、违反数 0、经典最优差距 0。
数据为合成数据；不需要 API Key、GPU 或真实量子硬件。
