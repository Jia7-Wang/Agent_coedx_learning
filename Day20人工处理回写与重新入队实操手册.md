# Day 20 人工处理回写与重新入队实操手册

## 1. 今天的目标

Day 19 你已经做到了：
- 失败项会进入 `dead letter queue`
- 系统会生成 `human handoff checklist`

Day 20 我们继续往前走一步：

`让人工接管不只停在“给出清单”，而是把人工处理结论真正写回 session，并决定任务是重新入队还是关闭。`

也就是说，今天你要理解的是：

`人工系统和自动系统之间，不只是交接，还要有“处理结果回流”。`

---

## 2. 今天和 Day 19 的差别

### Day 19

程序会：

1. 读取 `dead letter queue`
2. 生成 `human handoff checklist`
3. 把失败任务整理成可读的人工作业单

### Day 20

程序会再往前一步：

1. 读取 `human handoff checklist`
2. 生成一份“人工处理决定”
3. 把人工决定写回对应的 session
4. 明确标记：
   - 哪些任务 `ready_for_requeue`
   - 哪些任务 `closed_by_human`
5. 再把这些结果纳入最终 `execution report`

---

## 3. 为什么要学人工处理回写

如果系统只会把任务交给人，但不知道人后来怎么处理了，就会出现几个问题：

- 任务虽然被看过，但自动系统不知道结果
- 下次运行时，不知道这个任务还该不该继续排队
- `dead letter queue` 里的任务会越堆越多

更好的方式是把人工结论也结构化下来，例如：

- 这个任务是否值得继续
- 是否已经修复，适合重新入队
- 是否当前先关闭或暂停
- 人工结论是什么

这就是 Day 20 的意义：

`不是只把失败任务交给人，而是让人的处理结果重新回到系统里。`

---

## 4. 今天你会学到什么

跑完今天的示例后，你应该能理解：

- `human handoff checklist` 和“人工处理决定”的关系
- 为什么 `requeue` 和 `close` 是两种不同的系统分支
- 如何把人工结论写回 session state
- 为什么人工处理结果也应该进入统一 report

---

## 5. 今天的目录结构

```text
day20_human_resolution_agent/
  |- .env.example
  |- knowledge_base.txt
  |- human_resolution_assistant.py
  |- README.md
  |- sessions/
      |- demo-python-agent.json
      |- demo-rag-agent.json
      |- demo-engineering-agent.json
```

---

## 6. 运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day20_human_resolution_agent
Copy-Item .env.example .env
python .\human_resolution_assistant.py
```

如果你想稳定触发一条“失败 -> dead letter -> handoff -> human resolution”的主线，可以先在 `.env` 里保留：

```text
FAIL_SESSION_ID=demo-engineering-agent
FAIL_ON_RETRY=true
MAX_RETRY_COUNT=1
HUMAN_DECISION_PREFERENCE=balanced
```

---

## 7. 今天建议你做的实验

建议你重点观察这几个输出：

- `Human handoff checklist`
- `Human resolution decisions`
- `Applied human resolutions`
- `Requeue candidates`
- `Closed items`
- `Execution report`

你要看清楚的是：

1. 哪个任务先进入 `dead letter queue`
2. 它后来有没有进入人工接管清单
3. 人工处理决定是 `requeue` 还是 `close`
4. 这个决定有没有真的回写到 session 文件

---

## 8. 运行时重点看什么

重点看这几类状态变化：

- 自动系统在哪里停下来
- 人工系统给出了什么决定
- 决定回写后，session 是不是出现了新的 `status`
- 下一轮自动系统会不会把它重新入队

你会看到两个关键状态：

- `ready_for_requeue`
- `closed_by_human`

它们分别表示：

- 这条任务已经拿到人工结论，下一轮可以重新进入自动队列验证
- 这条任务已经被人工确认本轮不再自动推进

---

## 9. 一句话总结

Day 20 的重点是理解：

`人工接管不是流程的终点，人工处理结果还应该结构化回写到系统里，决定任务是重新入队还是关闭。`
