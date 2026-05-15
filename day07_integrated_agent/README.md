# Day 7 Integrated Agent

这是 Day 7 的最小练习项目。

## 目标

理解一个整合型 Agent 如何同时用到：

- 工具调用
- 知识库检索
- 最终行动方案生成

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\integrated_learning_agent.py
```

## 你会看到什么

- 模型是否调用知识库工具
- 工具返回的检索结果
- 模型整合出的行动方案
