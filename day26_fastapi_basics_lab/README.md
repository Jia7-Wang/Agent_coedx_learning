# Day 26 FastAPI Basics Lab

这是 Day 26 的最小 FastAPI 练习项目。

## 目标

理解：

- 什么是最小 API 服务
- 什么是路由
- 什么是 `/health`
- 怎样用 FastAPI 跑起一个本地服务

## 安装依赖

```powershell
pip install -r .\day26_fastapi_basics_lab\requirements.txt
```

## 启动方式 1：推荐

```powershell
uvicorn day26_fastapi_basics_lab.main:app --reload
```

## 启动方式 2：直接运行脚本

```powershell
python .\day26_fastapi_basics_lab\main.py
```

## 访问地址

- Root: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/health`
- Docs: `http://127.0.0.1:8000/docs`

## 今天重点看什么

- `main.py` 里的 `app = FastAPI(...)`
- `@app.get("/")`
- `@app.get("/health")`

你今天先不需要追求复杂接口，只要先建立“脚本 -> 服务”的感觉就够了。
