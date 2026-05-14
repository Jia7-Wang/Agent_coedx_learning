# Day 24 Git合并与冲突实操手册

## 1. 今天的目标

Day 23 你已经练过了：

- 新建分支
- 切换分支
- 在分支上修改文件
- 切回主分支观察差异

Day 24 的主题是：

`merge 和 conflict`

今天你要理解的是：

- 分支不是永远分开的
- 做完功能后，通常要把分支合并回主线
- 如果两边改了同一个地方，就可能发生冲突

---

## 2. 今天和 Day 23 的差别

### Day 23

你主要在体验：

- 分支隔离
- 不同分支可以有不同内容

### Day 24

你主要在体验：

1. 把功能分支合并回主分支
2. 什么情况下会自动合并成功
3. 什么情况下会产生冲突
4. 冲突时 Git 为什么不替你直接决定

今天的核心不是“背命令”，而是：

`理解合并本质上是在协调两条开发线。`

---

## 3. 今天你会学到什么

跑完今天的练习后，你应该能理解：

- `git merge` 是在做什么
- 什么叫“自动合并”
- 什么叫“冲突 conflict”
- 冲突标记长什么样
- 为什么解决冲突之后还要重新提交

---

## 4. 今天的目录结构

```text
day24_git_merge_conflict_lab/
  |- merge_story.txt
  |- merge_demo.py
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
python .\day24_git_merge_conflict_lab\merge_demo.py
```

### 第二步：先把 Day24 练习目录纳入 Git

```powershell
git add day24_git_merge_conflict_lab
git commit -m "day24: add git merge conflict practice lab"
```

### 第三步：新建功能分支

```powershell
git switch -c feature/day24-merge-practice
```

### 第四步：在功能分支修改文件并提交

建议你改：

- `day24_git_merge_conflict_lab/merge_story.txt`

例如把某一行改成：

```text
This line was updated on the feature branch.
```

然后执行：

```powershell
git add day24_git_merge_conflict_lab/merge_story.txt
git commit -m "day24: update merge story on feature branch"
```

### 第五步：切回主分支

```powershell
git switch master
```

如果你的主分支是 `main`，就用 `main`。

### 第六步：在主分支改同一个文件、同一行

例如改成：

```text
This line was updated on the master branch.
```

然后执行：

```powershell
git add day24_git_merge_conflict_lab/merge_story.txt
git commit -m "day24: update merge story on master branch"
```

### 第七步：尝试合并功能分支

```powershell
git merge feature/day24-merge-practice
```

如果你刚好改的是同一行，很可能会出现冲突。

### 第八步：观察冲突标记

这时打开：

- `day24_git_merge_conflict_lab/merge_story.txt`

你通常会看到类似：

```text
<<<<<<< HEAD
This line was updated on the master branch.
=======
This line was updated on the feature branch.
>>>>>>> feature/day24-merge-practice
```

这表示：

- 上半段是当前分支版本
- 下半段是要合并进来的分支版本

### 第九步：手动解决冲突

你要自己决定最终保留什么内容。

比如你可以改成：

```text
This line was updated on both master and feature branches, then manually resolved.
```

并且删掉那些：

- `<<<<<<<`
- `=======`
- `>>>>>>>`

### 第十步：解决后重新 add 和 commit

```powershell
git add day24_git_merge_conflict_lab/merge_story.txt
git commit -m "day24: resolve merge conflict in merge story"
```

### 第十一步：查看历史

```powershell
git log --oneline -n 8
```

你要观察：

- 冲突解决之后，历史里会出现新的提交
- 这表示你已经完成了一次手动合并

---

## 6. 今天建议你重点观察什么

### 观察 1：自动合并和冲突的区别

如果两边改的不是同一处，Git 往往能自动合并。

如果两边改的是同一行，Git 通常无法替你判断保留哪个版本，就会冲突。

### 观察 2：冲突标记长什么样

这是 Day24 最重要的可视化信号。

你以后在真实项目里看到：

- `<<<<<<<`
- `=======`
- `>>>>>>>`

就要知道：

`这是 Git 在告诉你：这里需要人来决定。`

### 观察 3：为什么冲突解决后还要 commit

因为：

- 冲突解决不是自动完成的
- 是你手工做出了最终决定
- 所以这个最终决定也需要进入 Git 历史

---

## 7. 今天最容易卡住的点

### 1. 以为 merge 一定成功

不是。

merge 只有在 Git 能清楚判断如何组合两边改动时才会自动成功。

### 2. 看到冲突标记就慌

其实这些标记只是让你看清：

- 当前分支内容
- 目标分支内容

你真正要做的只是：

`决定最后保留什么文本`

### 3. 解决完冲突忘了 add 和 commit

这一步很常见。

要记住：

```powershell
git add <resolved-file>
git commit -m "..."
```

才算真正完成冲突解决。

---

## 8. 一句话总结

Day 24 的重点是理解：

`Git merge 是在尝试合并两条开发线，而 conflict 则表示 Git 已经把选择权交还给人。`
