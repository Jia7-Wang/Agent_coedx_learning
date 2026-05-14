# Day 10 Session History Agent

这是 Day 10 的最小练习项目。

## 目标

理解：

- Agent 如何读取当前状态
- Agent 如何更新当前状态
- Agent 如何把每次更新记录进 `history`
- 为什么 session trace 对调试和复盘很重要

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\session_history_assistant.py
```

## 你会看到什么

- 初始 learner state
- 更新前的 history
- 模型是否调用知识库工具
- 结构化更新方案
- 更新后的 learner state
- 更新后的 session history
