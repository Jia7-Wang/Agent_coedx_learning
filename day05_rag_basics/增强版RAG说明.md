# 增强版 RAG 说明

## 1. 这个版本比最小版多了什么

`enhanced_rag_demo.py` 相比 `simple_rag_demo.py`，主要多了 3 个能力：

- 给每个 chunk 编号
- 输出每个命中 chunk 的分数
- 展示命中的关键词，并尽量让最终回答引用 chunk 编号

---

## 2. 为什么这很重要

最小版 RAG 只能让你看到：

- 哪些块被检索到了

增强版 RAG 让你进一步看到：

- 为什么会命中这些块
- 每个块的相关性分数是多少
- 最终回答大致引用了哪些块

这就是 RAG 里非常重要的“可解释性”。

---

## 3. 你运行时重点看什么

运行：

```powershell
python .\enhanced_rag_demo.py
```

重点看：

- `Loaded chunks with ids`
- `Top matched chunks with scores`
- `matched_keywords`
- `Final answer with references`

---

## 4. 一句话总结

`最小版在学检索骨架，增强版在学可解释 RAG。`
