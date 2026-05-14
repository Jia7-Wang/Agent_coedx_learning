# Day 25 PR And Code Review Lab

这是 Day 25 的最小练习项目。

## 目标

理解：

- 什么是 PR
- 什么是 Code Review
- 为什么一次改动最好聚焦一个点
- PR 描述通常应该写什么

## 建议练习顺序

```powershell
python .\day25_pr_review_lab\simple_agent_api.py
git add day25_pr_review_lab
git commit -m "day25: add pr and code review practice lab"
git switch -c feature/day25-pr-practice
```

然后做一个小改动，再执行：

```powershell
git diff
git add day25_pr_review_lab
git diff --staged
git commit -m "day25: improve simple agent api response message"
```

最后补完：

- `day25_pr_review_lab/change_summary.md`

把它当作你这次改动的“假想 PR 描述”。
