# Day 5 RAG 与知识库实操手册

## 1. 今天的目标

Day 5 我们开始学习一个非常重要的主题：

`RAG（Retrieval-Augmented Generation）`

你可以先把它简单理解成：

`先检索外部资料，再把检索到的内容交给模型回答。`

今天你要理解的核心问题是：

`为什么很多 Agent 不能只靠模型参数记忆，而要先查知识库。`

---

## 2. 什么是 RAG

RAG 可以拆成两部分：

- `Retrieval`：检索
- `Generation`：生成

也就是：

1. 先从外部资料里找相关内容
2. 再让模型基于这些内容组织回答

这和“直接问模型”最大的区别是：

`答案不只来自模型记忆，还来自外部上下文。`

---

## 3. 今天为什么先不用向量库

很多教程一上来就讲：

- embeddings
- chunking
- vector database
- rerank

这些东西后面都要学，但今天不是最好的起点。

今天我们先做一个最小版本：

- 本地文本知识库
- 简单切块
- 关键词匹配检索
- 把命中的文本块交给模型回答

这样你会先看懂：

`RAG 的骨架到底是什么。`

---

## 4. 今天这个示例会做什么

我们会准备一份本地知识库文档，内容是：

- Agent 学习路线
- Git / Docker / 调试等工程常识
- 项目建议

然后程序会：

1. 读取这份知识库
2. 把文本切成多个块
3. 根据问题做简单检索
4. 把最相关的文本块交给模型
5. 让模型基于这些上下文回答

---

## 5. 今天的目录结构

```text
day5_rag_basics/
  |- .env.example
  |- knowledge_base.txt
  |- simple_rag_demo.py
  |- README.md
```

---

## 6. 你今天会学到什么

跑完之后，你应该能理解：

- 什么是知识库
- 什么是 chunk
- 什么是 retrieval
- 为什么模型回答前要先拿 context

---

## 7. 你今天的运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day5_rag_basics
Copy-Item .env.example .env
python .\simple_rag_demo.py
```

如果你已经有前几天的 `.env`，直接复制这 3 个值：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

---

## 8. 你运行时重点看什么

重点看这些输出：

- loaded chunks
- top matched chunks
- final answer

它们分别表示：

- 知识库被切成了哪些块
- 当前问题检索命中了哪些块
- 模型基于这些块组织出的最终回答

---

## 9. 一句话总结

Day 5 的重点不是“更复杂的模型调用”，而是理解：

`先查资料，再回答，这就是最小 RAG。`

---

## 10. Day 5 进阶：增强版 RAG

如果你已经跑通 `simple_rag_demo.py`，可以继续运行：

```powershell
python .\day5_rag_basics\enhanced_rag_demo.py
```

这个版本会额外展示：

- chunk 编号
- chunk 命中分数
- 命中的关键词
- 最终回答中的来源引用

你要重点观察的是：

- 为什么某些块被命中
- 为什么某些块分数更高
- 最终答案有没有基于这些块来组织内容
