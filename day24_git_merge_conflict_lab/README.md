# Day 24 Git Merge Conflict Lab

这是 Day 24 的最小练习项目。

## 目标

理解：

- `git merge` 在做什么
- 什么情况下会冲突
- 冲突标记怎么看
- 为什么解决冲突后还要再次提交

## 建议练习顺序

```powershell
python .\day24_git_merge_conflict_lab\merge_demo.py
git add day24_git_merge_conflict_lab
git commit -m "day24: add git merge conflict practice lab"
git switch -c feature/day24-merge-practice
```

然后在功能分支改 `merge_story.txt`，提交后切回主分支，再改同一行，最后执行：

```powershell
git merge feature/day24-merge-practice
```

如果出现冲突，手动编辑文件，删掉冲突标记，保留最终版本，再执行：

```powershell
git add day24_git_merge_conflict_lab/merge_story.txt
git commit -m "day24: resolve merge conflict in merge story"
```
