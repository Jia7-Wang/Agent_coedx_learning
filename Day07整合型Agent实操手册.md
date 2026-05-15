# Day 7 整合型 Agent 实操手册

## 1. 今天的目标

Day 7 是一个很重要的节点。

因为从今天开始，你不再只是分别学习：

- Tool Calling
- 工作流
- RAG / 知识库

而是要把它们真正合在一起，做一个更完整的小 Agent。

今天你要理解的核心问题是：

`一个真正像样的 Agent，往往不是单点能力，而是多个能力协同工作。`

---

## 2. 今天这个 Agent 会做什么

我们会做一个“学习助理 Agent”：

1. 用户提出一个学习目标
2. 模型判断要不要查知识库
3. 如果需要，就调用知识库检索工具
4. 程序把检索结果回传
5. 模型基于检索结果生成一个“下一步执行方案”

这个过程同时包含：

- 工具调用
- 知识库检索
- 结果整合
- 多步骤执行

---

## 3. 为什么这比 Day 6 更进一步

Day 6 的重点是：

- 把知识库检索变成工具

Day 7 的重点是：

- 检索之后，模型不只是给一个问答结果
- 而是给出更像“行动方案”的输出

也就是说，Day 7 更接近“助理型 Agent”，而不是单纯“知识问答 Agent”。

---

## 4. 今天你会学到什么

跑完之后，你应该能理解：

- 一个 Agent 如何组合多个能力
- 为什么知识库工具只是中间步骤，不是最终目标
- 为什么真正的 Agent 更强调“行动建议”而不只是“知识回答”

---

## 5. 今天的目录结构

```text
day07_integrated_agent/
  |- .env.example
  |- knowledge_base.txt
  |- integrated_learning_agent.py
  |- README.md
```

---

## 6. 你今天的运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day07_integrated_agent
Copy-Item .env.example .env
python .\integrated_learning_agent.py
```

如果你已经有前几天的 `.env`，直接复制这 3 个值：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

---

## 7. 你运行时重点看什么

重点看这些输出：

- `Tool calls`
- `Knowledge tool result`
- `Final action plan`

它们分别表示：

- 模型是否决定查知识库
- 知识库工具返回了什么
- 最终生成的是不是更像一个行动型结果

---

## 8. 一句话总结

Day 7 的重点是理解：

`知识库检索、工具调用和结果规划可以合在一个 Agent 里协同工作。`
