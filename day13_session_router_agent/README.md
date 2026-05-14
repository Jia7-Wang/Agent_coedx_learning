# Day 13 Session Router Agent

这是 Day 13 的最小练习项目。

## 目标

理解：

- 为什么多 session 之后还需要“先看全局再选一个 session”
- 如何先汇总多个 session 的 overview
- 如何让模型基于 overview 选择当前最值得继续的 session
- 为什么 session 路由是更复杂 Agent 系统的重要入口

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\session_router_assistant.py
```

## 你会看到什么

- 当前有哪些可用 session
- 每个 session 的 overview
- 模型是否调用知识库工具
- 模型选中了哪个 session
- 选中的理由
- 被选中 session 的状态更新结果

## 建议你做的实验

修改不同 session 里的：

- `current_stage`
- `current_blocker`
- `history`

再重新运行脚本，观察模型最终会选哪个 session。
