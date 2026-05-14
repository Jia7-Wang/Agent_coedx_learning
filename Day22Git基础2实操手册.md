# Day 22 Git基础2实操手册

## 1. 今天的目标

Day 21 你已经练过了：

- `git init`
- `git status`
- `git diff`
- `git add`
- `git commit`
- `git log --oneline`

Day 22 不再重复第一天的动作，而是继续往前走，重点练这 4 个真实高频点：

- `git diff`
- `git diff --staged`
- `git log --oneline`
- `.gitignore`

今天你要真正建立的感觉是：

`工作区改动`、`暂存区改动`、`提交历史`、`被忽略文件`

这 4 个东西分别是什么。

---

## 2. 今天和 Day 21 的差别

### Day 21

你主要在练：

- Git 仓库初始化
- 文件从修改到提交的最小闭环

### Day 22

你主要在练：

1. 怎么看“还没 add 的改动”
2. 怎么看“已经 add 但还没 commit 的改动”
3. 怎么看最近提交历史
4. 什么文件应该被 `.gitignore` 忽略

也就是说，今天不只是“会提交”，而是要开始学会：

`在提交前检查自己到底准备交什么。`

---

## 3. 今天你会学到什么

跑完今天的练习后，你应该能理解：

- `git diff` 和 `git diff --staged` 的区别
- `working tree` 和 `staging area` 的区别
- 为什么 `.env` 这种文件一般不能提交
- 为什么提交前最好先看 diff
- 为什么 `git log --oneline` 是最常用的历史查看方式

---

## 4. 今天的目录结构

```text
day22_git_diff_ignore_lab/
  |- .env.example
  |- .gitignore
  |- app_config_demo.py
  |- notes.txt
  |- README.md
```

---

## 5. 今天怎么练

先进入仓库根目录：

```powershell
cd d:\PythonProjects\Agent_coedx_learning
```

### 第一步：运行今天的练习脚本

```powershell
python .\day22_git_diff_ignore_lab\app_config_demo.py
```

### 第二步：先把 Day22 练习目录纳入版本管理

```powershell
git add day22_git_diff_ignore_lab
git status
git commit -m "day22: add git diff and ignore practice lab"
```

### 第三步：修改 2 个已跟踪文件

建议你改：

- `day22_git_diff_ignore_lab/app_config_demo.py`
- `day22_git_diff_ignore_lab/notes.txt`

例如：

- 改一行输出文案
- 在 `notes.txt` 里多加一条 Git 学习笔记

### 第四步：先看工作区 diff

```powershell
git diff
```

你要看清楚：

- 哪些改动只是“改了但还没 add”
- Git 显示的是哪几行变化

### 第五步：只 add 其中一个文件

例如先 add：

```powershell
git add day22_git_diff_ignore_lab/notes.txt
git status
```

这时你应该看到：

- `notes.txt` 进入暂存区
- `app_config_demo.py` 仍然只是工作区修改

### 第六步：分别看两个 diff

```powershell
git diff
git diff --staged
```

你要观察：

- `git diff` 只看还没暂存的改动
- `git diff --staged` 看已经暂存、准备提交的改动

### 第七步：练 `.gitignore`

复制环境文件：

```powershell
Copy-Item .\day22_git_diff_ignore_lab\.env.example .\day22_git_diff_ignore_lab\.env
git status
```

你要观察：

- 如果 `.gitignore` 配置正确，`.env` 不应该出现在 `git status` 里

### 第八步：提交

```powershell
git add day22_git_diff_ignore_lab/app_config_demo.py
git commit -m "day22: practice diff staged and gitignore"
git log --oneline -n 5
```

---

## 6. 今天建议你重点观察什么

重点看这几个状态变化：

### 场景 1：文件改了，但没 add

这时：

- `git diff` 有内容
- `git diff --staged` 没内容

### 场景 2：文件 add 了，但还没 commit

这时：

- `git diff` 只显示未 add 的文件
- `git diff --staged` 显示已 add 的文件

### 场景 3：`.env` 被忽略

这时：

- 你明明新建了 `.env`
- 但 `git status` 不会列出来

这就是 `.gitignore` 在起作用

---

## 7. 今天最容易卡住的点

### 1. `git diff` 和 `git diff --staged` 搞混

记法很简单：

- `git diff`：看工作区，还没 add 的改动
- `git diff --staged`：看暂存区，已经 add 的改动

### 2. 以为 `.gitignore` 能忽略已经被 Git 跟踪的文件

不是这样的。

`.gitignore`` 主要影响的是还没被跟踪的文件。`

### 3. 提交前不看 diff

这是最常见的新手问题。

建议你养成习惯：

```powershell
git diff
git diff --staged
```

看完再 commit。

---

## 8. 一句话总结

Day 22 的重点是理解：

`提交前不只是要会 add 和 commit，更要会区分工作区改动、暂存区改动，以及哪些文件根本不应该被提交。`
