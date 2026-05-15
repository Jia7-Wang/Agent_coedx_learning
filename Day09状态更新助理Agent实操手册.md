# Day 9 状态更新助理 Agent 实操手册

## 1. 今天的目标

Day 8 你已经做出了一个：

- 会读当前状态
- 会查知识库
- 会给出更贴近当前阶段建议

的助理 Agent。

Day 9 我们继续前进一步：

`让 Agent 在给出建议之后，更新状态对象。`

也就是说，今天你要第一次看到：

`state 不只是输入，也会成为输出。`

---

## 2. 今天和 Day 8 的差别

### Day 8

程序把 state 给模型，模型基于 state 回答。

### Day 9

模型除了回答，还会生成一个结构化结果，程序再把这个结果写回 state，例如：

- 当前最优先任务
- 下一阶段名称
- 今日行动项

这就更像“助理真的推动你往前走”。

---

## 3. 今天你会学到什么

跑完之后，你应该能理解：

- 为什么很多 Agent 系统要读 state，也要写 state
- 为什么 state 不是只读数据
- 为什么“状态更新”是助理型 Agent 的关键能力

---

## 4. 今天的目录结构

```text
day09_state_update_agent/
  |- .env.example
  |- knowledge_base.txt
  |- state_updating_assistant.py
  |- README.md
```

---

## 5. 你今天的运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day09_state_update_agent
Copy-Item .env.example .env
python .\state_updating_assistant.py
```

如果你已经有前几天的 `.env`，直接复制这 3 个值：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

---

## 6. 你运行时重点看什么

重点看这些输出：

- `Initial learner state`
- `Knowledge tool result`
- `Structured update plan`
- `Updated learner state`

它们分别表示：

- 初始状态
- 知识库检索结果
- 模型生成的结构化状态更新建议
- 程序真正写回后的新状态

---

## 7. 一句话总结

Day 9 的重点是理解：

`助理型 Agent 不只是根据 state 回答，它还可以根据当前结果推进 state。`
