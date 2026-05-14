# Day 5 RAG Basics

这是 Day 5 的最小练习项目。

## 目标

理解：

- 什么是知识库检索
- 什么是 chunk
- 什么是 retrieval
- 什么是 context-based answering

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\simple_rag_demo.py
```

4. 想继续看“带分数、带 chunk 编号、带引用”的增强版，再运行：

```powershell
python .\enhanced_rag_demo.py
```

## 你会看到什么

- 知识库文本块
- 检索命中的文本块
- 基于上下文生成的答案
