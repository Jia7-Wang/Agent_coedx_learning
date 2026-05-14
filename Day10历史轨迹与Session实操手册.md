# Day 10 历史轨迹与 Session 实操手册

## 1. 今天的目标

Day 9 你已经做到了：

- Agent 会读取当前 state
- Agent 会结合知识库给出建议
- Agent 会把建议写回 state

Day 10 我们继续往前走一步：

`让 Agent 在更新 state 的同时，保留每一次更新轨迹。`

也就是说，今天你要理解的是：

`真实的 Agent 系统里，光有“当前状态”还不够，还要有“状态是怎么变成这样的历史记录”。`

---

## 2. 今天和 Day 9 的差别

### Day 9

程序会把模型生成的结构化结果写回当前 state。

### Day 10

程序除了更新当前 state，还会额外把这次变化记进 `history`，例如：

- 之前处在哪个阶段
- 现在推进到了哪个阶段
- 这次最重要的行动是什么
- 为什么会这样推进

这就更像一个真正能“留下过程痕迹”的助理 Agent。

---

## 3. 为什么要学 history / session trace

当 Agent 只会改当前状态时，你只能看到“现在是什么样”。

但如果有 `history`，你还能回答这些问题：

- 这个状态是怎么一步步变过来的？
- 上一次更新发生了什么？
- 为什么今天的建议和昨天不一样？
- 如果结果不好，应该回头查哪一步？

这对下面几类场景特别重要：

- 多轮学习助理
- 长任务工作流
- 调试和排查问题
- 项目复盘

一句话总结：

`current state 解决“现在是什么”，history 解决“怎么走到现在”。`

---

## 4. 今天你会学到什么

跑完今天的示例后，你应该能理解：

- `state` 和 `history` 的职责区别
- 为什么 Agent 不只是“读写当前值”
- 为什么 session trace 是很多 Agent 系统里的核心调试手段
- 怎样在程序里把一次结构化更新追加成历史记录

---

## 5. 今天的目录结构

```text
day10_session_history_agent/
  |- .env.example
  |- knowledge_base.txt
  |- session_history_assistant.py
  |- README.md
```

---

## 6. 运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day10_session_history_agent
Copy-Item .env.example .env
python .\session_history_assistant.py
```

如果你已经有前几天的 `.env`，直接复用这 3 个值即可：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

---

## 7. 运行时重点看什么

这次建议你重点观察这几段输出：

- `Initial learner state`
- `History before update`
- `Knowledge tool result`
- `Structured update plan`
- `Updated learner state`
- `History after update`

它们分别表示：

- 当前状态对象
- 更新前的历史轨迹
- 知识库检索结果
- 模型生成的结构化更新方案
- 写回后的最新状态
- 追加完成后的新 history

---

## 8. 你要特别看懂的一件事

今天最核心的一行思想不是“模型回答了什么”，而是：

`程序把本次更新，变成了一条可以回看的历史记录。`

这说明 Agent 的执行结果，不再只是一次性输出，而是：

- 会影响当前状态
- 会沉淀为历史信息
- 会继续影响后面的建议

这就是很多真正的带状态 Agent 系统开始变复杂、也开始变有价值的地方。

---

## 9. 一句话总结

Day 10 的重点是理解：

`Agent 不只会更新 state，还会把“这次为什么这样更新”记录进 session history。`
