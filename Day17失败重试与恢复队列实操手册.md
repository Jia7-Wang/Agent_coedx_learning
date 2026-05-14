# Day 17 失败重试与恢复队列实操手册

## 1. 今天的目标

Day 16 你已经做到了：

- Agent 会批量执行前几个 session
- Agent 会输出 execution report
- Agent 会做最小版失败隔离

Day 17 我们继续往前走一步：

`让失败项进入 retry queue，再按更保守的方式尝试恢复。`

也就是说，今天你要理解的是：

`失败不只是要被记录，还要被重新管理。`

---

## 2. 今天和 Day 16 的差别

### Day 16

程序会把失败项记进 execution report，但失败之后就结束了。

### Day 17

程序会：

1. 先执行 primary targets
2. 把失败项收集进 retry queue
3. 对 retry queue 再尝试一次
4. 最后再输出包含 retry 结果的 execution report

这就从“失败记录”升级成了“失败恢复流程”。

---

## 3. 为什么要学 retry queue

真实系统里，失败任务通常不会因为一次失败就永久放弃。

更常见的处理方式是：

- 先记录失败
- 再分类失败
- 对适合恢复的任务重新尝试

retry queue 的意义就是：

`把失败项从主执行流里分离出来，用更保守的方式再处理一次。`

---

## 4. 今天你会学到什么

跑完今天的示例后，你应该能理解：

- 为什么 retry queue 是失败隔离后的自然升级
- 为什么主执行和 retry 执行要分开记录
- 一个最小系统如何统计 primary failure 与 retry recovered
- 为什么真实系统里 retry 往往还会结合退避、上限和告警

---

## 5. 今天的目录结构

```text
day17_retry_queue_agent/
  |- .env.example
  |- knowledge_base.txt
  |- retry_queue_assistant.py
  |- README.md
  |- sessions/
      |- demo-python-agent.json
      |- demo-rag-agent.json
      |- demo-engineering-agent.json
```

---

## 6. 运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day17_retry_queue_agent
Copy-Item .env.example .env
python .\retry_queue_assistant.py
```

如果你想故意触发一个主执行失败，可以在 `.env` 里加一行：

```text
FAIL_SESSION_ID=demo-engineering-agent
```

这样这个 session 会在 primary execution 阶段被故意打断，然后进入 retry queue。

---

## 7. 今天建议你做的实验

建议你做这个实验：

1. 先正常运行一次脚本
2. 再配置 `FAIL_SESSION_ID`
3. 再运行一次
4. 观察：
   - primary results
   - retry queue
   - retry results
   - execution report

这样你会更容易看懂：

`主执行失败 -> 进入 retry queue -> retry 恢复或再次失败`

这条完整链路。

---

## 8. 运行时重点看什么

重点看这些输出：

- `Primary execution results`
- `Retry queue`
- `Retry execution results`
- `Execution report`

它们分别表示：

- 主执行阶段的结果
- 哪些失败项被送进 retry
- retry 阶段是否恢复成功
- 最终整轮执行和恢复的汇总

---

## 9. 一句话总结

Day 17 的重点是理解：

`失败隔离之后，系统下一步就要学会把失败项放进 retry queue，并尝试恢复。`
