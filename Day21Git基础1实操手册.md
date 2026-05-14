# Day 21 Git基础1实操手册

## 1. 今天的目标

从 Day 21 开始，你的主线不再只是继续堆 Agent 能力，还要开始补公司项目里真实会用到的工程基础。

今天的主题是：

`先把 Git 最基础、最常用的 5 个动作练熟。`

也就是：

- `git status`
- `git diff`
- `git add`
- `git commit`
- `git log --oneline`

今天不是为了把 Git 一次学完，而是先建立最重要的感觉：

`我改了什么 -> Git 看到了什么 -> 我准备提交什么 -> 我真的提交了什么`

---

## 2. 今天和前 20 天的差别

前 20 天你主要在学：

- 模型调用
- 工具调用
- 状态与工作流
- session / queue / retry / dead letter / handoff

从今天开始，你要补的是：

- 如何在真实仓库里修改代码
- 如何查看改动
- 如何把改动提交成一条清晰历史

因为公司项目不是“跑完就结束”，而是：

`写代码 -> 看改动 -> 提交 -> 回看历史 -> 协作`

---

## 3. 今天你会学到什么

跑完今天这套练习后，你应该能理解：

- `working tree` 是什么
- 什么叫“已修改但未暂存”
- 什么叫“已暂存但未提交”
- 为什么提交前要先看 `git diff`
- 为什么 `.env` 不能乱提交

---

## 4. 今天的目录结构

```text
day21_git_basics_lab/
  |- .env.example
  |- .gitignore
  |- greeting_agent.py
  |- README.md
```

---

## 5. 今天怎么练

先进入仓库根目录：

```powershell
cd d:\PythonProjects\Agent_coedx_learning
```

如果你第一次在这个目录练 Git，先初始化仓库：

```powershell
git init
```

初始化完成后，再继续下面的步骤。

然后建议按下面顺序练：

### 第一步：先看当前仓库状态

```powershell
git status
```

你要观察：

- 当前在哪个分支
- 哪些文件被修改了
- 哪些文件还没被 Git 跟踪

### 第二步：运行今天的练习脚本

```powershell
python .\day21_git_basics_lab\greeting_agent.py
```

### 第三步：手动改一个地方

例如你可以改：

- `OWNER_NAME`
- `PROJECT_STAGE`
- `TASKS`
- 输出文字

### 第四步：看改动

```powershell
git diff
```

你要学会看：

- 哪一行被删了
- 哪一行被加了
- 自己到底改了什么

### 第五步：把文件加入暂存区

```powershell
git add day21_git_basics_lab/greeting_agent.py
git status
```

观察：

- 它是不是从“未暂存”变成“已暂存”

### 第六步：提交

```powershell
git commit -m "day21: update git basics lab greeting script"
```

### 第七步：回看历史

```powershell
git log --oneline -n 5
```

你要看到：

- 最新一条 commit 在最上面
- commit message 是否能说明改了什么

---

## 6. 今天建议你做的实验

建议你做这 3 个小实验：

### 实验 1：只改 1 个文件提交一次

目标：

- 体验最干净的一次提交

### 实验 2：改 2 个文件，但只提交 1 个

目标：

- 理解 `git add <file>` 的意义

### 实验 3：提交前先看 diff

目标：

- 养成“提交前先检查自己改了什么”的习惯

---

## 7. 今天运行时重点看什么

重点不是代码输出，而是 Git 的几个状态变化：

- 修改前：仓库是否干净
- 修改后：Git 是否识别出变更
- `git add` 后：文件是否进入暂存区
- `git commit` 后：历史里是否出现新提交

---

## 8. 一句话总结

Day 21 的重点是理解：

`Git 不是只用来“保存代码”的，它是帮你把改动变成清晰、可追踪、可协作历史的工具。`
