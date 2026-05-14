# Day 4 State Workflow

这是 Day 4 的最小练习项目。

## 目标

理解：

- 什么是 state
- 什么是 workflow
- 为什么多步骤任务要共享状态

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\workflow_task_planner.py
```

4. 想继续看“多步循环工作流”，再运行：

```powershell
python .\workflow_loop_planner.py
```

## 你会看到什么

- 初始状态
- 模型拆解出的子任务
- 更新后的状态
- 基于状态生成的下一步建议
