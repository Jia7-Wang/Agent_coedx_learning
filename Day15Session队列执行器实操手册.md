# Day 15 Session 队列执行器实操手册

## 1. 今天的目标

Day 14 你已经做到了：

- Agent 会输出完整优先级队列
- Agent 会根据队列更新 top 1 session

Day 15 我们继续往前走一步：

`让 Agent 按队列顺序真正执行前几个 session，而不只是更新第一个。`

也就是说，今天你要理解的是：

`系统不只是会排队，还开始会沿着队列逐个推进工作。`

---

## 2. 今天和 Day 14 的差别

### Day 14

程序会输出完整 `priority_queue`，但只更新第 1 名。

### Day 15

程序会：

1. 输出完整 `priority_queue`
2. 取前 2 个 session 作为执行目标
3. 依次为它们生成更新方案
4. 依次写回状态文件

这就从“排序器”升级成了“最小版执行器”。

---

## 3. 为什么要学队列执行

如果系统只会排序，不会执行，很多工作还得你手动接上。

而真实工作流通常要求：

- 先定顺序
- 再按顺序推进
- 批量处理前几个任务

这就是队列执行的意义：

`把调度结果真正转成执行动作。`

---

## 4. 今天你会学到什么

跑完今天的示例后，你应该能理解：

- 为什么“priority queue”之后自然会出现“executor”
- 为什么执行器通常只拿前 N 个，而不是一口气执行全部
- 一个 Agent 如何按顺序逐个更新多个 session
- 为什么真实系统里执行器还会涉及失败重试、并发和中断恢复

---

## 5. 今天的目录结构

```text
day15_session_queue_executor_agent/
  |- .env.example
  |- knowledge_base.txt
  |- session_queue_executor_assistant.py
  |- README.md
  |- sessions/
      |- demo-python-agent.json
      |- demo-rag-agent.json
      |- demo-engineering-agent.json
```

---

## 6. 运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day15_session_queue_executor_agent
Copy-Item .env.example .env
python .\session_queue_executor_assistant.py
```

---

## 7. 今天建议你做的实验

建议你做这个实验：

1. 先运行一次脚本
2. 看 `priority_queue`
3. 看 `Execution targets`
4. 确认前 2 个 session 都被更新
5. 打开对应的 `sessions/*.json` 看 history 是否分别增长

你会很直观地看到：

`Day 14 是只推进第一名，Day 15 是开始按队列批量推进前几个。`

---

## 8. 运行时重点看什么

重点看这些输出：

- `Available sessions`
- `Priority queue`
- `Execution targets`
- `Executing session: ...`
- `Structured update plan`
- `Updated learner state`

它们分别表示：

- 当前所有 session 概况
- 模型输出的整体优先级队列
- 本轮准备执行的前几个 session
- 当前正在执行哪个 session
- 针对该 session 的结构化更新方案
- 更新后的新状态

---

## 9. 一句话总结

Day 15 的重点是理解：

`多 session 系统在会排序之后，下一步就是按队列顺序真正执行前几个 session。`
