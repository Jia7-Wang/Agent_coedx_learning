# Day 12 多 Session 管理实操手册

## 1. 今天的目标

Day 11 你已经做到了：

- 一个 session 的 state 可以持久化保存
- 下次运行时可以恢复同一个 session

Day 12 我们继续往前走一步：

`让同一个 Agent 能管理多个 session，而不是只维护一个 state.json。`

也就是说，今天你要理解的是：

`真实 Agent 系统面对的往往不是“一个状态对象”，而是“很多不同会话各自有自己的状态”。`

---

## 2. 今天和 Day 11 的差别

### Day 11

程序只管理一个 `state.json`。

### Day 12

程序开始按 `session_id` 区分状态：

- `demo-python-agent` 对应一个状态文件
- `demo-rag-agent` 对应另一个状态文件

它们会：

- 分开读取
- 分开更新
- 分开保存

这就实现了最小版本的多 session 管理。

---

## 3. 为什么要学多 session

只管理一个 session 时，问题不明显。

但一旦出现下面这些场景，就必须区分 session：

- 同一个用户有多个学习目标
- 一个 Agent 同时服务多个用户
- 同一个用户同时做多个不同项目

如果还共用一个状态文件，就会出现：

- 状态互相污染
- history 混在一起
- 无法判断当前在推进哪个任务

一句话总结：

`持久化解决“能记住”，多 session 解决“分别记住谁的状态”。`

---

## 4. 今天你会学到什么

跑完今天的示例后，你应该能理解：

- 为什么 `session_id` 很重要
- 程序如何根据 `session_id` 找到对应状态文件
- 为什么每个 session 都应该有独立的 history
- 为什么真实项目通常会把 session 存到数据库而不是散落文件

---

## 5. 今天的目录结构

```text
day12_multi_session_agent/
  |- .env.example
  |- knowledge_base.txt
  |- multi_session_assistant.py
  |- README.md
  |- sessions/
      |- demo-python-agent.json
      |- demo-rag-agent.json
```

---

## 6. 运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day12_multi_session_agent
Copy-Item .env.example .env
python .\multi_session_assistant.py
```

如果你想切换 session，可以在 `.env` 里额外加一行：

```text
LEARNER_SESSION_ID=demo-rag-agent
```

不加时，程序默认读取 `sessions/` 里排序后的第一个 session。

---

## 7. 今天建议你做的实验

最推荐你做这个小实验：

1. 先用默认 session 跑一次
2. 打开对应的 `sessions/*.json`
3. 再把 `LEARNER_SESSION_ID` 改成另一个 session
4. 再跑一次
5. 对比两个 session 文件里的 `history`

你会看到：

- 每个 session 的历史轨迹独立增长
- 一个 session 的更新不会覆盖另一个 session

这就是“多 session 隔离”的最直观体现。

---

## 8. 运行时重点看什么

重点看这些输出：

- `Session id`
- `Available sessions`
- `State source`
- `State file`
- `Learner state before update`
- `Knowledge tool result`
- `Structured update plan`
- `Updated learner state`

它们分别表示：

- 当前正在操作哪个 session
- 当前目录下有哪些可用 session
- 本次状态是恢复的还是新建的
- 当前 session 对应哪个状态文件
- 更新前状态
- 检索结果
- 模型返回的结构化更新
- 写回后的新状态

---

## 9. 一句话总结

Day 12 的重点是理解：

`一个真实 Agent 往往不是维护一个状态，而是维护很多个按 session_id 隔离的状态。`
