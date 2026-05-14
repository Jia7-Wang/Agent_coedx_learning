# Day 14 Session Priority Queue Agent

这是 Day 14 的最小练习项目。

## 目标

理解：

- 为什么只选出“第一个 session”还不够
- 如何基于多个 session 生成优先级队列
- 如何让模型输出完整排序而不是单点选择
- 为什么优先级队列是工作流调度的重要基础

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\session_priority_queue_assistant.py
```

## 你会看到什么

- 当前有哪些可用 session 概览
- 模型是否调用知识库工具
- 模型输出的 priority queue
- 队列中的 top 1 session
- 被更新的 session 状态

## 建议你做的实验

修改某个 session 的：

- `current_blocker`
- `history`
- `current_stage`

再重新运行脚本，观察队列整体顺序会不会变化。
