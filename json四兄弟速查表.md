# JSON 四兄弟速查表

## 1. 最短记忆版

- `json.load()`：从文件读 JSON
- `json.loads()`：从字符串读 JSON
- `json.dump()`：把 JSON 写入文件
- `json.dumps()`：把 JSON 变成字符串

你可以直接记成：

- `load / loads`：读进来
- `dump / dumps`：吐出去

---

## 2. `load()` 和 `loads()` 的区别

### `json.load()`

从**文件对象**里读取 JSON。

例子：

```python
import json

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
```

意思是：

`从文件里读取 JSON，并转成 Python 对象`

---

### `json.loads()`

从**字符串**里读取 JSON。

例子：

```python
import json

text = '{"name": "Tom", "age": 18}'
data = json.loads(text)
```

意思是：

`把 JSON 字符串解析成 Python 对象`

---

## 3. `dump()` 和 `dumps()` 的区别

### `json.dump()`

把 Python 对象直接写进文件。

例子：

```python
import json

data = {"name": "Tom", "age": 18}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

意思是：

`把 Python 对象写成 JSON 文件`

---

### `json.dumps()`

把 Python 对象转成字符串。

例子：

```python
import json

data = {"name": "Tom", "age": 18}
text = json.dumps(data, ensure_ascii=False)
```

意思是：

`把 Python 对象变成 JSON 字符串`

---

## 4. 一张对照表

| 函数 | 输入 | 输出 | 常见场景 |
|------|------|------|----------|
| `json.load()` | 文件对象 | Python 对象 | 从 `.json` 文件读取 |
| `json.loads()` | 字符串 | Python 对象 | 解析模型返回的 JSON 文本 |
| `json.dump()` | Python 对象 | 写入文件 | 保存 JSON 文件 |
| `json.dumps()` | Python 对象 | 字符串 | 打印、传接口、发给模型 |

---

## 5. 你当前代码里的真实例子

### Day 2

在 [extract_learning_profile.py](</d:/PythonProjects/Agent_coedx_learning/day2_structured_output/extract_learning_profile.py>) 里：

```python
parsed = json.loads(json_text)
```

意思是：

`把模型返回的 JSON 字符串解析成 Python 字典`

---

### Day 3

在 Day 3 脚本里常见这种写法：

```python
json.dumps(tool_result, ensure_ascii=False, indent=2)
```

意思是：

`把 Python 字典转成 JSON 字符串，方便打印或发回模型`

---

## 6. 新手最容易混淆的地方

### `load` vs `loads`

- `load`：读文件
- `loads`：读字符串

你可以把 `loads` 里的 `s` 理解成：

`string`

---

### `dump` vs `dumps`

- `dump`：写文件
- `dumps`：变字符串

---

## 7. 最短例子

### 字符串转 Python

```python
import json

text = '{"level": "beginner"}'
data = json.loads(text)
print(data["level"])
```

---

### Python 转字符串

```python
import json

data = {"level": "beginner"}
text = json.dumps(data)
print(text)
```

---

### Python 写入文件

```python
import json

data = {"level": "beginner"}

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

### 文件读回 Python

```python
import json

with open("result.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(data["level"])
```

---

## 8. 一句话总结

- `load`：文件 -> Python
- `loads`：字符串 -> Python
- `dump`：Python -> 文件
- `dumps`：Python -> 字符串
