# Day 23 Git Branch Lab

这是 Day 23 的最小练习项目。

## 目标

理解：

- 什么是 branch
- 如何新建并切换分支
- 为什么分支上的改动不会自动出现在主分支

## 建议练习顺序

```powershell
python .\day23_git_branch_lab\branch_demo.py
git add day23_git_branch_lab
git commit -m "day23: add git branch practice lab"
git branch
git switch -c feature/day23-branch-practice
```

然后修改文件，再执行：

```powershell
git status
git diff
git add day23_git_branch_lab
git commit -m "day23: update branch practice on feature branch"
git switch master
```

如果主分支不是 `master`，请改成你的实际主分支名称。

## 重点观察

- `git branch` 的输出
- 切换分支前后文件内容的变化
- 为什么主分支和功能分支可以看到不同版本的同一个文件
