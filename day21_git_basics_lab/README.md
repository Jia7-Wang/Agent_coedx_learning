# Day 21 Git Basics Lab

这是 Day 21 的最小练习项目。

## 目标

理解：

- `git status` 在看什么
- `git diff` 在看什么
- `git add` 和 `git commit` 的区别
- 为什么提交前应该先看改动

## 运行方式

先运行脚本：

```powershell
python .\greeting_agent.py
```

如果你当前目录还不是 Git 仓库，先在项目根目录执行：

```powershell
git init
```

然后在仓库根目录里练这些命令：

```powershell
git status
git diff
git add day21_git_basics_lab/greeting_agent.py
git status
git commit -m "day21: update git basics lab greeting script"
git log --oneline -n 5
```

## 建议你观察什么

- 修改文件后，`git status` 怎么变
- `git diff` 是否能清楚显示你改的行
- `git add` 后文件状态是否变化
- `git commit` 后历史里是否有新记录

## 小提醒

- 不要把 `.env` 提交上去
- 提交前尽量先看 `git diff`
- 新手先多用 `git add <file>`，少用无脑 `git add .`
