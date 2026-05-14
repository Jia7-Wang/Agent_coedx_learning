# Day 3 Tool Calling

这是 Day 3 的最小练习项目。

## 目标

理解工具调用闭环：

- 模型决定要不要调用工具
- 程序执行工具
- 程序把工具结果返回模型
- 模型生成最终答案

## 运行步骤

1. 复制 `.env.example` 为 `.env`
2. 填入你的 API 配置
3. 运行：

```powershell
python .\simple_tool_calling.py
```

4. 想继续练“模型在多个工具间做选择”，再运行：

```powershell
python .\multi_tool_routing.py
```

5. 想看更接近真实项目的“带校验、带异常处理、带日志”的版本，再运行：

```powershell
python .\engineering_tool_calling.py
```

## 注意

如果中转 API 不支持标准 Tool Calling，也没关系。  
这一步主要是帮助你理解 Agent 的核心工作方式。
