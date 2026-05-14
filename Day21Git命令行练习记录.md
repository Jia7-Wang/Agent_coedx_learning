# Day21 Git 命令行练习记录

## 1. 这份记录是干什么的

这份文档整理了你在 Day21 里实际执行过的 Git 命令、终端里出现的关键输出，以及每一步代表什么。

目标不是只留“命令清单”，而是把这次练习真正变成你以后能回看的学习记录。

---

## 2. 第一次执行 `git status`

### 你执行的命令

```powershell
git status
```

### 终端结果

```powershell
fatal: not a git repository (or any of the parent directories): .git
```

### 这一步说明什么

这不是 Git 坏了，而是当前目录还不是 Git 仓库。

也就是说：

- 这个目录里虽然已经有很多文件
- 但 Git 还没有在这里建立自己的版本管理空间
- 所以它不知道该看谁的状态

### 当时对应的处理

正确动作是先初始化仓库：

```powershell
git init
```

---

## 3. 初始化 Git 仓库

### 执行的命令

```powershell
git init
```

### 终端结果

```powershell
Initialized empty Git repository in D:/PythonProjects/Agent_coedx_learning/.git/
```

### 这一步说明什么

这表示当前目录已经正式变成 Git 仓库了。

你可以把这一步理解成：

`给这个项目装上版本管理能力。`

初始化之后，这个目录里会出现一个隐藏的 `.git/` 目录，Git 的历史和元信息都会放在里面。

---

## 4. 初始化后第一次 `git status`

### 执行的命令

```powershell
git status
```

### 终端结果摘要

```powershell
On branch master

No commits yet

Untracked files:
  ...

nothing added to commit but untracked files present
```

### 这一步说明什么

这一步非常关键，因为你第一次看到 Git 的“初始状态”。

它表示：

- 当前在 `master` 分支
- 仓库已经初始化成功
- 但还没有任何提交历史
- 当前目录里的很多文件 Git 看到了
- 但这些文件还没有被纳入版本管理

这里最重要的词是：

`Untracked files`

意思是：

`文件存在，但 Git 还没开始正式管理它们。`

### 关于中文文件名乱码

终端里你看到很多中文文件名显示成：

```powershell
"90\345\244\251..."
```

这不是文件坏了，而是 Git 在终端里用转义形式显示中文路径。

---

## 5. 第一次执行 `git diff`

### 执行的命令

```powershell
git diff
```

### 终端结果

没有输出。

### 这一步说明什么

这也是正常现象。

因为当时：

- 你还没有修改已经被 Git 跟踪的文件
- 也还没有形成 Git 可比较的历史差异

所以 `git diff` 没有内容可显示。

可以把它理解成：

`Git 现在没有发现“已跟踪文件的内容变化”。`

---

## 6. 修改 `greeting_agent.py` 后再次执行 `git diff`

### 你改动的内容

你把：

```python
"Run git status",
```

改成了：

```python
"Run git status first",
```

### 执行的命令

```powershell
git diff
```

### 终端结果

```powershell
warning: in the working copy of 'day21_git_basics_lab/greeting_agent.py', LF will be replaced by CRLF the next time Git touches it
diff --git a/day21_git_basics_lab/greeting_agent.py b/day21_git_basics_lab/greeting_agent.py
index 4898cf3..85e171f 100644
--- a/day21_git_basics_lab/greeting_agent.py
+++ b/day21_git_basics_lab/greeting_agent.py
@@ -23,7 +23,7 @@ def main() -> None:
     project_stage = os.getenv("PROJECT_STAGE", "day21-git-basics")

     tasks = [
-        "Run git status",
+        "Run git status first",
         "Edit one line in this file",
         "Run git diff",
         "Stage only this file",
```

### 这一步说明什么

这是 Day21 最重要的输出之一。

它说明 Git 已经可以准确告诉你：

- 改的是哪个文件
- 改的是哪一行
- 原来是什么
- 现在变成了什么

也就是：

`git diff` 不是只告诉你“文件变了”，而是告诉你“具体哪一行怎么变了”。`

### 关于 LF / CRLF warning

这一句：

```powershell
LF will be replaced by CRLF
```

在 Windows 上很常见。

它表示：

- 文件当前是 `LF` 换行
- Git 后续处理时可能转成 `CRLF`

这不是错误，Day21 阶段先把它当成“Windows 下常见的换行符提示”即可。

---

## 7. 修改后执行 `git status`

### 执行的命令

```powershell
git status
```

### 终端结果摘要

```powershell
On branch master
Changes not staged for commit:
        modified:   day21_git_basics_lab/greeting_agent.py

Untracked files:
        ...
```

### 这一步说明什么

你第一次看到了：

`modified but not staged`

也就是：

- Git 认识这个文件
- 你修改了它
- 但你还没有 `git add`

这时这个文件处在：

`工作区已修改，但还没进入暂存区`

---

## 8. 执行 `git add day21_git_basics_lab/greeting_agent.py`

### 执行的命令

```powershell
git add day21_git_basics_lab/greeting_agent.py
```

### 终端结果

```powershell
warning: in the working copy of 'day21_git_basics_lab/greeting_agent.py', LF will be replaced by CRLF the next time Git touches it
```

### 这一步说明什么

虽然只看到 warning，但真正发生的动作是：

`greeting_agent.py` 被放进暂存区了。`

`git add` 的本质不是提交，而是：

`告诉 Git：这次提交我准备带上这个文件。`

---

## 9. `git add` 后执行 `git status`

### 执行的命令

```powershell
git status
```

### 终端结果摘要

```powershell
On branch master
Changes to be committed:
        modified:   day21_git_basics_lab/greeting_agent.py

Untracked files:
        ...
```

### 这一步说明什么

这是 Day21 的第一个状态跳转：

从：

`modified but not staged`

变成：

`Changes to be committed`

这说明：

- 文件仍然是修改状态
- 但现在它已经进入暂存区
- 下一次 commit 会把它带进去

---

## 10. 第一次提交修改过的文件

### 执行的命令

```powershell
git commit -m "day21: update git basics lab greeting script"
```

### 终端结果

```powershell
[master a3e284b] day21: update git basics lab greeting script
 1 file changed, 1 insertion(+), 1 deletion(-)
```

### 这一步说明什么

这次提交成功把 `greeting_agent.py` 的那 1 行改动写进了 Git 历史。

这里最重要的是：

- `a3e284b` 是这次提交的短哈希
- `1 insertion(+), 1 deletion(-)` 对应你那一行文本的替换

也就是说：

`git commit` 才是真正把改动写进历史。`

---

## 11. 提交后执行 `git log --oneline -n 5`

### 执行的命令

```powershell
git log --oneline -n 5
```

### 终端结果

```powershell
a3e284b (HEAD -> master) day21: update git basics lab greeting script
19c78d2 day21: update git basics lab greeting script
```

### 这一步说明什么

这说明仓库里已经至少有两条提交历史。

其中：

- 最新的是 `a3e284b`
- `HEAD -> master` 表示你当前就在 `master` 分支的最新提交上

这里你第一次看到了：

`HEAD`

可以先简单理解成：

`我现在站在哪个提交上。`

---

## 12. 提交后再次执行 `git status`

### 执行的命令

```powershell
git status
```

### 终端结果摘要

```powershell
On branch master
Untracked files:
        ...

nothing added to commit but untracked files present
```

### 这一步说明什么

这一步说明：

- `greeting_agent.py` 那个修改已经完全干净了
- 它已经进了 Git 历史
- 当前仓库里剩下的是其他还没被跟踪的文件

这一步能帮助你理解：

`一次 commit 只会提交你 add 进去的那部分，不会顺便处理其他文件。`

---

## 13. 继续 add 三个新文件

### 执行的命令

```powershell
git add day21_git_basics_lab/README.md
git add day21_git_basics_lab/.env.example
git add day21_git_basics_lab/.gitignore
git status
```

### 终端结果摘要

```powershell
Changes to be committed:
        new file:   day21_git_basics_lab/.env.example
        new file:   day21_git_basics_lab/.gitignore
        new file:   day21_git_basics_lab/README.md

Untracked files:
        ...
```

### 这一步说明什么

这里你第一次看到了：

`new file`

它和前面的 `modified` 不一样。

意思是：

- 这些文件以前从来没进过 Git 历史
- 这次是第一次把它们纳入版本控制

也就是说，你现在已经见过两种很重要的情况：

- `modified`：旧文件被修改
- `new file`：新文件第一次加入版本控制

---

## 14. 提交这三个新文件

### 执行的命令

```powershell
git commit -m "day21: add git basics lab support files"
```

### 终端结果

```powershell
[master 6170560] day21: add git basics lab support files
 3 files changed, 54 insertions(+)
 create mode 100644 day21_git_basics_lab/.env.example
 create mode 100644 day21_git_basics_lab/.gitignore
 create mode 100644 day21_git_basics_lab/README.md
```

### 这一步说明什么

这次提交把 3 个新文件正式纳入 Git 历史。

可以理解成：

- 这 3 个文件以前是“Git 不认识”
- 现在已经变成“Git 正式开始管理”

这里的：

```powershell
create mode 100644
```

你现在不用深究，先把它理解成：

`Git 记录：这是新创建并纳入版本管理的普通文件。`

---

## 15. 第二次查看提交历史

### 执行的命令

```powershell
git log --oneline -n 5
```

### 终端结果

```powershell
6170560 (HEAD -> master) day21: add git basics lab support files
a3e284b day21: update git basics lab greeting script
19c78d2 day21: update git basics lab greeting script
```

### 这一步说明什么

你现在的最新提交已经变成：

- `6170560`

而且它就是当前 `HEAD` 所在的位置。

这说明 Git 历史是按时间往前叠加的。

最新提交永远在最上面。

---

## 16. 第二次提交后执行 `git status`

### 执行的命令

```powershell
git status
```

### 终端结果摘要

```powershell
On branch master
Untracked files:
        ...

nothing added to commit but untracked files present
```

### 这一步说明什么

说明你刚才 add 并 commit 的 3 个文件也已经干净了。

也就是说：

- `greeting_agent.py` 已提交
- `README.md`、`.env.example`、`.gitignore` 也已提交
- 剩下没有提交的，都是其他你还没追踪的文件

这一步进一步强化了一个 Git 核心规则：

`Git 只会提交你明确 add 的内容。`

---

## 17. 你在 Day21 里真正学会了什么

到这里，你已经不是只会背命令了，而是真的经历了 Git 的状态变化。

你已经实际见过这些状态：

- `not a git repository`
- `untracked`
- `modified`
- `changes to be committed`
- `committed`

你也已经实际完成了这条链路：

`git init -> git status -> 修改文件 -> git diff -> git add -> git commit -> git log`

这就是 Day21 最重要的最小闭环。

---

## 18. 一句话总结

Day21 里你学到的核心不是“几个 Git 命令”，而是：

`Git 会把你的文件从未跟踪、已修改、已暂存、已提交这几个状态一步步推进，而你要学会看懂它每一步在说什么。`
