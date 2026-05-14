# Day 6 知识库 Agent 实操手册

## 1. 今天的目标

Day 5 你已经学会了最小 RAG：

- 先检索
- 再回答

Day 6 我们往前走一步，把 RAG 和 Tool Calling 合在一起，做一个：

`知识库 Agent`

今天你要理解的核心问题是：

`知识库检索本身，也可以被设计成一种工具能力。`

---

## 2. Day 5 和 Day 6 的区别

### Day 5

程序固定先做检索，再把上下文交给模型。

### Day 6

程序把“检索知识库”声明成一个工具，让模型自己决定：

- 要不要查知识库
- 查什么问题
- 查到结果后再怎么回答

所以 Day 6 更像真正的 Agent。

---

## 3. 今天这个示例会做什么

我们会把本地知识库检索封装成一个工具：

- 工具名：`search_knowledge_base`

然后让模型面对用户问题时自己决定：

- 是否调用这个工具
- 用什么查询参数调用

程序再：

1. 执行检索工具
2. 返回命中的 chunk
3. 让模型基于检索结果生成最终答案

---

## 4. 今天你会学到什么

跑完后，你应该能理解：

- RAG 可以是固定流程
- RAG 也可以变成工具调用的一部分
- “查知识库”本质上就是一种工具能力

---

## 5. 今天的目录结构

```text
day6_knowledge_agent/
  |- .env.example
  |- knowledge_base.txt
  |- knowledge_agent_demo.py
  |- README.md
```

---

## 6. 你今天的运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day6_knowledge_agent
Copy-Item .env.example .env
python .\knowledge_agent_demo.py
```

如果你已经有前几天的 `.env`，直接复制这 3 个值：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

---

## 7. 你运行时重点看什么

重点看这些输出：

- `Tool calls`
- `Knowledge search result`
- `Final answer after knowledge retrieval`

它们分别表示：

- 模型是否决定调用知识库工具
- 检索命中了哪些 chunk
- 模型如何基于这些 chunk 回答

---

## 8. 一句话总结

Day 6 的重点是理解：

`知识库检索不只是预处理步骤，它也可以成为 Agent 自己会调用的一种工具。`
