# Day 19 人工接管工作台实操手册

## 1. 今天的目标

Day 18 你已经做到了：

- 失败项会进入 dead letter queue
- 系统知道什么时候该停止自动重试

Day 19 我们继续往前走一步：

`让 dead letter queue 不只是“停在那里”，而是变成一份可执行的人工接管清单。`

也就是说，今天你要理解的是：

`自动系统和人工系统之间，最好有一层结构化 handoff。`

---

## 2. 今天和 Day 18 的差别

### Day 18

程序会把超过阈值的失败项送进 dead letter queue。

### Day 19

程序会进一步：

1. 读取 dead letter queue
2. 为每个失败项生成人工接管建议
3. 输出 `human handoff checklist`
4. 再把它纳入最终 execution report

这就从“停止自动处理”升级成了“交给人处理的结构化接口”。

---

## 3. 为什么要学 human handoff

如果系统只告诉你“这个任务失败了”，人接手时通常还得重新读很多上下文。

更好的方式是直接给出：

- 失败的是谁
- 为什么失败
- 应该找谁处理
- 人第一步该检查什么
- 之后推荐怎么继续

这就是 human handoff 的意义：

`不是把问题甩给人，而是把问题整理好再交给人。`

---

## 4. 今天你会学到什么

跑完今天的示例后，你应该能理解：

- dead letter queue 和 handoff checklist 的关系
- 为什么 handoff 也应该结构化
- 一个最小系统如何把失败项转成人工任务
- 为什么真实系统里 handoff 往往会进入工单、告警或值班系统

---

## 5. 今天的目录结构

```text
day19_human_handoff_agent/
  |- .env.example
  |- knowledge_base.txt
  |- human_handoff_assistant.py
  |- README.md
  |- sessions/
      |- demo-python-agent.json
      |- demo-rag-agent.json
      |- demo-engineering-agent.json
```

---

## 6. 运行方式

```powershell
cd d:\PythonProjects\Agent_coedx_learning\day19_human_handoff_agent
Copy-Item .env.example .env
python .\human_handoff_assistant.py
```

如果你想强制产生 dead letter queue，可以参考 Day18 的方式在 `.env` 里加：

```text
FAIL_SESSION_ID=demo-engineering-agent
FAIL_ON_RETRY=true
MAX_RETRY_COUNT=1
```

---

## 7. 今天建议你做的实验

建议你做这个实验：

1. 让某个 session 进入 dead letter queue
2. 观察 `Human handoff checklist`
3. 看 checklist 里是否包含：
   - failure_reason
   - human_owner_hint
   - first_manual_check
   - recommended_next_step

这样你会更容易体会：

`handoff 的重点不是“交出去”，而是“交得清楚”。`

---

## 8. 运行时重点看什么

重点看这些输出：

- `Dead letter queue`
- `Human handoff checklist`
- `Execution report`

它们分别表示：

- 哪些任务已停止自动恢复
- 这些失败任务该如何交给人处理
- 整轮自动执行和人工接管的汇总结果

---

## 9. 一句话总结

Day 19 的重点是理解：

`当任务进入 dead letter queue 后，下一步应该把它们转成结构化的人工接管清单，而不是简单停在那里。`
