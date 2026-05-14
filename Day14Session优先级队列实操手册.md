# Day 14 Session 优先级队列实操手册

## 1. 今天的目标

Day 13 你已经做到了：

- Agent 会先看所有 session 的概况
- Agent 会自动选出当前最该继续的一个 session

Day 14 我们继续往前走一步：

`让 Agent 不只选出第一个，还能给多个 session 排出一个优先级队列。`

也就是说，今天你要理解的是：

`当 session 变多后，系统最好不仅知道“先做谁”，还知道“然后做谁”。`

---

## 2. 今天和 Day 13 的差别

### Day 13

程序输出一个 `selected_session_id`，表示当前最该继续谁。

### Day 14

程序会输出一个完整的 `priority_queue`：

- 第 1 个是谁
- 第 2 个是谁
- 第 3 个是谁

每个队列项都带一个原因。

这就从“单点路由”升级成了“排序调度”。

---

## 3. 为什么要学优先级队列

只知道“第一个”在简单场景够用，但一旦任务多起来，就会遇到这些问题：

- 做完第一个后，下一个该是谁？
- 当前顺序变化了吗？
- 哪些 session 是高优先级但还没轮到？

优先级队列可以解决这些问题，因为它给出了：

- 当前顺序
- 排序依据
- 后续执行方向

一句话总结：

`Day 13 解决“先选谁”，Day 14 解决“整体怎么排”。`

---

## 4. 今天你会学到什么

跑完今天的示例后，你应该能理解：

- 为什么 overview 可以进一步变成 queue
- 为什么优先级队列比单个选择更适合调度
- 一个 Agent 如何基于 queue 推进 top 1 session
- 为什么真实系统里队列通常还会结合分数、规则或人工干预

---

## 5. 今天的目录结构

```text
day14_session_priority_queue_agent/
  |- .env.example
  |- knowledge_base.txt
  |- session_priority_queue_assistant.py
  |- README.md
  |- sessions/
      |- demo-python-agent.json
      |- demo-rag-agent.json
      |- demo-engineering-agent.json
```

---

## 6. 运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day14_session_priority_queue_agent
Copy-Item .env.example .env
python .\session_priority_queue_assistant.py
```

---

## 7. 今天建议你做的实验

建议你做这个实验：

1. 先运行一次脚本
2. 记下 priority queue 顺序
3. 修改某个 session 的 blocker 或 stage
4. 再运行一次
5. 比较队列顺序有没有变化

你会更容易感受到：

`队列不是固定的，而是会随着 session 状态变化而重新排序。`

---

## 8. 运行时重点看什么

重点看这些输出：

- `Available sessions`
- `Knowledge tool result`
- `Priority queue`
- `Top priority learner state before update`
- `Structured update plan`
- `Updated learner state`

它们分别表示：

- 当前所有 session 的概况
- 知识库对排序判断的支持
- 模型输出的完整优先级队列
- 队列第一名的原始状态
- 针对第一名的更新方案
- 更新后的新状态

---

## 9. 一句话总结

Day 14 的重点是理解：

`多 session 系统不仅要会挑出当前最优先的一个，还要能把所有 session 排成一个可执行的优先级队列。`
