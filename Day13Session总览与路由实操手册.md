# Day 13 Session 总览与路由实操手册

## 1. 今天的目标

Day 12 你已经做到了：

- 一个 Agent 能管理多个 session
- 每个 session 有自己的状态文件和 history

Day 13 我们继续往前走一步：

`让 Agent 先看所有 session 的概况，再决定现在最该进入哪个 session。`

也就是说，今天你要理解的是：

`多 session 之后，系统不仅要会“保存谁”，还要会“先挑谁”。`

---

## 2. 今天和 Day 12 的差别

### Day 12

程序已经能管理多个 session，但当前操作哪个 session，还是靠外部指定或默认选择。

### Day 13

程序会先：

1. 扫描所有 session 文件
2. 生成每个 session 的 overview
3. 把 overview 交给模型判断
4. 选出当前最值得继续推进的 session
5. 再进入这个 session 做状态更新

这就从“多 session 存储”升级成了“多 session 路由”。

---

## 3. 为什么要学 session 路由

如果系统里有很多 session，而你每次都要手动挑，会越来越麻烦。

更真实的需求通常是：

- 哪个 session 最卡？
- 哪个 session 最值得现在推进？
- 哪个 session 和当前总目标最相关？

这就是 session 路由的意义：

`先做全局判断，再决定局部执行。`

---

## 4. 今天你会学到什么

跑完今天的示例后，你应该能理解：

- 什么是 session overview
- 为什么 overview 不能直接等于完整 state
- 为什么路由通常先做“粗判断”，再进入具体 session
- 一个 Agent 如何先选 session，再推进 session

---

## 5. 今天的目录结构

```text
day13_session_router_agent/
  |- .env.example
  |- knowledge_base.txt
  |- session_router_assistant.py
  |- README.md
  |- sessions/
      |- demo-python-agent.json
      |- demo-rag-agent.json
      |- demo-engineering-agent.json
```

---

## 6. 运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day13_session_router_agent
Copy-Item .env.example .env
python .\session_router_assistant.py
```

---

## 7. 今天建议你做的实验

你最应该做这个实验：

1. 先运行一次脚本
2. 看模型选中了哪个 session
3. 修改某个 session 的 `current_blocker`
4. 再运行一次
5. 看模型是否换了选择

这样你会很直观地看到：

`路由决定不是写死的，而是会根据 session 概况变化。`

---

## 8. 运行时重点看什么

重点看这些输出：

- `Available sessions`
- `Knowledge tool result`
- `Routing decision`
- `Selected learner state before update`
- `Structured update plan`
- `Updated learner state`

它们分别表示：

- 当前所有会话的概况
- 知识库对路由判断的支持
- 模型最终选中了哪个 session
- 被选中 session 的原始状态
- 对该 session 的结构化更新方案
- 更新后的新状态

---

## 9. 一句话总结

Day 13 的重点是理解：

`在多 session 系统里，Agent 不只是更新某个 session，还要先看全局 overview，再决定当前最该推进哪个 session。`
