# 第13章：Python 实现最小 Agent —— 从零开始，动手写一个

> **本章目标**：用 Python 从零实现一个能工作的最小 Agent。基于前 12 章学到的原理，把"思考→行动→观察"的循环变成真实代码。这是整个教程最激动人心的一章——你将亲手创造出自己的 Agent！
>
> **难度**：⭐⭐⭐⭐⭐ 实战
>
> **无需安装额外依赖**——只用 Python 标准库

---

## 13.1 设计目标

我们要实现的 Agent 叫 **MiniAgent**，它能：

1. 接收用户输入
2. 调用 AI 获取回复
3. 解析 AI 的工具调用
4. 执行工具并返回结果
5. 循环直到任务完成

对应 claw-code 的核心模块：

| claw-code 组件 | MiniAgent 对应 |
|---------------|---------------|
| ConversationRuntime | `MiniAgent` 类 |
| Agent Loop (`run_turn`) | `run()` 方法 |
| ToolExecutor | `execute_tool()` 方法 |
| StaticToolExecutor | 工具注册表 `tools` 字典 |
| PermissionPolicy | 简化为"全部允许" |
| Session | `messages` 列表 |
| ContentBlock | 字典（`{"type": "text", ...}`） |

---

## 13.2 第一步：消息模型

```python
# --- 消息模型 ---

def user_message(text):
    """创建用户消息"""
    return {"role": "user", "content": text}

def assistant_message(text):
    """创建 AI 消息（纯文字）"""
    return {"role": "assistant", "content": text}

def tool_result_message(tool_use_id, output):
    """创建工具结果消息"""
    return {"role": "user", "content": [{
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": output,
    }]}
```

> claw-code 用 `ConversationMessage` 和 `ContentBlock` 两个结构体，我们用 Python 字典来简化。效果一样，但代码更短。

---

## 13.3 第二步：工具系统

```python
# --- 工具系统 ---

def read_file(path):
    """读取文件"""
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"错误：文件 {path} 不存在"

def write_file(path, content):
    """写入文件"""
    with open(path, 'w') as f:
        f.write(content)
    return f"已写入 {path} ({len(content)} 字符)"

def list_files(pattern="*"):
    """列出当前目录的文件"""
    import glob
    files = glob.glob(pattern)
    return "\n".join(files) if files else "没有找到文件"

# 工具注册表（名字 → 函数）
TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
}

# 工具描述（告诉 AI 有哪些工具可用）
TOOL_DESCRIPTIONS = [
    {
        "name": "read_file",
        "description": "读取指定路径的文件内容",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "将内容写入指定路径的文件",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "content": {"type": "string", "description": "文件内容"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_files",
        "description": "列出当前目录匹配的文件",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "glob 模式，如 *.py"}
            },
            "required": []
        }
    },
]
```

> 这就是第5章讲的 ToolSpec！每个工具都有名字、描述和 JSON Schema 格式的参数定义。

---

## 13.4 第三步：工具执行器

```python
import json

def execute_tool(name, arguments):
    """
    执行工具调用。
    
    对应 claw-code 的:
      execute_tool(name, input) -> Result<String, String>
    """
    tool_fn = TOOLS.get(name)
    if tool_fn is None:
        return f"错误：未知工具 '{name}'"
    
    try:
        # 把 JSON 参数传给工具函数
        result = tool_fn(**arguments)
        return str(result)
    except Exception as e:
        return f"工具执行错误：{e}"
```

> 对应 claw-code 的 `StaticToolExecutor`——通过名字查找工具函数并执行。

---

## 13.5 第四步：Agent Loop

```python
class MiniAgent:
    """
    最小 Agent 实现。
    
    对应 claw-code 的 ConversationRuntime。
    """
    
    def __init__(self, system_prompt="你是一个有用的助手。"):
        self.system_prompt = system_prompt
        self.messages = []           # 对应 Session.messages
        self.max_iterations = 10     # 对应 max_iterations (16)
    
    def run(self, user_input, api_client):
        """
        运行一次完整的 Agent Loop。
        
        对应 claw-code 的 run_turn()。
        """
        # 第一步：追加用户消息
        self.messages.append(user_message(user_input))
        
        iterations = 0
        total_usage = {"input_tokens": 0, "output_tokens": 0}
        
        while iterations < self.max_iterations:
            iterations += 1
            
            # 第二步：调用 AI
            response = api_client.chat(
                system=self.system_prompt,
                messages=self.messages,
                tools=TOOL_DESCRIPTIONS,
            )
            
            # 记录 token 用量
            usage = response.get("usage", {})
            total_usage["input_tokens"] += usage.get("input_tokens", 0)
            total_usage["output_tokens"] += usage.get("output_tokens", 0)
            
            # 第三步：检查是否有工具调用
            content = response.get("content", [])
            tool_calls = [block for block in content if block.get("type") == "tool_use"]
            text_parts = [block for block in content if block.get("type") == "text"]
            
            # 打印 AI 的文字回复
            for part in text_parts:
                print(f"  AI: {part['text']}")
            
            # 追加 AI 消息到历史
            self.messages.append({"role": "assistant", "content": content})
            
            # 第四步：如果没有工具调用，循环结束
            if not tool_calls:
                break
            
            # 第五步：执行每个工具调用
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["input"]
                tool_use_id = tool_call["id"]
                
                print(f"  [工具调用] {tool_name}({json.dumps(tool_input, ensure_ascii=False)})")
                
                # 执行工具（这里跳过了权限检查——简化版）
                result = execute_tool(tool_name, tool_input)
                
                print(f"  [工具结果] {result[:100]}...")
                
                # 追加工具结果到历史
                self.messages.append(tool_result_message(tool_use_id, result))
        
        return {
            "iterations": iterations,
            "usage": total_usage,
        }
```

> 和 claw-code 的 `run_turn()` 对比：结构完全一样！只是用 Python 字典替代了 Rust 结构体，用列表推导替代了 `filter_map`。

---

## 13.6 第五步：模拟 API 客户端

如果你没有 API key，可以用一个模拟客户端来测试：

```python
class MockApiClient:
    """模拟 AI API，用于测试"""
    
    def __init__(self):
        self.call_count = 0
    
    def chat(self, system, messages, tools):
        self.call_count += 1
        
        if self.call_count == 1:
            # 第一次调用：AI 决定读取文件
            return {
                "content": [
                    {"type": "text", "text": "让我先看看有哪些文件。"},
                    {
                        "type": "tool_use",
                        "id": "tool-1",
                        "name": "list_files",
                        "input": {"pattern": "*.py"},
                    }
                ],
                "usage": {"input_tokens": 50, "output_tokens": 20},
            }
        else:
            # 第二次调用：AI 给出最终回答
            return {
                "content": [
                    {"type": "text", "text": "我看到了你的 Python 文件。有什么需要我帮忙的吗？"},
                ],
                "usage": {"input_tokens": 100, "output_tokens": 15},
            }

# 测试
agent = MiniAgent()
result = agent.run("帮我看看当前目录有哪些 Python 文件", MockApiClient())
print(f"\n循环了 {result['iterations']} 轮，用了 {result['usage']} token")
```

输出：
```
  AI: 让我先看看有哪些文件。
  [工具调用] list_files({"pattern": "*.py"})
  [工具结果] agent.py
utils.py
...
  AI: 我看到了你的 Python 文件。有什么需要我帮忙的吗？

循环了 2 轮，用了 {'input_tokens': 150, 'output_tokens': 35} token
```

---

## 13.7 第六步：连接真实 AI

如果你有 Anthropic API key，可以连接真实的 AI：

```python
import urllib.request

class AnthropicApiClient:
    """真实的 Anthropic API 客户端"""
    
    def __init__(self, api_key, model="claude-sonnet-4-20250514"):
        self.api_key = api_key
        self.model = model
    
    def chat(self, system, messages, tools):
        # 构建请求体
        body = {
            "model": self.model,
            "max_tokens": 1024,
            "system": system,
            "messages": messages,
            "tools": [{"name": t["name"], "description": t["description"],
                        "input_schema": t["input_schema"]} for t in tools],
        }
        
        # 发送 HTTP 请求
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(body).encode(),
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        
        return data

# 使用
client = AnthropicApiClient("your-api-key-here")
agent = MiniAgent("你是一个编程助手。请使用提供的工具来完成任务。")
result = agent.run("帮我创建一个 hello.py 文件", client)
```

---

## 13.8 和 claw-code 的完整对比

| 特性 | claw-code (Rust) | MiniAgent (Python) |
|------|------------------|-------------------|
| 消息模型 | struct + enum | 字典 |
| 工具定义 | ToolSpec + JSON Schema | 字典 + 函数 |
| 工具执行 | match 分发 | 字典查找 |
| 权限系统 | Allow/Deny/Prompt | 无（全部允许） |
| Session 持久化 | JSON 文件 | 无 |
| 对话压缩 | 规则摘要 | 无 |
| Token 追踪 | UsageTracker | 简单累加 |
| MCP 支持 | 完整 | 无 |
| 错误处理 | Result<T, E> | try/except |
| 类型安全 | 编译时检查 | 运行时检查 |

---

## 13.9 本章小结

### 你学到了什么

1. **消息模型**：用 Python 字典表示消息
2. **工具系统**：注册表模式 + JSON Schema 描述
3. **Agent Loop**：while 循环 + 工具调用检测
4. **API 客户端**：模拟客户端用于测试，真实客户端用于生产

### 核心代码结构

```python
class MiniAgent:
    def __init__(self, system_prompt)    # 初始化
    def run(self, user_input, client)    # Agent Loop
    → messages.append(user_msg)          # 追加用户消息
    → while loop:                        # 循环
        → client.chat(...)               # 调用 AI
        → 检查工具调用                    # 判断是否继续
        → execute_tool(...)              # 执行工具
        → messages.append(tool_result)   # 追加结果
```

---

> **下一章**：[第14章：扩展 Agent](14-extend-agent.md) —— 怎么让你的 Agent 更强大？添加权限系统、对话压缩、MCP 支持、Session 持久化……
