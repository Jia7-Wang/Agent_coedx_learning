# Day 2 Structured Output

这是 Day 2 的最小练习项目。

## 目标

让模型返回稳定 JSON，并在 Python 中完成解析。

## 运行步骤

1. 复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

2. 编辑 `.env`，填入中转 API 或官方 API 配置。

3. 运行脚本：

```powershell
python .\extract_learning_profile.py
```

## 你会看到什么

- 原始模型输出
- 解析后的 JSON 对象

## 关键学习点

- 结构化输出
- JSON 解析
- 基础容错处理
