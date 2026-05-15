# Day 6 Knowledge Agent

这是 Day 6 的最小练习项目。

## 目标

理解：

- 如何把知识库检索变成工具
- 模型如何自己决定要不要查知识库
- 检索结果如何回传模型

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\knowledge_agent_demo.py
```

## 你会看到什么

- 模型是否触发知识库工具
- 工具返回的命中块
- 基于检索结果生成的回答
