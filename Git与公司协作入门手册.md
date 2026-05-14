# Git 与公司协作入门手册

## 1. 这份文档是干什么的

这份手册是给零基础学习者准备的公司协作入门文档。

目标不是把 Git 讲成一本厚书，而是帮助你快速建立下面这些能力：

- 知道 Git 在公司项目里是干什么的
- 会完成最常见的日常操作
- 知道分支、提交、合并的大致流程
- 知道新人进入项目后应该怎么开始工作
- 知道哪些操作容易踩坑

如果你未来要做 Agent 项目，这份文档同样重要。因为真实工作里，你不是一个人写 demo，而是要在团队代码仓库里协作开发。

---

## 2. 先建立正确认知

### 2.1 Git 是什么

Git 是一个版本控制工具。

你可以把它理解成：

`帮你记录代码历史、支持多人协作、允许回看改动过程的系统`

它解决的问题主要有：

- 谁改了什么
- 什么时候改的
- 为什么改
- 改坏了能不能定位
- 多个人同时开发怎么不互相覆盖

### 2.2 Git 和 GitHub / GitLab 的区别

- `Git`：本地和远程都能工作的版本控制工具
- `GitHub / GitLab`：代码托管平台，方便团队协作、提 Merge Request、做 Code Review

简单记：

- Git 是“工具”
- GitHub / GitLab 是“平台”

### 2.3 为什么公司项目一定会用 Git

因为公司开发通常有这些特点：

- 多人同时开发
- 一个项目持续很多个月甚至很多年
- 每次改动都需要能追踪
- 出 bug 后需要回看历史
- 代码上线前通常要 review

如果没有 Git，这些事情几乎没法规范做。

---

## 3. 你必须先理解的 7 个核心概念

### 3.1 仓库 Repository

仓库就是项目代码所在的地方。

一个仓库通常包含：

- 代码
- 配置文件
- 文档
- 提交历史

你可以把仓库理解成“整个项目的版本空间”。

### 3.2 工作区 Working Directory

工作区就是你电脑上当前看到的项目目录。

你改文件，其实是在改工作区里的内容。

### 3.3 暂存区 Staging Area

暂存区是 commit 前的“待提交清单”。

它的意义是：

- 你可以只提交一部分改动
- 不是所有改动都会自动进入 commit

最常见命令是：

```powershell
git add .
git add app.py
```

### 3.4 提交 Commit

commit 就像一次“带说明的存档”。

一次好的 commit 应该做到：

- 改动范围清楚
- 目标单一
- 信息可读

例如：

```powershell
git commit -m "feat: add weather tool for agent demo"
```

### 3.5 分支 Branch

分支可以理解成一条独立开发线。

它的作用是：

- 让你在不影响主线的情况下开发新功能
- 每个需求、bug 修复都可以独立处理

公司里通常不会让你直接在主分支上改代码。

### 3.6 合并 Merge

当你的分支开发完成后，需要把改动合并回主线。

常见方式：

- 直接 merge
- 通过 `Pull Request` / `Merge Request`

在公司里，通常会走 MR 或 PR 审核流程。

### 3.7 冲突 Conflict

当两个人改了同一段代码，Git 无法自动决定保留哪份内容时，就会产生冲突。

冲突并不可怕，重点是：

- 看懂冲突位置
- 确认应该保留哪部分
- 解决后重新提交

---

## 4. 你每天最常用的 Git 命令

下面这些命令，是你最值得先记住的。

### 4.1 查看状态

```powershell
git status
```

作用：

- 看当前在哪个分支
- 看哪些文件被修改了
- 看哪些文件已经暂存

这是最常用的命令之一。

### 4.2 查看提交历史

```powershell
git log --oneline
```

作用：

- 快速看最近提交
- 看项目历史节奏

### 4.3 添加到暂存区

```powershell
git add .
git add <file>
```

建议：

- 新手尽量多用 `git add <file>`
- 不要每次都无脑 `git add .`

### 4.4 提交

```powershell
git commit -m "feat: add schedule query tool"
```

### 4.5 拉取远程最新代码

```powershell
git pull
```

作用：

- 获取远程仓库最新内容
- 避免你在旧代码上继续开发

### 4.6 推送到远程

```powershell
git push
```

第一次推送新分支时常见写法：

```powershell
git push -u origin <branch-name>
```

### 4.7 新建分支并切换

```powershell
git switch -c feature/add-weather-tool
```

旧写法也常见：

```powershell
git checkout -b feature/add-weather-tool
```

### 4.8 切换分支

```powershell
git switch main
git switch feature/add-weather-tool
```

### 4.9 查看改动

```powershell
git diff
git diff --staged
```

作用：

- 提交前检查自己到底改了什么
- review 自己的代码

---

## 5. 公司项目里最常见的工作流

虽然每家公司细节不同，但对新人最常见的流程通常是这样：

1. 从远程仓库拉代码
2. 切到主分支并更新到最新
3. 新建自己的需求分支
4. 在分支上开发
5. 本地自测
6. 提交 commit
7. 推送分支到远程
8. 发起 PR / MR
9. 等待 Code Review
10. 根据 review 意见修改
11. 通过后合并

你可以把它理解成：

`拉代码 -> 开分支 -> 开发 -> 提交 -> 推送 -> 提 MR -> 修改 -> 合并`

---

## 6. 一个新人进入公司项目后的标准操作流程

这一段非常重要，你以后可以按这个顺序练。

### 第一步：克隆仓库

```powershell
git clone <repo-url>
cd <repo-name>
```

### 第二步：先看项目，而不是急着写代码

进入项目后，先做这些事：

- 看 `README.md`
- 看依赖文件
- 看启动方式
- 看目录结构
- 看 `.env.example` 或配置说明
- 看有没有测试命令

### 第三步：确认主分支名称

常见是：

- `main`
- `master`
- `develop`

你可以用：

```powershell
git branch
git branch -a
```

### 第四步：先同步最新代码

```powershell
git switch main
git pull
```

如果团队主分支不是 `main`，就替换成实际分支名。

### 第五步：为当前任务创建分支

```powershell
git switch -c feature/agent-weather-tool
```

常见分支命名方式：

- `feature/...`：新功能
- `fix/...`：bug 修复
- `refactor/...`：重构
- `docs/...`：文档修改

### 第六步：开发并频繁自检

在开发过程中要反复做这些事：

- 跑服务
- 看日志
- 做最基本测试
- 用 `git diff` 检查改动

### 第七步：提交前自查

提交前至少确认：

- 没有把无关文件一起提交
- 没有把密钥写进代码
- 没有把调试垃圾日志保留太多
- 代码能正常运行

### 第八步：提交并推送

```powershell
git add <files>
git commit -m "feat: add agent weather query tool"
git push -u origin feature/agent-weather-tool
```

### 第九步：发起 MR / PR

在 GitHub 或 GitLab 页面上发起代码合并请求。

通常要写清楚：

- 这次改了什么
- 为什么改
- 如何验证
- 有哪些风险点

### 第十步：根据 review 修改

收到 review 意见后：

- 不要有情绪
- 先理解问题
- 修改代码
- 再提交新的 commit 或按团队规范整理提交

---

## 7. 什么是 Code Review

Code Review 就是别人查看你的代码改动，并给出反馈。

它不是在“挑刺”，本质是在做这些事：

- 帮你发现 bug
- 帮你统一风格
- 帮你检查边界条件
- 帮团队降低线上风险

### Review 时别人最常看什么

- 功能是否正确
- 命名是否清晰
- 边界条件有没有漏
- 异常处理是否合理
- 改动是不是过大
- 有没有不必要的复杂度

### 你该怎么面对 Review

- 把它当成学习机会
- 不要把建议理解成否定你
- 如果不理解，直接问原因
- 改完后再自己检查一遍

---

## 8. 新手最该掌握的 Commit 习惯

### 8.1 一次 commit 只做一件事

坏习惯：

- 一次提交里同时改功能、改样式、改文档、改配置

好习惯：

- 一次提交聚焦一个目标

### 8.2 提交信息要能看懂

推荐格式：

```text
feat: 新功能
fix: 修复问题
docs: 文档修改
refactor: 重构
test: 测试相关
chore: 杂项维护
```

例如：

```powershell
git commit -m "fix: handle missing tool arguments in weather agent"
git commit -m "docs: add setup steps for local development"
```

### 8.3 提交前先看 diff

```powershell
git diff
git diff --staged
```

这一步可以帮你提前发现：

- 多提交了无关文件
- 有调试代码没删
- 有敏感信息误提交

---

## 9. 分支应该怎么用

### 9.1 为什么不要直接在主分支开发

因为这样会带来这些问题：

- 容易把未完成代码推上去
- 不利于 review
- 容易影响别人
- 回滚和定位都更麻烦

### 9.2 正确思路

通常一个需求对应一个分支。

例如：

- `feature/add-rag-retriever`
- `fix/session-state-bug`
- `docs/update-readme`

### 9.3 分支命名建议

尽量做到：

- 简洁
- 可读
- 能看出目的

避免这种名字：

- `aaa`
- `test`
- `new`

---

## 10. 冲突怎么理解

冲突最常见的原因是：

- 你和别人改了同一段代码
- 你本地分支太久没同步主线

### 一个重要原则

冲突不是错误，它只是告诉你：

`Git 无法自动替你做业务判断`

### 解决冲突的大致步骤

1. 看冲突文件
2. 找到冲突标记
3. 判断应该保留哪部分
4. 手动修改文件
5. 再次 `git add`
6. 完成后继续提交

### 新手建议

第一次遇到冲突不要慌，先看清楚：

- 你的改动是什么
- 对方改动是什么
- 最终业务上应该保留什么

如果看不懂，及时问同事，不要硬解。

---

## 11. 这些文件你一定要熟悉

进入一个项目后，建议优先认识这些文件：

- `README.md`
- `.gitignore`
- `.env.example`
- `requirements.txt`
- `pyproject.toml`
- `package.json`
- `docker-compose.yml`
- `Makefile`

### `.gitignore` 是干什么的

它用来告诉 Git 哪些文件不应该提交。

常见不该提交的内容：

- 虚拟环境目录
- 缓存文件
- 编译产物
- 本地日志
- 密钥文件

---

## 12. 公司项目中最容易踩的 Git 坑

### 坑 1：不看 `git status`

后果：

- 不知道自己改了什么
- 不知道当前在哪个分支
- 不知道哪些文件会被提交

### 坑 2：无脑 `git add .`

后果：

- 容易把无关文件一起提交
- 容易把密钥、缓存、日志误提交

### 坑 3：直接在主分支改代码

后果：

- 协作风险很高
- 提交历史混乱
- review 不方便

### 坑 4：commit message 太随意

例如：

- `update`
- `test`
- `fix`

这种提交信息对团队几乎没有帮助。

### 坑 5：长时间不 pull

后果：

- 和主线差距越来越大
- 最后合并时冲突很多

### 坑 6：把敏感信息提交上去

例如：

- API Key
- 数据库密码
- 私有证书

这是非常严重的问题。

### 坑 7：改完不自测就提 MR

这样会直接拖慢 review 效率，也会降低别人对你改动的信任。

---

## 13. Agent 项目里你特别要注意什么

如果你后面做的是 Agent 项目，Git 协作里还要额外注意这些点：

### 13.1 不要提交密钥

像这些内容不要进入仓库：

- `OPENAI_API_KEY`
- 数据库密码
- 第三方平台 token

正确方式是：

- 放进 `.env`
- 提供 `.env.example`
- 在文档里说明需要哪些变量

### 13.2 不要把大量测试数据随便提交

Agent 项目里常见有：

- 长日志
- 评测结果
- 临时对话样本
- 本地缓存

这些内容要判断是否真的需要入库。

### 13.3 提交前注意日志与调试输出

因为 Agent 项目经常打印：

- prompt
- tool input
- tool output
- trace 信息

提交前要注意：

- 不要泄露敏感信息
- 不要留下过多无意义调试日志

### 13.4 需求要拆小

Agent 项目如果一次改动太大，review 会非常困难。

建议：

- 先拆工具层
- 再拆工作流层
- 再拆接口层
- 最后补文档和测试

---

## 14. 你每天最常见的操作模板

下面给你一套可以直接照着练的日常模板。

### 场景 1：开始一个新需求

```powershell
git switch main
git pull
git switch -c feature/my-task
```

### 场景 2：开发中查看状态

```powershell
git status
git diff
```

### 场景 3：提交代码

```powershell
git add <files>
git diff --staged
git commit -m "feat: add my feature"
```

### 场景 4：推送分支

```powershell
git push -u origin feature/my-task
```

### 场景 5：查看最近提交

```powershell
git log --oneline -10
```

---

## 15. 新人至少要形成的工程习惯

你未来如果想更快上手公司项目，建议现在就开始练这些习惯：

- 每次工作前先看 `git status`
- 每次提交前先看 `git diff`
- 每个需求开一个分支
- 每次 commit 只做一件事
- 每次提交流程前先自测
- 每个项目都写基础 `README`
- 不确定时先问，不要凭感觉乱操作

---

## 16. 学习路线建议

如果你是完全新手，我建议你按这个顺序学 Git：

### 第 1 步

先学这 6 个命令：

- `git status`
- `git add`
- `git commit`
- `git log`
- `git pull`
- `git push`

### 第 2 步

再学分支操作：

- `git switch`
- `git switch -c`
- `git branch`

### 第 3 步

再学这些协作能力：

- 看 diff
- 发 PR / MR
- 处理 review
- 解决简单冲突

### 第 4 步

最后再补：

- rebase 概念
- cherry-pick 概念
- stash 概念

这几个进阶内容你现在不用急着深挖，先把基础流程跑顺更重要。

---

## 17. 给你的练习任务

为了让你真正掌握，我建议你亲手练下面这组动作：

### 练习 1

创建一个新目录，初始化 Git 仓库：

```powershell
git init
```

### 练习 2

新建一个 `README.md`，提交第一次 commit。

### 练习 3

新建一个分支，在分支里改一个文件，再提交一次。

### 练习 4

用 `git diff` 看看你到底改了什么。

### 练习 5

尝试写 3 条不同类型的 commit message：

- `feat: ...`
- `fix: ...`
- `docs: ...`

### 练习 6

为你后面的 Agent 学习项目建立统一目录，并且每个小项目都练一次：

- 建分支
- 开发
- 提交
- 写 README

---

## 18. 一句话总结

Git 不是单纯的命令集合，它本质上是公司开发协作的基础设施。

你真正要掌握的不是“背命令”，而是这条工作链路：

`拉代码 -> 开分支 -> 开发 -> 自测 -> 提交 -> 推送 -> Review -> 合并`

只要你把这条链路练熟，后面进入真实项目时会轻松很多。

---

## 19. 下一步最适合补什么

看完这份文档后，最适合接着补的文档有 2 份：

- `Day 1 入门实操手册`
- `90 天详细周计划`

如果你愿意，我下一步可以直接继续帮你生成 `Day 1 入门实操手册`，把 Python、环境配置、第一次模型调用、第一次 Git 提交串成一套可操作流程。
