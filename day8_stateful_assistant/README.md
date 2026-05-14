# Day 8 Stateful Assistant

这是 Day 8 的最小练习项目。

## 目标

理解：

- 状态如何影响 Agent 建议
- 同一个 Agent 如何根据当前学习进度调整输出
- 知识库 + 工具 + 状态如何结合

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\stateful_learning_assistant.py
```

## 你会看到什么

- 当前学习状态对象
- 模型是否调用知识库工具
- 基于状态输出的行动建议
