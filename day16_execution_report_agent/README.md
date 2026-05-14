# Day 16 Execution Report Agent

这是 Day 16 的最小练习项目。

## 目标

理解：

- 为什么批量执行之后还需要 execution report
- 如何记录每个 session 的执行结果
- 如何让某个 session 失败时不拖垮整轮执行
- 为什么执行报告是调度系统的重要反馈层

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\execution_report_assistant.py
```

## 你会看到什么

- 当前 session 概览
- 模型输出的 priority queue
- 本轮 execution targets
- 每个 session 的执行结果
- 最终 execution report

## 建议你做的实验

你可以故意在一个 session 文件里删掉某个关键字段，观察：

- 这个 session 是否执行失败
- 其他 session 是否还能继续
- 最终 execution report 是否能看出失败原因
