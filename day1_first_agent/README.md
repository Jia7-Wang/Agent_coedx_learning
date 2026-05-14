# Day 1 First Agent

这是你的 Day 1 最小练习项目。

## 目录说明

- `.env.example`：环境变量模板
- `first_model_call.py`：第一次模型调用脚本

## 如果你使用中转 API

请在 `.env` 里同时填写：

```env
OPENAI_API_KEY=你的中转Key
OPENAI_BASE_URL=https://你的中转地址/v1
OPENAI_MODEL=你的中转支持的模型名
```

注意：

- `OPENAI_BASE_URL` 一般要带 `/v1`
- `OPENAI_MODEL` 要写成中转平台实际支持的模型名
- 很多中转更兼容 `chat.completions`，所以 Day 1 脚本已经按这个方式写好了

## 运行步骤

1. 复制模板文件：

```powershell
Copy-Item .env.example .env
```

2. 编辑 `.env`，填入你自己的 API Key。

3. 运行脚本：

```powershell
python .\first_model_call.py
```

## 目标

跑通这一步后，你就完成了：

- 第一次环境变量读取
- 第一次模型调用
- 第一次最小 AI 工程脚本运行
