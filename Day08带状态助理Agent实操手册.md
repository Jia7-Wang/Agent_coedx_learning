# Day 8 带状态助理 Agent 实操手册

## 1. 今天的目标

Day 7 你已经做出了一个会：

- 调知识库工具
- 基于检索结果生成行动方案

的小助理 Agent。

Day 8 我们继续往前走一步，让这个助理：

`不只是给通用方案，而是根据当前学习进度状态给不同建议。`

---

## 2. 今天和 Day 7 的差别

### Day 7

用户提出目标，Agent 查知识库，再给一个统一行动方案。

### Day 8

除了目标之外，程序还会维护一个：

- 当前阶段
- 已完成内容
- 当前卡点

然后让 Agent 根据这些状态，给更贴近当前进度的建议。

---

## 3. 这就是“助理开始记住你”的第一步

这里的“记住”不是神奇记忆，而是：

`程序把用户当前状态对象一起传给模型`

所以 Agent 可以根据状态判断：

- 你是刚开始，还是已经学到一半
- 你卡在 Git，还是卡在 Tool Calling
- 下一步到底该补什么

---

## 4. 今天你会学到什么

跑完之后，你应该能理解：

- 同一个知识库 Agent，在不同 state 下会给不同建议
- 为什么状态会让助理“更像助理”
- 为什么很多 Agent 不只是问答，而是“带状态的建议系统”

---

## 5. 今天的目录结构

```text
day08_stateful_assistant/
  |- .env.example
  |- knowledge_base.txt
  |- stateful_learning_assistant.py
  |- README.md
```

---

## 6. 你今天的运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day08_stateful_assistant
Copy-Item .env.example .env
python .\stateful_learning_assistant.py
```

如果你已经有前几天的 `.env`，直接复制这 3 个值：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

---

## 7. 你运行时重点看什么

重点看这些输出：

- `Current learner state`
- `Tool calls`
- `Knowledge tool result`
- `Final state-aware plan`

它们分别表示：

- 当前学习进度状态
- 模型是否决定查知识库
- 检索回来的知识块
- 最终是否根据 state 给出了更具体的建议

---

## 8. 一句话总结

Day 8 的重点是理解：

`同样的知识库，同样的目标，不同的 state 会让 Agent 给出不同的建议。`
