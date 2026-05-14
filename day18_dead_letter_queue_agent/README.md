# Day 18 Dead Letter Queue Agent

这是 Day 18 的最小练习项目。

## 目标

理解：

- 为什么 retry queue 之后自然会出现 dead letter queue
- 如何给失败项设置最大重试次数
- 为什么超过阈值后不应该无限自动重试
- 为什么死信队列是系统稳定性的最后一道边界

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\dead_letter_queue_assistant.py
```

## 你会看到什么

- 当前 session 概览
- priority queue
- primary execution results
- retry queue
- retry results
- dead letter queue
- 最终 execution report

## 建议你做的实验

你可以在 `.env` 里设置：

```text
FAIL_SESSION_ID=demo-engineering-agent
MAX_RETRY_COUNT=1
```

这样就更容易观察：

- 某个失败项进入 retry
- retry 之后仍然失败
- 最终被送进 dead letter queue
