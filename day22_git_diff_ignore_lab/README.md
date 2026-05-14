# Day 22 Git Diff And Ignore Lab

这是 Day 22 的最小练习项目。

## 目标

理解：

- `git diff` 和 `git diff --staged` 的区别
- 为什么 `.env` 应该放进 `.gitignore`
- 为什么提交前最好先检查改动

## 练习顺序

1. 先运行脚本
2. 把本目录纳入 Git
3. 修改 `app_config_demo.py` 和 `notes.txt`
4. 用 `git diff` 看工作区改动
5. 只 add 一个文件
6. 再分别看 `git diff` 和 `git diff --staged`
7. 复制 `.env.example` 为 `.env`
8. 用 `git status` 验证 `.env` 是否被忽略

## 建议命令

```powershell
python .\day22_git_diff_ignore_lab\app_config_demo.py
git add day22_git_diff_ignore_lab
git commit -m "day22: add git diff and ignore practice lab"
git diff
git add day22_git_diff_ignore_lab/notes.txt
git diff
git diff --staged
Copy-Item .\day22_git_diff_ignore_lab\.env.example .\day22_git_diff_ignore_lab\.env
git status
```
