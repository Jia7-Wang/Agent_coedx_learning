# Day 17 Retry Queue Agent

这是 Day 17 的最小练习项目。

## 目标

理解：

- 为什么 execution report 之后自然会出现 retry queue
- 如何收集失败项并单独重试
- 为什么失败恢复不应该直接打断整轮执行
- 为什么 retry queue 是调度系统的重要稳定性机制

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\retry_queue_assistant.py
```

## 你会看到什么

- 当前 session 概览
- 模型输出的 priority queue
- 本轮 execution targets
- 本轮 primary execution results
- retry queue
- retry execution results
- 最终 execution report

## 建议你做的实验

你可以故意让某个 session 在主执行阶段失败，观察：

- 它是否进入 retry queue
- retry 阶段是否会再次尝试它
- 最终 report 是否区分 primary failure 和 retry result
