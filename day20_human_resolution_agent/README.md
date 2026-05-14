# Day 20 Human Resolution Agent

这是 Day 20 的最小练习项目。

## 目标

理解：
- 为什么 human handoff checklist 之后还需要人工处理结果回写
- 如何把人工处理结论写回 session state
- 为什么有些任务会被重新入队，有些任务会被人工关闭
- 为什么“人工介入”也应该进入统一工作流，而不是停留在口头结论

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\human_resolution_assistant.py
```

## 你会看到什么

- priority queue
- primary execution results
- retry queue
- dead letter queue
- human handoff checklist
- human resolution decisions
- applied human resolutions
- requeue candidates
- closed items
- 最终 execution report

## 建议你做的实验

你可以故意让某个 session 进入 dead letter queue，然后观察：

- 它是否出现在 human handoff checklist 里
- 人工处理决定是 `requeue` 还是 `close`
- session 文件里是否真的写回了人工处理结果
- execution report 是否已经把人工处理结果也纳入闭环
