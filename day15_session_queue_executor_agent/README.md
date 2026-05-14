# Day 15 Session Queue Executor Agent

这是 Day 15 的最小练习项目。

## 目标

理解：

- 为什么只排出优先级队列还不够
- 如何按队列顺序真正推进前几个 session
- 如何让系统从“会排序”升级到“会执行”
- 为什么队列执行器是工作流调度的重要基础

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\session_queue_executor_assistant.py
```

## 你会看到什么

- 当前 session 概览
- 模型输出的 priority queue
- 本次准备执行的 top N session
- 每个被执行 session 的更新前状态
- 每个被执行 session 的结构化更新结果
- 每个被执行 session 的写回结果

## 建议你做的实验

修改某个 session 的：

- `current_blocker`
- `history`
- `current_stage`

再重新运行脚本，观察：

- 队列顺序是否变化
- 实际被执行的前两个 session 是否变化
