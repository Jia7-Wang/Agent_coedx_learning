# Day 19 Human Handoff Agent

这是 Day 19 的最小练习项目。

## 目标

理解：

- 为什么 dead letter queue 之后自然会出现 human handoff
- 如何把死信项转成一份人工处理清单
- 为什么人工接管不是“什么都交给人”，而是交付结构化信息
- 为什么 handoff 是自动系统和人工系统之间的重要接口

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\human_handoff_assistant.py
```

## 你会看到什么

- priority queue
- primary execution results
- retry queue
- dead letter queue
- human handoff checklist
- 最终 execution report

## 建议你做的实验

你可以故意让某个 session 进入 dead letter queue，然后观察：

- human handoff checklist 里有没有它
- checklist 是否包含失败原因、检查重点和下一步人工动作
