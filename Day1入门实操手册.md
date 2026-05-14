# Day 1 入门实操手册

## 1. 今天的目标

今天我们不追求学很多概念，只做 4 件事：

1. 确认 Python 环境可用
2. 学会为项目准备 API Key
3. 跑通第一次模型调用
4. 用 Git 完成第一次本地提交

如果这 4 件事做完，你就已经真正迈出 Agent 开发第一步了。

---

## 2. 你当前的环境情况

根据当前机器环境，我已经帮你确认到这些信息：

- 已安装 `Anaconda`
- 当前终端可用 `python`
- 当前实际生效版本是 `Python 3.13.9`
- 已安装 `openai` Python SDK

注意：

你提到安装了 `Python 3.14`，但当前终端里实际跑起来的是 `Anaconda` 自带的 `Python 3.13.9`。  
这不是错误，只是说明你现在终端优先使用的是 Anaconda 环境。

对我们当前学习来说，这个版本已经足够使用，可以先继续。

---

## 3. 今天你会接触到的最小项目结构

今天我们先用一个很小的目录练习：

```text
day1_first_agent/
  |- .env.example
  |- first_model_call.py
  |- README.md
```

这个目录的目标很简单：

- 放 API Key 模板
- 放第一次模型调用脚本
- 放项目说明

---

## 4. 第一步：准备 API Key

### 你要做什么

你需要准备自己的 `OPENAI_API_KEY`。

### 正确做法

不要把 Key 直接写死进 Python 代码里。  
正确方式是放到环境变量或 `.env` 文件中。

### 今天的做法

我们会在项目目录里放一个 `.env.example` 模板。

你需要自己新建 `.env` 文件，并填写：

```env
OPENAI_API_KEY=你的真实Key或中转Key
OPENAI_BASE_URL=https://你的中转地址/v1
OPENAI_MODEL=gpt-4.1-mini
```

注意：

- `.env.example` 可以提交到仓库
- `.env` 通常不要提交

如果你使用的是官方 API，可以不填 `OPENAI_BASE_URL`。

如果你使用的是中转 API：

- `OPENAI_BASE_URL` 一般需要写成中转服务给你的接口根地址
- 大多数情况下结尾需要包含 `/v1`
- `OPENAI_MODEL` 要填写中转平台真正支持的模型名，而不是想当然写一个名字

---

## 5. 第二步：看懂第一次模型调用脚本

今天的脚本目标只有一个：

`向模型发送一句话，然后拿回回答`

这一步你重点不是背代码，而是理解下面这件事：

1. 代码读取环境变量
2. 创建 OpenAI client
3. 指定模型
4. 发送输入
5. 打印输出结果

如果这一步跑通，就说明：

- 你的 Python 没问题
- 你的 SDK 没问题
- 你的 API Key 生效了
- 你已经完成第一次真实模型调用

---

## 6. 第三步：你今天要亲手执行的命令

下面这些命令，建议你在 VS Code 终端里亲手跑一遍。

### 6.1 进入项目目录

```powershell
cd d:\PythonProjects\Agent_coedx_learning
```

### 6.2 进入练习目录

```powershell
cd .\day1_first_agent\
```

### 6.3 新建 `.env`

你可以直接复制 `.env.example`：

```powershell
Copy-Item .env.example .env
```

然后把 `.env` 里的 Key 改成你自己的。

### 6.4 运行第一次模型调用

```powershell
python .\first_model_call.py
```

如果成功，你会看到模型返回的文字结果。

如果你使用的是中转 API，这个脚本会自动读取：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

并使用兼容性更高的 `chat.completions` 方式调用。

---

## 7. 第四步：完成第一次 Git 提交

今天你不需要推远程仓库，先做一次本地提交就够了。

### 常用命令

```powershell
git init
git status
git add .
git commit -m "docs: add day1 learning materials"
```

### 你今天要理解的重点

- `git init`：初始化仓库
- `git status`：查看状态
- `git add .`：加入暂存区
- `git commit`：提交一次版本记录

---

## 8. 今天最容易卡住的地方

### 8.1 没有 API Key

现象：

- 程序提示找不到 `OPENAI_API_KEY`

解决：

- 检查 `.env` 是否创建
- 检查变量名是否写对

### 8.2 Key 写了但程序还是报错

检查：

- `.env` 是否和脚本在同一目录
- Key 是否有多余空格
- 账号额度或权限是否正常

如果你使用中转 API，还要额外检查：

- `OPENAI_BASE_URL` 是否写对
- 地址末尾是否需要 `/v1`
- 模型名是否是中转平台真实支持的名字
- 该中转是否兼容 OpenAI Python SDK

### 8.3 Python 版本和你想的不一样

你当前终端里优先使用的是：

```text
D:\Users\Giaci\anaconda3\python.exe
```

这个没问题，今天先不需要切环境。

---

## 9. 今天学完你应该会什么

今天结束后，你应该能做到：

- 知道 Agent 开发不是只聊天
- 会准备 API Key
- 会运行第一次模型调用脚本
- 会看懂最基础的 SDK 调用结构
- 会做一次 Git 本地提交

---

## 10. 明天会学什么

Day 2 最适合继续学的是：

- 结构化输出
- 让模型返回 JSON
- 学会把模型输出当程序输入处理

这一步会把你从“会调用模型”推进到“开始像工程师一样使用模型”。

---

## 11. 你现在就可以执行的动作

请按这个顺序继续：

1. 打开 [day1_first_agent/README.md](</d:/PythonProjects/Agent_coedx_learning/day1_first_agent/README.md>)
2. 按说明创建 `.env`
3. 运行 `python .\first_model_call.py`
4. 跑完后把终端报错或结果贴给我

我会继续带你进入下一步，不需要你自己猜。
