# Day 25 PR与Code Review意识实操手册

## 1. 今天的目标

Day 21 到 Day 24 你已经练过：

- `git init`
- `git status`
- `git add`
- `git commit`
- `git diff`
- `git diff --staged`
- `git branch`
- `git switch`
- `git merge`
- `conflict`

Day 25 开始补一件“公司项目里非常重要，但新手最容易忽略”的事：

`PR（Pull Request）和 Code Review 意识`

今天你不一定需要真的把代码推到 GitHub 或 GitLab，但你要开始理解：

- 为什么不是改完就直接 merge
- 为什么改动要先让别人看
- 为什么 PR 描述和提交说明一样重要

---

## 2. 今天和前几天的差别

### Day 21 - Day 24

你主要在练：

- Git 命令本身怎么用
- 分支怎么切
- 合并冲突怎么处理

### Day 25

你开始练：

1. 如何描述一段改动
2. Review 时别人通常会看什么
3. 为什么一次改动最好单一、清晰、可解释
4. 什么样的 PR 更容易被接受

今天的核心不是技术命令，而是工程协作意识。

---

## 3. 今天你会学到什么

跑完今天的练习后，你应该能理解：

- 什么是 PR
- 什么是 Code Review
- PR 描述通常要写什么
- Review 时常见关注点有哪些
- 为什么“我自己知道我改了什么”还不够

---

## 4. 先把几个核心概念讲清楚

### 什么是 PR

PR 是 `Pull Request`，你可以先把它理解成：

`我做完了一组改动，现在正式请求别人来看、讨论、检查，并决定要不要合并。`

它不只是“提交代码”，更像是一次带说明的交接。

在公司里，很多代码不是“写完就直接进主分支”，而是先通过 PR 让团队看到：

- 你改了什么
- 你为什么要这样改
- 这次改动影响了哪里
- 别人应该重点检查什么

所以 PR 的本质是：

`把代码改动变成一个可以被团队理解和审核的协作单元。`

### 什么是 Code Review

Code Review 就是别人在合并前先看你的改动。

它的目标通常不是挑刺，也不是证明“谁更厉害”，而是尽量提前发现问题，比如：

- 明显 bug
- 边界情况没处理
- 命名不清楚
- 改动范围过大
- 实现虽然能跑，但后面难维护

你可以把 review 理解成：

`在问题进入主分支之前，先让团队一起做一次低成本检查。`

### PR 描述通常写什么

一个最小可用的 PR 描述，通常至少回答 4 个问题：

1. 这次改了什么
2. 为什么要改
3. 怎么验证
4. 还有什么没覆盖到

你可以直接套下面这个思路：

- `What`：改了哪些文件、功能、文案或逻辑
- `Why`：这次改动要解决什么问题
- `How to verify`： reviewer 怎么快速验证
- `Known gaps`：还有哪些没做、没测、暂时不处理

这也是为什么今天目录里专门放了 [change_summary.md](/D:/PythonProjects/Agent_coedx_learning/day25_pr_review_lab/change_summary.md)，它本质上就是在练这种表达能力。

### Review 时常见关注点有哪些

review 的时候，别人通常不会只看“能不能运行”，还会看：

- 这次改动是不是足够小，能不能快速看懂
- 命名是否清楚
- 逻辑是否容易读
- 有没有影响旧功能
- 有没有漏掉错误处理
- 有没有明显重复代码
- 有没有更简单的实现方式
- 有没有测试、日志或验证说明

对于 Agent 项目，这些关注点还会进一步落到：

- prompt 或状态更新会不会引发意外行为
- structured output 是否稳定
- tool 调用失败时有没有兜底
- session / retry / dead letter queue 的状态是否一致

### 为什么“我自己知道我改了什么”还不够

因为代码协作里最重要的不是“作者脑子里清楚”，而是：

`别人能不能只看你的改动和说明，就快速理解、放心接手、继续维护。`

你自己知道，并不代表 reviewer 知道，也不代表一周后的你自己还能立刻想起来。

如果没有清楚的 PR 描述和小而明确的改动范围，就很容易出现这些问题：

- 别人看不懂，只能来回追问
- review 速度变慢
- 问题藏进主分支后才暴露
- 过几天你自己回头看，也忘了当时为什么这么改

所以真正专业的协作方式，不是“我改完了”，而是：

`我把改动整理成了别人容易理解、容易检查、容易接手的样子。`

---

## 5. 今天的目录结构

```text
day25_pr_review_lab/
  |- change_summary.md
  |- simple_agent_api.py
  |- README.md
```

---

## 6. 今天怎么练

先进入仓库根目录：

```powershell
cd d:\PythonProjects\Agent_coedx_learning
```

### 第一步：运行今天的脚本

```powershell
python .\day25_pr_review_lab\simple_agent_api.py
```

### 第二步：先把 Day25 练习目录纳入 Git

```powershell
git add day25_pr_review_lab
git commit -m "day25: add pr and code review practice lab"
```

### 第三步：新建一个功能分支

```powershell
git switch -c feature/day25-pr-practice
```

### 第四步：做一个非常小的改动

建议改一个非常清晰的小点，例如：

- 修改 `simple_agent_api.py` 中的一行输出
- 在 `change_summary.md` 里补一条“为什么改”

### 第五步：查看改动

```powershell
git diff
git add day25_pr_review_lab
git diff --staged
```

### 第六步：提交

```powershell
git commit -m "day25: improve simple agent api response message"
```

### 第七步：写一份“假想 PR 描述”

打开并完善：

- `day25_pr_review_lab/change_summary.md`

你可以按这个结构写：

1. 这次改了什么
2. 为什么要改
3. 怎么验证
4. 还没覆盖什么

### 第八步：用“review 视角”重新看自己的改动

你要开始尝试问自己：

- 这次改动是不是太大了？
- 别人不看上下文能不能看懂？
- 命名清不清楚？
- 改动有没有副作用？
- 有没有遗漏边界情况？

---

## 7. 今天建议你重点观察什么

### 观察 1：为什么一次改动最好只做一件事

因为如果一次改动同时做太多事：

- review 很难看
- 出问题很难定位
- 提交历史也会变乱

### 观察 2：PR 描述的价值

PR 描述不是形式主义。

它是在帮 reviewer 快速理解：

- 这次改动目标是什么
- 改动范围是什么
- 他应该重点看哪里

### 观察 3：Code Review 不是挑刺

review 更像是在看：

- 有没有 bug 风险
- 有没有边界情况没处理
- 改动是不是足够清楚

---

## 8. 今天最容易卡住的点

### 1. 以为 commit message 就够了

不够。

commit message 很短，通常只够做标题。

PR 描述更像是：

`这次改动的说明书`

### 2. 以为 review 只看代码对不对

真实 review 常常更关注：

- 改动范围是否合理
- 命名是否清楚
- 有没有引入额外复杂度
- 有没有漏掉错误处理

### 3. 以为只有多人协作才需要 review 意识

其实不是。

即使你现在一个人练项目，review 意识也能帮你：

- 改动更清楚
- 提交更有条理
- 后面回头看更轻松

---

## 9. 一句话总结

Day 25 的重点是理解：

`公司项目里的 Git 不只是“我会提交代码”，而是“我能把改动清楚地交给别人理解、检查和合并”。`
