# Day 18 死信队列与最大重试次数实操手册

## 1. 今天的目标

Day 17 你已经做到了：

- 失败项会进入 retry queue
- 系统会尝试恢复失败项

Day 18 我们继续往前走一步：

`让系统知道“不是所有失败都应该无限重试”，并把超过阈值的任务送进 dead letter queue。`

也就是说，今天你要理解的是：

`retry queue 解决“再试一次”，dead letter queue 解决“别再盲目重试了”。`

---

## 2. 今天和 Day 17 的差别

### Day 17

失败项进入 retry queue 后，会被再尝试一次。

### Day 18

系统增加了：

1. `retry_count`
2. `MAX_RETRY_COUNT`
3. `dead_letter_queue`

如果某个任务的失败次数超过阈值，就不再继续自动恢复，而是进入死信队列。

---

## 3. 为什么要学 dead letter queue

如果系统对失败项无限重试，会有几个问题：

- 一直卡住资源
- 反复输出同样错误
- 无法及时暴露真正需要人工处理的问题

死信队列的意义就是：

`把“当前不适合继续自动处理”的失败项单独隔离出来。`

---

## 4. 今天你会学到什么

跑完今天的示例后，你应该能理解：

- retry queue 和 dead letter queue 的职责区别
- 为什么系统需要 `retry_count`
- 为什么“无限重试”通常不是好策略
- 一个最小调度系统如何把失败项推进到人工介入边界

---

## 5. 今天的目录结构

```text
day18_dead_letter_queue_agent/
  |- .env.example
  |- knowledge_base.txt
  |- dead_letter_queue_assistant.py
  |- README.md
  |- sessions/
      |- demo-python-agent.json
      |- demo-rag-agent.json
      |- demo-engineering-agent.json
```

---

## 6. 运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day18_dead_letter_queue_agent
Copy-Item .env.example .env
python .\dead_letter_queue_assistant.py
```

如果你想观察死信队列效果，可以在 `.env` 里加：

```text
FAIL_SESSION_ID=demo-engineering-agent
FAIL_ON_RETRY=true
MAX_RETRY_COUNT=1
```

这样某个 session 会：

- primary 失败
- retry 继续失败
- 最终进入 dead letter queue

---

## 7. 今天建议你做的实验

建议你做这个实验：

1. 先正常运行一次脚本
2. 再配置 `FAIL_SESSION_ID`
3. 再配置 `FAIL_ON_RETRY=true`
4. 观察：
   - primary results
   - retry queue
   - retry results
   - dead letter queue
   - execution report

你会更容易看懂：

`失败 -> 重试 -> 仍失败 -> 进入死信队列`

这条完整链路。

---

## 8. 运行时重点看什么

重点看这些输出：

- `Primary execution results`
- `Retry queue`
- `Retry execution results`
- `Dead letter queue`
- `Execution report`

它们分别表示：

- 主执行阶段的结果
- 哪些项进入 retry
- retry 阶段结果
- 哪些项已不再自动重试
- 最终整轮执行与失败处理汇总

---

## 9. 一句话总结

Day 18 的重点是理解：

`失败重试机制继续升级后，系统需要设置最大重试次数，并把超过阈值的失败项送进 dead letter queue。`
