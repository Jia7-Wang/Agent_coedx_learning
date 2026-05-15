# Git学习项目日常操作速查表

## 1. 这份速查表怎么用

这份表不是讲原理为主，而是给你每天练项目时直接照着执行的。

适用场景：

- 每天开始新一天练习
- 写完代码准备提交
- 想推到 GitHub
- 想把当天分支合并回 `master`

---

## 2. 你的推荐工作流

对你现在这个学习项目，最推荐的流程是：

`master 放稳定结果，feature 分支上做当天练习。`

也就是：

1. 先回 `master`
2. 拉最新内容
3. 新建当天分支
4. 在分支上改代码
5. 提交并推送
6. 确认没问题后再合并回 `master`

---

## 3. 每天开始时怎么做

```powershell
git switch master
git pull
git switch -c feature/day26-fastapi-basics
```

如果是下一天，就把分支名换掉，比如：

```powershell
git switch -c feature/day27-pydantic-basics
git switch -c feature/day28-config-settings
```

---

## 4. 分支怎么命名

推荐固定用这 3 类：

- `feature/...`：新功能、新练习、新内容
- `fix/...`：修 bug、修错误、修配置
- `docs/...`：只改文档、手册、README

推荐命名示例：

```text
feature/day26-fastapi-basics
feature/day27-pydantic-basics
fix/day26-health-endpoint
docs/day25-pr-notes
```

原则：

- 带 `dayXX`
- 用英文短词描述主题
- 一天一个主分支最清楚

---

## 5. 写完后怎么检查

先看状态：

```powershell
git status
```

再看改了什么：

```powershell
git diff
```

如果你已经 `git add` 过了，想看“准备提交的内容”：

```powershell
git diff --staged
```

---

## 6. 提交当天内容

最常用流程：

```powershell
git add .
git commit -m "day26: complete fastapi basics lab"
```

更稳一点的做法是先看状态再提交：

```powershell
git status
git add .
git diff --staged
git commit -m "day26: complete fastapi basics lab"
```

---

## 7. commit message 怎么写

推荐格式：

```text
dayXX: 动词 + 本次改动
```

示例：

```text
day26: complete fastapi basics lab
day26: add health endpoint demo
day26: update fastapi practice notes
day27: add pydantic request model
```

常见动词：

- `add`
- `update`
- `complete`
- `improve`
- `fix`

---

## 8. 怎么推到 GitHub

第一次把新分支推上去：

```powershell
git push -u origin feature/day26-fastapi-basics
```

以后这个分支再推送，通常直接：

```powershell
git push
```

---

## 9. 怎么合并回 master

如果你已经确认当天内容没问题，可以这样合并：

```powershell
git switch master
git pull
git merge feature/day26-fastapi-basics
git push
```

合并完成后，如果这个分支后面不用了，可以删掉本地分支：

```powershell
git branch -d feature/day26-fastapi-basics
```

如果远程分支也想删掉：

```powershell
git push origin --delete feature/day26-fastapi-basics
```

---

## 10. 最小日常命令清单

你现在最常用的其实就这些：

```powershell
git status
git diff
git add .
git diff --staged
git commit -m "..."
git push
git pull
git switch master
git switch -c feature/dayXX-topic
git merge feature/dayXX-topic
git log --oneline -n 5
```

---

## 11. 常见场景速用

### 场景 1：我今天要开始新一天练习

```powershell
git switch master
git pull
git switch -c feature/dayXX-topic
```

### 场景 2：我改完了，想提交

```powershell
git status
git diff
git add .
git diff --staged
git commit -m "dayXX: ..."
```

### 场景 3：我提交完了，想上传 GitHub

第一次推这个分支：

```powershell
git push -u origin feature/dayXX-topic
```

后续继续推：

```powershell
git push
```

### 场景 4：我今天内容完成了，想并回 master

```powershell
git switch master
git pull
git merge feature/dayXX-topic
git push
```

---

## 12. 你现在最该避免的几个坑

### 1. 直接在 `master` 上乱改

可以改，但不推荐。

因为后面你会越来越难分清：

- 哪天改了什么
- 哪次练习对应哪个提交
- 哪些内容还没整理好

### 2. 不看 `git diff` 就直接提交

这很容易把：

- 临时调试代码
- 不该提交的文件
- 无关改动

一起带进去。

### 3. 把 `.env` 提交上去

原则上：

- `.env.example` 可以提交
- `.env` 不应该提交

### 4. 一次 commit 太大

最好保持：

`一次提交，只表达一个清楚的小目标。`

---

## 13. 一套你可以每天照抄的模板

```powershell
git switch master
git pull
git switch -c feature/dayXX-topic

# 开始改代码 / 文档

git status
git diff
git add .
git diff --staged
git commit -m "dayXX: ..."
git push -u origin feature/dayXX-topic
```

如果当天结束并准备合并：

```powershell
git switch master
git pull
git merge feature/dayXX-topic
git push
```

---

## 14. 一句话总结

你现在最适合的 Git 节奏就是：

`每天先开分支，在分支上完成练习，提交并推送，确认稳定后再合并回 master。`
