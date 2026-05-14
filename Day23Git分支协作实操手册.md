# Day 23 Git分支协作实操手册

## 1. 今天的目标

Day 21 你已经练过：

- `git init`
- `git status`
- `git add`
- `git commit`
- `git log --oneline`

Day 22 你已经练过：

- `git diff`
- `git diff --staged`
- `.gitignore`

Day 23 开始进入 Git 里更像公司项目的第一步：

`分支 branch`

今天你要理解的是：

`为什么真实项目里，通常不会让你一直在 master / main 上直接改代码。`

---

## 2. 今天和 Day 21、Day 22 的差别

### Day 21 / Day 22

你主要是在练：

- 在当前分支里改文件
- 看改动
- add
- commit

### Day 23

你开始练：

1. 新建分支
2. 切换分支
3. 在分支上改文件
4. 切回主分支观察差异
5. 理解“分支隔离”的意义

今天不是要学复杂的团队流程，而是先建立一个非常关键的心智模型：

`一个功能、一段实验、一处修复，最好在自己的分支里做。`

---

## 3. 今天你会学到什么

跑完今天的练习后，你应该能理解：

- 什么是 branch
- 为什么 branch 像一条独立工作线
- `git switch -c` 是在干什么
- 为什么切换回主分支后，某些文件变化会消失
- 为什么这正是 branch 的价值

---

## 4. 今天的目录结构

```text
day23_git_branch_lab/
  |- branch_story.txt
  |- branch_demo.py
  |- README.md
```

---

## 5. 今天怎么练

先进入仓库根目录：

```powershell
cd d:\PythonProjects\Agent_coedx_learning
```

### 第一步：运行今天的脚本

```powershell
python .\day23_git_branch_lab\branch_demo.py
```

### 第二步：把 Day23 练习目录纳入 Git

```powershell
git add day23_git_branch_lab
git commit -m "day23: add git branch practice lab"
```

### 第三步：查看当前分支

```powershell
git branch
```

你应该能看到当前分支，一般会是：

- `master`

或者：

- `main`

### 第四步：新建并切换分支

```powershell
git switch -c feature/day23-branch-practice
```

这一步的意思是：

- 新建一个分支
- 并且立刻切换过去

### 第五步：在分支上改文件

建议你改：

- `day23_git_branch_lab/branch_story.txt`
- 或 `day23_git_branch_lab/branch_demo.py`

例如：

- 给 `branch_story.txt` 新加一行
- 修改 `branch_demo.py` 的输出内容

### 第六步：查看分支上的改动

```powershell
git status
git diff
```

### 第七步：提交分支改动

```powershell
git add day23_git_branch_lab
git commit -m "day23: update branch practice on feature branch"
```

### 第八步：切回主分支

```powershell
git switch master
```

如果你的主分支叫 `main`，就用：

```powershell
git switch main
```

### 第九步：再看文件内容

现在再去看：

- `day23_git_branch_lab/branch_story.txt`
- 或重新运行：

```powershell
python .\day23_git_branch_lab\branch_demo.py
```

你要观察：

- 你在分支上提交的变化，在主分支上通常看不到

这一步最重要。

因为它能让你真正体会到：

`分支就是一条隔离开的工作线。`

### 第十步：再切回功能分支

```powershell
git switch feature/day23-branch-practice
```

你再看文件内容，会发现：

- 分支上的改动又回来了

---

## 6. 今天建议你重点观察什么

### 观察 1：`git branch`

它在告诉你：

- 当前有哪些分支
- 你现在正站在哪个分支上

### 观察 2：切换分支前后文件内容变化

这是 Day23 最核心的观察点。

你会真正看到：

- 同一个文件
- 在不同分支上可以长得不一样

### 观察 3：为什么团队开发要用分支

因为这样可以做到：

- 你在自己分支里实验
- 不会直接污染主分支
- 功能做完再考虑合并

---

## 7. 今天最容易卡住的点

### 1. 忘了自己当前在哪个分支

解决方法：

```powershell
git branch
git status
```

### 2. 改了文件却切不过去分支

这通常是因为：

- 当前工作区还有未处理改动

先提交，或者先清理状态，再切分支。

### 3. 切回主分支后，以为文件“丢了”

不是丢了。

而是：

`那份改动只存在于你刚才那个功能分支上。`

这正是分支隔离的意义。

---

## 8. 一句话总结

Day 23 的重点是理解：

`Git 分支不是额外复杂度，而是让你能在不干扰主线的前提下独立开发、实验和提交改动。`
