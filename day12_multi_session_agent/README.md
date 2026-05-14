# Day 12 Multi Session Agent

这是 Day 12 的最小练习项目。

## 目标

理解：

- 为什么一个 Agent 不能只维护一个 `state.json`
- 如何用 `session_id` 区分不同会话
- 如何按不同 `session_id` 读写不同状态文件
- 为什么多 session 是真实 Agent 系统的重要基础

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\multi_session_assistant.py
```

## 你会看到什么

- 当前加载的是哪个 session
- 对应 session 的状态文件路径
- 更新前的 learner state
- 知识库检索结果
- 结构化更新方案
- 写回后的 learner state

## 建议你做的实验

连续运行两次脚本，观察：

- `demo-python-agent.json`
- `demo-rag-agent.json`

你会发现它们的状态和 history 会分别演进，不会互相覆盖。
