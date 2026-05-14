# Day 11 Persistent Session Agent

这是 Day 11 的最小练习项目。

## 目标

理解：

- 为什么 state 不能只存在内存里
- 如何把 learner state 保存到 `state.json`
- 如何在下次运行时恢复之前的 session
- 如何用原子写回减少写文件中断时的损坏风险
- 为什么持久化是很多真实 Agent 系统的基础

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\persistent_session_assistant.py
```

## 你会看到什么

- 是否从文件恢复了旧状态
- 更新前的 learner state
- 知识库检索结果
- 结构化更新方案
- 写回后的 learner state
- `state.json` 已通过原子写回持久化保存

## 建议你做的实验

连续运行两次脚本，对比第二次输出里的：

- `current_stage`
- `today_action`
- `history`

你会更直观地看到“状态跨运行保留”的效果。

## 这次和上一版的区别

现在脚本不是直接覆盖 `state.json`，而是：

1. 先写入同目录临时文件
2. 确保内容真正写入磁盘
3. 再用 `os.replace()` 一次性替换正式文件

这就叫最小原子写回方案。对学习项目来说已经很接近真实工程做法了。
