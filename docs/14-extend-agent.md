# 第14章：扩展 Agent —— 从最小到完整

> **本章目标**：基于第13章的最小 Agent，讨论如何逐步扩展成完整的 Agent 系统。我们会覆盖权限系统、对话压缩、MCP 支持、Session 持久化等扩展方向，以及 Agent 开发的最佳实践。
>
> **难度**：⭐⭐⭐⭐⭐ 高级

---

## 14.1 回顾：我们的 Agent 还缺什么？

第13章我们实现了一个能工作的最小 Agent，但它缺少很多关键特性：

```
✅ 已有：Agent Loop、工具调用、消息模型
❌ 缺少：权限系统、对话压缩、MCP、持久化、多模型支持、错误恢复
```

这一章我们来讨论如何逐步添加这些功能。

---

## 14.2 扩展一：添加权限系统

### 设计思路

权限系统需要：
1. 三种模式：Allow、Deny、Prompt
2. 按工具配置不同的模式
3. 交互式确认（终端提示）

### Python 实现

```python
class PermissionPolicy:
    """权限策略"""
    
    def __init__(self, default_mode="prompt"):
        self.default_mode = default_mode  # "allow" / "deny" / "prompt"
        self.tool_modes = {}              # {"tool_name": "mode"}
    
    def with_tool_mode(self, tool_name, mode):
        self.tool_modes[tool_name] = mode
        return self
    
    def authorize(self, tool_name, tool_input):
        mode = self.tool_modes.get(tool_name, self.default_mode)
        
        if mode == "allow":
            return True
        elif mode == "deny":
            return False
        else:  # prompt
            print(f"\n  AI 想要执行: {tool_name}")
            print(f"  参数: {json.dumps(tool_input, ensure_ascii=False)[:200]}")
            answer = input("  允许吗？(y/n): ").strip().lower()
            return answer == "y"

# 使用
policy = PermissionPolicy(default_mode="prompt")
policy.with_tool_mode("read_file", "allow")   # 读文件自动允许
policy.with_tool_mode("list_files", "allow")   # 列出文件自动允许
# write_file 默认需要确认
```

### 集成到 Agent Loop

```python
# 在 run() 方法中，执行工具之前：
if not policy.authorize(tool_name, tool_input):
    result = f"权限拒绝：{tool_name} 未被授权"
else:
    result = execute_tool(tool_name, tool_input)
```

> 这就是第7章讲的"门卫"——在 AI 动手之前先问一句。

---

## 14.3 扩展二：添加对话压缩

### 设计思路

当消息太多时，把旧消息变成摘要。

### Python 实现

```python
def estimate_tokens(messages):
    """粗略估算 token 数（每 4 个字符约 1 个 token）"""
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += len(content) // 4
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text", "") or block.get("content", "")
                    total += len(text) // 4
    return total

def compact_messages(messages, preserve_recent=4, max_tokens=10000):
    """压缩旧消息，保留近期消息"""
    if len(messages) <= preserve_recent:
        return messages
    
    if estimate_tokens(messages) < max_tokens:
        return messages
    
    old = messages[:-preserve_recent]
    recent = messages[-preserve_recent:]
    
    # 生成摘要
    summary = generate_summary(old)
    
    # 用 System 消息替换旧消息
    compacted = [
        {"role": "user", "content": f"[对话摘要]\n{summary}"},
        {"role": "assistant", "content": "好的，我了解了之前的对话内容。请继续。"},
    ]
    compacted.extend(recent)
    
    return compacted

def generate_summary(messages):
    """从旧消息中提取关键信息"""
    user_count = sum(1 for m in messages if m["role"] == "user")
    tool_names = set()
    for m in messages:
        content = m.get("content", [])
        if isinstance(content, list):
            for block in content:
                if block.get("type") == "tool_use":
                    tool_names.add(block["name"])
    
    return (
        f"之前有 {len(messages)} 条消息 "
        f"(用户 {user_count} 条)，"
        f"使用过的工具: {', '.join(tool_names) if tool_names else '无'}"
    )
```

> 这是第10章讲的"对话压缩"的 Python 版本。更完善的版本可以用 AI 来生成摘要，而不是用规则。

---

## 14.4 扩展三：添加 Session 持久化

### Python 实现

```python
import json
import os

class SessionManager:
    """Session 管理器"""
    
    def __init__(self, save_dir=".sessions"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def save(self, session_id, messages):
        path = os.path.join(self.save_dir, f"{session_id}.json")
        with open(path, 'w') as f:
            json.dump({"version": 1, "messages": messages}, f, ensure_ascii=False, indent=2)
    
    def load(self, session_id):
        path = os.path.join(self.save_dir, f"{session_id}.json")
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            data = json.load(f)
        return data.get("messages", [])

# 集成到 Agent
class MiniAgent:
    def __init__(self, system_prompt, session_manager=None, session_id=None):
        self.system_prompt = system_prompt
        self.session_manager = session_manager
        self.session_id = session_id
        self.messages = []
        
        # 尝试恢复之前的会话
        if session_manager and session_id:
            self.messages = session_manager.load(session_id)
    
    def save(self):
        if self.session_manager and self.session_id:
            self.session_manager.save(self.session_id, self.messages)
```

> 对应第9章讲的"序列化 → 存储 → 反序列化"流程。

---

## 14.5 扩展四：添加 MCP 支持

### 设计思路

MCP 支持需要：
1. 连接外部工具服务器（通过 Stdio 启动子进程）
2. 通过 JSON-RPC 2.0 协议通信（带 Content-Length 帧编码）
3. 获取服务器提供的工具列表
4. 将外部工具添加到工具注册表

### Python 实现（基于 claw-code 的 McpStdioProcess）

```python
import subprocess
import json
import os

class McpStdioClient:
    """
    MCP Stdio 客户端。
    基于 claw-code 的 mcp_stdio.rs 实现。
    
    通信协议：JSON-RPC 2.0 over Stdio
    帧格式：Content-Length: {len}\r\n\r\n{json_payload}
    """
    
    def __init__(self, command, args=None, env=None):
        self.command = command
        self.args = args or []
        self.env = env or {}
        self.process = None
        self.request_id = 0
        self.initialized = False
    
    def connect(self):
        """启动 MCP 服务器子进程"""
        full_env = {**os.environ, **self.env}
        self.process = subprocess.Popen(
            [self.command, *self.args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env,
        )
    
    def _next_id(self):
        """递增请求 ID"""
        self.request_id += 1
        return self.request_id
    
    def _write_frame(self, payload):
        """写入一帧数据（Content-Length 编码）"""
        body = json.dumps(payload)
        frame = f"Content-Length: {len(body)}\r\n\r\n{body}"
        self.process.stdin.write(frame.encode())
        self.process.stdin.flush()
    
    def _read_frame(self):
        """读取一帧数据"""
        # 读取 header（直到空行）
        content_length = None
        while True:
            line = self.process.stdout.readline().decode()
            if line == "\r\n" or line == "\n":
                break
            if line.startswith("Content-Length:"):
                content_length = int(line.split(":")[1].strip())
        
        # 读取 body
        if content_length is None:
            raise ValueError("Missing Content-Length header")
        body = self.process.stdout.read(content_length)
        return json.loads(body)
    
    def _request(self, method, params=None):
        """发送 JSON-RPC 请求并等待响应"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }
        if params is not None:
            payload["params"] = params
        
        self._write_frame(payload)
        response = self._read_frame()
        
        if "error" in response:
            raise McpError(response["error"]["message"], response["error"]["code"])
        return response.get("result")
    
    def initialize(self):
        """初始化 MCP 连接（必须最先调用）"""
        result = self._request("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "my-agent", "version": "1.0.0"},
        })
        self.initialized = True
        return result
    
    def list_tools(self):
        """获取服务器提供的工具列表"""
        if not self.initialized:
            self.initialize()
        
        all_tools = []
        cursor = None
        
        # 支持分页（cursor 机制）
        while True:
            params = {}
            if cursor:
                params["cursor"] = cursor
            
            result = self._request("tools/list", params if params else None)
            all_tools.extend(result.get("tools", []))
            
            cursor = result.get("nextCursor")
            if not cursor:
                break
        
        return all_tools
    
    def call_tool(self, tool_name, arguments=None):
        """调用 MCP 服务器上的工具"""
        return self._request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {},
        })
    
    def shutdown(self):
        """关闭 MCP 连接"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()

class McpError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


class McpServerManager:
    """
    MCP 服务器管理器。
    管理多个 MCP 服务器连接，维护工具路由表。
    
    基于 claw-code 的 McpServerManager。
    """
    
    def __init__(self):
        self.servers = {}         # {server_name: McpStdioClient}
        self.tool_index = {}      # {qualified_name: (server_name, raw_name)}
    
    def add_server(self, name, command, args=None, env=None):
        """添加一个 MCP 服务器"""
        self.servers[name] = McpStdioClient(command, args, env)
    
    def discover_all_tools(self):
        """发现所有服务器的工具"""
        discovered = []
        
        for server_name, client in self.servers.items():
            client.connect()
            tools = client.list_tools()
            
            for tool in tools:
                raw_name = tool["name"]
                qualified_name = f"mcp__{server_name}__{raw_name}"
                
                # 注册到路由表
                self.tool_index[qualified_name] = (server_name, raw_name)
                discovered.append({
                    "server": server_name,
                    "qualified_name": qualified_name,
                    "raw_name": raw_name,
                    "tool": tool,
                })
        
        return discovered
    
    def call_tool(self, qualified_name, arguments=None):
        """调用工具（自动路由到正确的服务器）"""
        if qualified_name not in self.tool_index:
            raise ValueError(f"Unknown tool: {qualified_name}")
        
        server_name, raw_name = self.tool_index[qualified_name]
        client = self.servers[server_name]
        return client.call_tool(raw_name, arguments)
    
    def shutdown_all(self):
        """关闭所有服务器"""
        for client in self.servers.values():
            client.shutdown()


# 集成到 Agent
manager = McpServerManager()
manager.add_server("github", "uvx", args=["mcp-server-github"],
                   env={"GITHUB_TOKEN": "xxx"})
manager.add_server("filesystem", "uvx", args=["mcp-server-filesystem", "/tmp"])

# 发现所有工具
mcp_tools = manager.discover_all_tools()
# [{'server': 'github', 'qualified_name': 'mcp__github__create_issue', ...},
#  {'server': 'filesystem', 'qualified_name': 'mcp__filesystem__read_file', ...}]

# 把 MCP 工具添加到工具注册表
for entry in mcp_tools:
    tool = entry["tool"]
    TOOL_DESCRIPTIONS.append({
        "name": entry["qualified_name"],
        "description": tool.get("description", ""),
        "input_schema": tool.get("inputSchema", {}),
    })

# 使用
result = manager.call_tool("mcp__github__create_issue", {"title": "Bug fix"})
manager.shutdown_all()
```

> **和 claw-code 源码的对应关系**：`McpStdioClient` 对应 `mcp_stdio.rs` 中的 `McpStdioProcess`，`McpServerManager` 对应同文件中的 `McpServerManager`。`_write_frame` / `_read_frame` 对应 `write_frame` / `read_frame`，分页的 `while True` 循环对应 `discover_tools()` 中的 cursor 机制。

### MCP 通信协议详解

MCP 使用 JSON-RPC 2.0 协议，帧格式如下：

```
请求帧：
Content-Length: 87\r\n
\r\n
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26",...}}

响应帧：
Content-Length: 152\r\n
\r\n
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-03-26","capabilities":{"tools":{}},"serverInfo":{"name":"fake-mcp","version":"0.2.0"}}}
```

一次完整的 MCP 会话流程：

```
客户端                              服务器
  │                                    │
  │── initialize ──────────────────→   │  ① 握手
  │← ─ ─ ─ ─ ─ ─ ─ ─ capabilities ─   │
  │                                    │
  │── tools/list ──────────────────→   │  ② 发现工具
  │← ─ ─ ─ ─ ─ ─ ─ ─ tools[] ─ ─ ─   │
  │                                    │
  │── tools/call {name:"echo"} ───→    │  ③ 调用工具
  │← ─ ─ ─ ─ ─ ─ ─ ─ result ─ ─ ─    │
  │                                    │
  │── tools/call {name:"echo"} ───→    │  ④ 再次调用（复用连接）
  │← ─ ─ ─ ─ ─ ─ ─ ─ result ─ ─ ─    │
```

> 关键设计：连接是持久的——`initialize` 只调用一次，后续的 `tools/list` 和 `tools/call` 都复用同一个连接。claw-code 的 `McpServerManager` 通过 `ensure_server_ready()` 方法确保这一点。

---

## 14.6 扩展五：添加 Token 追踪

```python
class UsageTracker:
    """Token 用量追踪器"""
    
    def __init__(self):
        self.cumulative = {
            "input_tokens": 0,
            "output_tokens": 0,
        }
        self.turns = 0
    
    def record(self, usage):
        self.cumulative["input_tokens"] += usage.get("input_tokens", 0)
        self.cumulative["output_tokens"] += usage.get("output_tokens", 0)
        self.turns += 1
    
    def estimate_cost(self, model="sonnet"):
        pricing = {
            "haiku": {"input": 1, "output": 5},
            "sonnet": {"input": 15, "output": 75},
            "opus": {"input": 15, "output": 75},
        }
        p = pricing.get(model, pricing["sonnet"])
        input_cost = self.cumulative["input_tokens"] / 1_000_000 * p["input"]
        output_cost = self.cumulative["output_tokens"] / 1_000_000 * p["output"]
        return input_cost + output_cost
    
    def summary(self):
        return (
            f"轮数: {self.turns}, "
            f"输入: {self.cumulative['input_tokens']:,} tokens, "
            f"输出: {self.cumulative['output_tokens']:,} tokens, "
            f"预计费用: ${self.estimate_cost():.4f}"
        )
```

---

## 14.7 Agent 开发的最佳实践

### 实践一：永远限制迭代次数

```python
MAX_ITERATIONS = 16  # 安全阀
```

> 没有上限的循环是 Agent 的头号杀手。第4章详细讲了为什么。

### 实践二：工具输出要精简

```python
def execute_tool(name, arguments):
    result = TOOLS[name](**arguments)
    # 截断过长的输出
    if len(result) > 10000:
        result = result[:10000] + "\n... (已截断)"
    return result
```

> 工具输出会变成下一轮的 input token。输出越长，下一轮越贵。

### 实践三：错误不是异常，而是数据

```python
try:
    result = tool_fn(**arguments)
except Exception as e:
    result = f"工具执行错误：{e}"
# 不要 raise，把错误信息返回给 AI
```

> AI 看到错误后会自己想办法解决，而不是直接崩溃。

### 实践四：System Prompt 要清晰

```python
SYSTEM_PROMPT = """你是一个编程助手。

规则：
1. 先理解用户需求，再动手
2. 每次只做一件事
3. 做完后简要说明结果
4. 如果不确定，先询问用户

你可以使用以下工具：
- read_file: 读取文件
- write_file: 写入文件
- list_files: 列出文件
"""
```

### 实践五：测试用 Mock，生产用真实

```python
# 测试时用 Mock
client = MockApiClient()
agent = MiniAgent(SYSTEM_PROMPT)
result = agent.run("测试", client)

# 生产时用真实 API
client = AnthropicApiClient(os.environ["ANTHROPIC_API_KEY"])
agent = MiniAgent(SYSTEM_PROMPT)
result = agent.run("帮我创建一个项目", client)
```

---

## 14.8 扩展七：添加错误恢复

Agent 在运行中可能遇到各种错误——API 超时、工具执行失败、网络中断。一个好的 Agent 需要有错误恢复能力。

### 重试机制

```python
import time

class RetryPolicy:
    """重试策略"""
    
    def __init__(self, max_retries=3, base_delay=1.0, max_delay=30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def delay(self, attempt):
        """指数退避延迟"""
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)

def call_with_retry(fn, policy=RetryPolicy()):
    """带重试的函数调用"""
    last_error = None
    
    for attempt in range(policy.max_retries):
        try:
            return fn()
        except Exception as e:
            last_error = e
            if attempt < policy.max_retries - 1:
                delay = policy.delay(attempt)
                print(f"  [重试] {attempt + 1}/{policy.max_retries}，{delay:.1f}s 后重试...")
                time.sleep(delay)
    
    raise last_error

# 使用：在 Agent Loop 中包装 API 调用
response = call_with_retry(lambda: api_client.chat(...))
```

### 优雅降级

```python
class GracefulAgent:
    """支持优雅降级的 Agent"""
    
    def __init__(self, system_prompt, models=None):
        self.system_prompt = system_prompt
        self.models = models or ["claude-sonnet", "claude-haiku"]  # 降级序列
    
    def run(self, user_input):
        """尝试主模型，失败则降级到备用模型"""
        for model in self.models:
            try:
                return self._run_with_model(user_input, model)
            except Exception as e:
                print(f"  [降级] {model} 失败: {e}")
                if model == self.models[-1]:
                    raise  # 最后一个模型也失败了
                print(f"  [降级] 尝试 {self.models[self.models.index(model) + 1]}...")
        
    def _run_with_model(self, user_input, model):
        """使用指定模型运行 Agent"""
        client = AnthropicApiClient(os.environ["ANTHROPIC_API_KEY"], model=model)
        agent = MiniAgent(self.system_prompt)
        return agent.run(user_input, client)
```

> **降级序列**：从最强的模型开始，逐步降级到更便宜但更稳定的模型。这在生产环境中很有用——当 Sonnet 因负载过高而超时时，可以自动切换到 Haiku。

---

## 14.9 Agent 的未来方向

### 多 Agent 协作

多个 Agent 分工合作——一个负责搜索，一个负责编码，一个负责测试。

```python
class AgentPool:
    """Agent 池——并行执行多个子任务"""
    
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
    
    def dispatch(self, tasks, client):
        """
        并行分发多个任务给独立的 Agent。
        
        对应 claw-code 的 Agent 工具：启动子代理执行特定任务。
        """
        results = {}
        
        for task in tasks:
            # 每个子任务创建一个独立的 Agent（独立的 Session）
            agent = MiniAgent(self.system_prompt)
            result = agent.run(task, client)
            results[task] = result
        
        return results

# 使用：并行搜索多个目录
pool = AgentPool("你是一个代码搜索专家。")
results = pool.dispatch([
    "搜索 src/ 目录中的 TODO 注释",
    "搜索 tests/ 目录中的 TODO 注释",
    "搜索 docs/ 目录中的 TODO 注释",
], client)

# 汇总结果
for task, result in results.items():
    print(f"{task}: {result['iterations']} 轮完成")
```

> **claw-code 的 Agent 工具**就实现了类似的功能。子代理有独立的 System Prompt 和 Agent Loop，执行完成后结果保存到磁盘文件中。主代理通过读取这些文件来获取子代理的结果。这种设计避免了子代理的上下文污染主对话。

#### 主流多 Agent 框架对比

| 框架 | 协作模式 | 适用场景 |
|------|---------|---------|
| **CrewAI** | 角色分工（研究员、程序员、测试员） | 流水线式任务 |
| **LangGraph** | 状态图（DAG 定义 Agent 间的依赖关系） | 复杂工作流 |
| **AutoGen** | 事件驱动（Agent 之间对话） | 讨论和协商 |
| **claw-code** | 主-子（主 Agent 派生子 Agent） | 并行子任务 |

### 长期记忆

不只是压缩对话历史，而是让 Agent 真正"记住"你之前的偏好和项目知识。

### 工具自动发现

Agent 自动发现可用的 MCP 服务，不需要手动配置。

### 更好的错误恢复

Agent 遇到错误后能更智能地恢复，而不是简单地重试。

---

## 14.9 全书总结

恭喜你读完了整本教程！让我们回顾一下你学到了什么：

### 第一部分：入门（第1-3章）

- Agent = LLM + 工具 + 循环
- ReAct 模式：思考 → 行动 → 观察
- System Prompt 的双层架构

### 第二部分：核心机制（第4-8章）

- Agent Loop：消息循环的核心
- 工具系统：18 个工具的设计和实现
- 消息模型：Session → Message → ContentBlock
- 权限系统：Allow / Deny / Prompt
- 启动流程：12 个 Bootstrap 阶段

### 第三部分：高级特性（第9-12章）

- Session 持久化：对话的保存和恢复
- 对话压缩：旧消息变成摘要
- Token 计费：四种 token 类型和模型定价
- MCP 协议：连接外部工具服务

### 第四部分：实战（第13-14章）

- 用 Python 实现最小 Agent
- 扩展成完整 Agent 的路线图

### 术语速查（全书）

| 术语 | 章节 | 解释 |
|------|------|------|
| Agent | 1 | 能自主行动的 AI 系统 |
| LLM | 1 | 大语言模型 |
| ReAct | 1 | 思考+行动模式 |
| Agent Loop | 4 | 思考→行动→观察循环 |
| ToolSpec | 5 | 工具规范（名称+描述+参数） |
| ContentBlock | 6 | 消息内容块 |
| PermissionPolicy | 7 | 权限策略 |
| Bootstrap | 8 | 启动初始化 |
| Session | 9 | 一次完整的对话 |
| Compaction | 10 | 对话压缩 |
| TokenUsage | 11 | Token 用量统计 |
| MCP | 12 | 外部工具连接协议 |

---

> **感谢你的阅读！** 希望这本教程帮你理解了 AI Agent 的核心架构。下一步，你可以：
> 1. 阅读真实的 Claude Code 源码
> 2. 基于 MiniAgent 构建自己的 Agent
> 3. 学习更多 Agent 框架（LangChain、CrewAI 等）
> 4. 探索 MCP 生态，连接更多工具服务
