"""
教程配图生成器 - claw-code 教程专用
用法: python3 draw.py <图名>
生成的 PNG 图片保存在 tutorial/diagrams/ 目录下
"""

import graphviz
import sys
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 配色方案 ──────────────────────────────────────────────
# 温暖、现代、非程序员友好的配色
COLORS = {
    "user":      "#4A90D9",   # 蓝色 - 用户相关
    "llm":       "#7B68EE",   # 紫色 - AI/LLM 相关
    "tool":      "#2ECC71",   # 绿色 - 工具相关
    "core":      "#E74C3C",   # 红色 - 核心模块
    "data":      "#F39C12",   # 橙色 - 数据/存储
    "security":  "#E67E22",   # 深橙 - 安全/权限
    "mcp":       "#1ABC9C",   # 青色 - MCP
    "bg_light":  "#F8F9FA",   # 浅灰背景
    "bg_user":   "#EBF5FB",   # 浅蓝背景
    "bg_llm":    "#F4ECF7",   # 浅紫背景
    "bg_tool":   "#EAFAF1",   # 浅绿背景
    "bg_core":   "#FDEDEC",   # 浅红背景
}


def make_dot(name: str, label: str = "", **kwargs) -> graphviz.Digraph:
    """创建一个预配置的 Digraph"""
    dot = graphviz.Digraph(name=name, format="png")
    dot.attr(
        rankdir="LR",         # 默认从左到右，减少图片高度
        bgcolor=COLORS["bg_light"],
        fontname="Arial",
        label=label,
        labelloc="t",
        fontsize="20",
        fontcolor="#2C3E50",
        pad="0.5",
        nodesep="0.4",
        ranksep="0.6",
        dpi="300",            # 300 DPI 高清
        size="15,9",          # 更大的画布，给节点更多空间
        ratio="fill",         # 填充指定区域，避免图片过高
    )
    return dot


def node(dot, name, label, color, shape="box", icon="", fontsize="14"):
    """添加一个带样式的节点"""
    display = f"{icon} {label}" if icon else label
    dot.node(
        name,
        label=display,
        shape=shape,
        style="filled,rounded",
        fillcolor=color,
        fontcolor="white",
        fontname="Arial",
        fontsize=fontsize,
        penwidth="0",
        margin="0.2,0.1",
    )


def edge(dot, src, dst, label="", style="solid", color="#7F8C8D"):
    """添加一条带样式的边"""
    dot.edge(
        src, dst,
        label=label,
        color=color,
        fontname="Arial",
        fontsize="11",
        fontcolor="#7F8C8D",
        style=style,
        penwidth="1.5",
    )


def save(dot, name):
    """保存到文件"""
    path = os.path.join(OUTPUT_DIR, name)
    dot.render(path, cleanup=True)
    print(f"✅ 已生成: {path}.png")


# ── 第1章配图 ──────────────────────────────────────────────

def ch01_agent_three_elements():
    """第1章: Agent 三大要素"""
    dot = make_dot("ch01_three_elements", "Agent 的三大要素")

    with dot.subgraph(name="cluster_main") as c:
        c.attr(
            style="filled",
            color=COLORS["bg_light"],
            fillcolor=COLORS["bg_light"],
            label="Agent（智能助手）",
            fontname="Arial",
            fontsize="18",
            fontcolor="#2C3E50",
            labeljust="l",
        )

        node(c, "llm", "LLM\n大脑\n理解意图 · 制定计划 · 做出决策", COLORS["llm"], icon="🧠")
        node(c, "tools", "Tools\n双手\n读写文件 · 执行命令 · 搜索代码", COLORS["tool"], icon="🛠️")
        node(c, "loop", "Loop\n意志\n持续迭代 · 不达目的不停止", COLORS["core"], icon="🔄")

    save(dot, "ch01_three_elements")


def ch01_react_loop():
    """第1章: ReAct 循环"""
    dot = make_dot("ch01_react_loop", "ReAct 循环: 思考 → 行动 → 观察")
    dot.attr(rankdir="TB")

    node(dot, "thought", "Thought 思考\n\"我需要先看看文件内容\"", COLORS["llm"], icon="💭")
    node(dot, "action", "Action 行动\n调用 Read 工具读取文件", COLORS["tool"], icon="🎯")
    node(dot, "observe", "Observe 观察\n\"文件中有 3 个 print 语句\"", COLORS["data"], icon="👁️")
    node(dot, "done", "最终回答\n\"已全部替换完成\"", COLORS["user"], icon="✅")
    node(dot, "user_input", "用户输入", COLORS["user"], shape="oval", icon="👤")

    edge(dot, "user_input", "thought", "")
    edge(dot, "thought", "action", "决定怎么做")
    edge(dot, "action", "observe", "获得结果")
    edge(dot, "observe", "thought", "还没做完?\n再想想", style="dashed", color=COLORS["core"])
    edge(dot, "observe", "done", "做完了!", color=COLORS["tool"])

    save(dot, "ch01_react_loop")


def ch01_evolution():
    """第1章: Agent 发展历程"""
    dot = make_dot("ch01_evolution", "AI 的进化之路")
    dot.attr(rankdir="LR")

    node(dot, "v1", "传统 NLP\n2022之前\n只能做特定任务", "#95A5A6", icon="📋")
    node(dot, "v2", "LLM 时代\n2022-2023\n能聊天回答问题", COLORS["user"], icon="💬")
    node(dot, "v3", "工具调用\n2024\n能查天气算数学", COLORS["tool"], icon="🔧")
    node(dot, "v4", "Agent 时代\n2025-2026\n能自主完成任务", COLORS["core"], icon="🚀")

    edge(dot, "v1", "v2", "能说更多话")
    edge(dot, "v2", "v3", "能动手了")
    edge(dot, "v3", "v4", "能自主循环")

    save(dot, "ch01_evolution")


# ── 第2章配图 ──────────────────────────────────────────────

def ch02_full_journey():
    """第2章: 一次请求的完整旅程"""
    dot = make_dot("ch02_full_journey", "一次请求从头到尾的旅程")
    dot.attr(rankdir="TB", nodesep="0.3", ranksep="0.5")

    steps = [
        ("input",   "① 你按下回车",            COLORS["user"],     "👤"),
        ("prompt",  "② 组装 \"员工手册\"\n(System Prompt)", COLORS["llm"], "📖"),
        ("history", "③ 加载之前的对话记录",      COLORS["data"],     "💾"),
        ("api",     "④ 打电话给 AI 大脑\n(API 调用)",        COLORS["llm"],     "📡"),
        ("parse",   "⑤ 解析 AI 的回复",         COLORS["llm"],     "📝"),
        ("perm",    "⑥ 安全检查:\nAI 可以做这个操作吗?",   COLORS["security"], "🔒"),
        ("exec",    "⑦ 执行工具\n(读文件/改代码/跑命令)",  COLORS["tool"],     "⚡"),
        ("check",   "⑧ 任务完成了吗?",          COLORS["core"],    "❓"),
        ("output",  "⑨ 显示最终回答",           COLORS["user"],    "✅"),
    ]

    for name, label, color, icon in steps:
        node(dot, name, label, color, icon=icon)

    edge(dot, "input", "prompt")
    edge(dot, "prompt", "history")
    edge(dot, "history", "api")
    edge(dot, "api", "parse")
    edge(dot, "parse", "perm")
    edge(dot, "perm", "exec")
    edge(dot, "exec", "check")
    edge(dot, "check", "output", "完成了!")
    edge(dot, "check", "api", "还没完成?\n回到④再来一轮", style="dashed", color=COLORS["core"])

    save(dot, "ch02_full_journey")


def ch02_six_stages():
    """第2章: 六大阶段精简版"""
    dot = make_dot("ch02_six_stages", "六大阶段 (精简版)")
    dot.attr(rankdir="LR", nodesep="0.6")

    stages = [
        ("s1", "输入\n你说一句话",   COLORS["user"]),
        ("s2", "准备\n组装员工手册",  COLORS["llm"]),
        ("s3", "思考\nAI 大脑推理",   COLORS["llm"]),
        ("s4", "行动\n执行工具",      COLORS["tool"]),
        ("s5", "判断\n做完了吗?",     COLORS["core"]),
        ("s6", "回答\n告诉你结果",    COLORS["user"]),
    ]

    for name, label, color in stages:
        node(dot, name, label, color, shape="box")

    edge(dot, "s1", "s2")
    edge(dot, "s2", "s3")
    edge(dot, "s3", "s4")
    edge(dot, "s4", "s5")
    edge(dot, "s5", "s6", "是")
    edge(dot, "s5", "s3", "否，再想", style="dashed", color=COLORS["core"])

    save(dot, "ch02_six_stages")


def ch02_crate_architecture():
    """第2章: claw-code 6个Crate架构"""
    dot = make_dot("ch02_crates", "claw-code 的 6 个模块")
    dot.attr(rankdir="TB")

    # CLI 层
    with dot.subgraph(name="cluster_cli") as c:
        c.attr(style="filled", fillcolor=COLORS["bg_user"], label="前台 (CLI)", fontname="Arial", fontsize="14")
        node(c, "cli", "rusty-claude-cli\n前台接待\n接收你的指令", COLORS["user"], icon="🏪")

    # 核心层
    with dot.subgraph(name="cluster_runtime") as c:
        c.attr(style="filled", fillcolor=COLORS["bg_core"], label="核心 (Runtime)", fontname="Arial", fontsize="14")
        node(c, "rt", "runtime\n厨师长\n统筹整个流程", COLORS["core"], icon="👨‍🍳")

    # 支撑层
    with dot.subgraph(name="cluster_support") as c:
        c.attr(style="filled", fillcolor=COLORS["bg_tool"], label="支撑工具", fontname="Arial", fontsize="14")
        node(c, "api", "api\n电话线\n和 AI 通信", COLORS["llm"], icon="📞")
        node(c, "tools", "tools\n厨具\n具体工具实现", COLORS["tool"], icon="🔧")

    # 辅助层
    with dot.subgraph(name="cluster_aux") as c:
        c.attr(style="filled", fillcolor="#F5EEF8", label="辅助", fontname="Arial", fontsize="14")
        node(c, "cmd", "commands\n菜单\n斜杠命令定义", "#9B59B6", icon="📋")
        node(c, "compat", "compat-harness\n翻译器\n提取元数据", "#9B59B6", icon="🔄")

    edge(dot, "cli", "rt", "交给厨师长")
    edge(dot, "rt", "api", "打电话给 AI")
    edge(dot, "rt", "tools", "使用厨具")
    edge(dot, "compat", "cmd", "")
    edge(dot, "compat", "tools", "")

    save(dot, "ch02_crates")


# ── 第3章配图 ──────────────────────────────────────────────

def ch03_prompt_layers():
    """第3章: System Prompt 分层结构"""
    dot = make_dot("ch03_prompt_layers", "System Prompt 的分层结构")
    dot.attr(rankdir="TB", ranksep="0.4")

    node(dot, "intro",   "📋 身份定义\n\"你是一个编程助手\"",      "#3498DB", icon="")
    node(dot, "style",   "🎨 输出风格\n\"回答要简洁\"",         "#9B59B6", icon="")
    node(dot, "system",  "⚙️ 系统规则\n\"不要猜 URL\"",         COLORS["llm"], icon="")
    node(dot, "tasks",   "📝 任务准则\n\"先看代码再改\"",        COLORS["tool"], icon="")
    node(dot, "boundary","━━━ 动态分界线 ━━━",                  "#BDC3C7", fontsize="12")
    node(dot, "env",     "🌍 环境信息\n操作系统/工作目录/日期",   "#1ABC9C", icon="")
    node(dot, "project", "📄 项目上下文\ngit status",            COLORS["data"], icon="")
    node(dot, "claude_md","📜 CLAUDE.md\n项目专属规则",         COLORS["core"], icon="")
    node(dot, "config",  "🔧 运行时配置\nsettings.json",        "#E67E22", icon="")

    with dot.subgraph(name="cluster_static") as s:
        s.attr(style="filled", fillcolor="#EBF5FB", label="静态层（不变的部分）", fontname="Arial", fontsize="13", fontcolor="#2C3E50")
        s.node("intro")
        s.node("style")
        s.node("system")
        s.node("tasks")

    with dot.subgraph(name="cluster_dynamic") as s:
        s.attr(style="filled", fillcolor="#FEF9E7", label="动态层（每次启动时更新）", fontname="Arial", fontsize="13", fontcolor="#2C3E50")
        s.node("env")
        s.node("project")
        s.node("claude_md")
        s.node("config")

    edge(dot, "intro", "style", "")
    edge(dot, "style", "system", "")
    edge(dot, "system", "tasks", "")
    edge(dot, "tasks", "boundary", "")
    edge(dot, "boundary", "env", "")
    edge(dot, "env", "project", "")
    edge(dot, "project", "claude_md", "")
    edge(dot, "claude_md", "config", "")

    save(dot, "ch03_prompt_layers")


def ch03_claude_md_discovery():
    """第3章: CLAUDE.md 文件发现过程"""
    dot = make_dot("ch03_claude_md_discovery", "CLAUDE.md 文件是怎么被发现的")
    dot.attr(rankdir="LR", ranksep="0.3")

    with dot.subgraph(name="cluster_fs") as c:
        c.attr(style="filled", fillcolor=COLORS["bg_light"], label="你的文件系统", fontname="Arial", fontsize="13")
        node(c, "root", "/ 项目根目录\nCLAUDE.md ✅", "#2ECC71")
        node(c, "src",  "/src 源代码目录\nCLAUDE.md ✅", "#2ECC71")
        node(c, "api",  "/src/api API目录\nCLAUDE.md ✅", "#2ECC71")
        node(c, "dot",  "/src/api/.claude\nCLAUDE.md ✅", "#2ECC71")
        node(c, "other", "/src/api/tests\n(没有 CLAUDE.md)", "#BDC3C7")

    node(dot, "agent", "🤖 Agent\n从当前目录\n向上逐级查找", COLORS["core"], shape="diamond")

    edge(dot, "root", "src", "")
    edge(dot, "src", "api", "")
    edge(dot, "api", "dot", "")
    edge(dot, "dot", "other", "")

    save(dot, "ch03_claude_md_discovery")


def ch03_budget():
    """第3章: 指令文件预算控制"""
    dot = make_dot("ch03_budget", "指令文件的预算控制")
    dot.attr(rankdir="TB")

    node(dot, "f1", "CLAUDE.md (根目录)\n\"用 Python 3.12\"\n120 字 → ✅ 放行", "#2ECC71")
    node(dot, "f2", "CLAUDE.md (src/)\n\"代码风格遵循 PEP 8\"\n80 字 → ✅ 放行", "#2ECC71")
    node(dot, "f3", "CLAUDE.md (src/api/)\n\"所有 API 要有测试\"\"\n50 字 → ✅ 放行", "#2ECC71")
    node(dot, "f4", "CLAUDE.local.md\n（和根目录内容重复）\n→ 🚫 去重，跳过", "#E74C3C")
    node(dot, "f5", "大文件 CLAUDE.md\n5000 字 → ✂️ 截断到 4000 字", "#F39C12")

    with dot.subgraph(name="cluster_rules") as c:
        c.attr(style="filled", fillcolor="#FEF9E7", label="三条规则", fontname="Arial", fontsize="13")
        node(c, "r1", "规则1: 单文件不超过 4000 字", "#3498DB")
        node(c, "r2", "规则2: 所有文件总计不超过 12000 字", "#3498DB")
        node(c, "r3", "规则3: 相同内容自动去重", "#3498DB")

    edge(dot, "r1", "f5", "超了就截断")
    edge(dot, "r3", "f4", "重复就跳过")

    save(dot, "ch03_budget")


# ── 第4章配图 ──────────────────────────────────────────────

def ch04_loop_overview():
    """第4章: Agent Loop 整体流程"""
    dot = make_dot("ch04_loop_overview", "Agent Loop: 思考→行动→观察 的循环")
    dot.attr(rankdir="TB", nodesep="0.4", ranksep="0.5")

    node(dot, "start", "用户输入\n\"帮我把 print 换成 logging\"", COLORS["user"], icon="👤")
    node(dot, "build_req", "组装请求\nSystem Prompt + 聊天记录", COLORS["llm"], icon="📦")
    node(dot, "call_api", "调用 AI\n(stream 流式传输)", COLORS["llm"], icon="📡")
    node(dot, "parse", "解析回复\n文字 or 工具调用?", COLORS["data"], icon="🔍")
    node(dot, "has_tool", "有工具调用?", COLORS["core"], shape="diamond", icon="")
    node(dot, "check_perm", "权限检查\n允许执行吗?", COLORS["security"], shape="diamond", icon="🔒")
    node(dot, "exec_tool", "执行工具\n拿到结果", COLORS["tool"], icon="⚡")
    node(dot, "deny", "权限拒绝\n返回拒绝原因", "#E74C3C", icon="🚫")
    node(dot, "append", "结果追加到\n聊天记录", COLORS["data"], icon="💾")
    node(dot, "done", "循环结束\n返回最终回答", COLORS["user"], icon="✅")
    node(dot, "max_iter", "超过 16 轮?\n报错退出", "#E74C3C", icon="⚠️")

    edge(dot, "start", "build_req", "新一轮开始")
    edge(dot, "build_req", "call_api")
    edge(dot, "call_api", "parse")
    edge(dot, "parse", "has_tool")
    edge(dot, "has_tool", "done", "没有 → 循环结束", color=COLORS["tool"])
    edge(dot, "has_tool", "check_perm", "有 → 检查权限")
    edge(dot, "check_perm", "exec_tool", "允许", color=COLORS["tool"])
    edge(dot, "check_perm", "deny", "拒绝", color="#E74C3C")
    edge(dot, "deny", "append")
    edge(dot, "exec_tool", "append")
    edge(dot, "append", "build_req", "回到下一轮", style="dashed", color=COLORS["core"])
    edge(dot, "build_req", "max_iter", "迭代计数 +1", style="dashed", color="#E74C3C")

    save(dot, "ch04_loop_overview")


def ch04_run_turn_dataflow():
    """第4章: run_turn 数据流"""
    dot = make_dot("ch04_run_turn_dataflow", "run_turn() 的数据流")
    dot.attr(rankdir="LR", nodesep="0.3", ranksep="0.4")

    # 输入
    with dot.subgraph(name="cluster_input") as c:
        c.attr(style="filled", fillcolor=COLORS["bg_user"], label="输入", fontname="Arial", fontsize="13")
        node(c, "user_msg", "用户消息\n\"2+2等于几?\"", COLORS["user"])
        node(c, "sys_prompt", "System Prompt\n[员工手册...]", COLORS["llm"])
        node(c, "history", "聊天记录\n[之前的对话...]", COLORS["data"])

    # 处理
    with dot.subgraph(name="cluster_process") as c:
        c.attr(style="filled", fillcolor=COLORS["bg_core"], label="ConversationRuntime", fontname="Arial", fontsize="13")
        node(c, "api_req", "ApiRequest\n{system_prompt,\n messages}", COLORS["core"])
        node(c, "events", "Vec<AssistantEvent>\n[TextDelta, ToolUse,\n Usage, MessageStop]", "#9B59B6")
        node(c, "built_msg", "ConversationMessage\n[文字块, 工具调用块]", COLORS["data"])

    # 输出
    with dot.subgraph(name="cluster_output") as c:
        c.attr(style="filled", fillcolor=COLORS["bg_tool"], label="输出", fontname="Arial", fontsize="13")
        node(c, "turn_sum", "TurnSummary\n{iterations, usage,\n messages}", COLORS["tool"])

    edge(dot, "sys_prompt", "api_req")
    edge(dot, "history", "api_req")
    edge(dot, "user_msg", "api_req")
    edge(dot, "api_req", "events", "api_client.stream()")
    edge(dot, "events", "built_msg", "build_assistant_message()")
    edge(dot, "built_msg", "turn_sum")

    save(dot, "ch04_run_turn_dataflow")


def ch04_event_types():
    """第4章: AssistantEvent 四种类型"""
    dot = make_dot("ch04_event_types", "AI 回复的四种事件 (AssistantEvent)")
    dot.attr(rankdir="LR", nodesep="0.5")

    node(dot, "stream", "AI 流式回复\n(stream)", COLORS["llm"], icon="📡")

    node(dot, "text", "TextDelta\n文字片段\n\"让我想想...\"", COLORS["user"], icon="💬")
    node(dot, "tool", "ToolUse\n工具调用\n{id, name, input}", COLORS["tool"], icon="🔧")
    node(dot, "usage", "Usage\nToken 用量\n{input, output}", COLORS["data"], icon="📊")
    node(dot, "stop", "MessageStop\n回复结束\n（哨兵信号）", COLORS["core"], icon="🏁")

    node(dot, "result", "ConversationMessage\n{role: Assistant,\n blocks: [...]}", "#9B59B6", icon="📦")

    edge(dot, "stream", "text")
    edge(dot, "stream", "tool")
    edge(dot, "stream", "usage")
    edge(dot, "stream", "stop")
    edge(dot, "text", "result", "拼成 Text 块")
    edge(dot, "tool", "result", "变成 ToolUse 块")
    edge(dot, "usage", "result", "记录用量")
    edge(dot, "stop", "result", "确认完整")

    save(dot, "ch04_event_types")


# ── 第5章配图 ──────────────────────────────────────────────

def ch05_tool_categories():
    """第5章: 工具分类"""
    dot = make_dot("ch05_tool_categories", "claw-code 的 18 个工具（按类型分类）")
    dot.attr(rankdir="TB", nodesep="0.15", ranksep="0.3")

    # 第一行：核心 + 搜索 + 执行
    with dot.subgraph(name="cluster_row1") as row:
        row.attr(style="invis")

        with row.subgraph(name="cluster_file") as c:
            c.attr(style="filled", fillcolor=COLORS["bg_tool"], label="文件操作（核心）", fontname="Arial", fontsize="13")
            node(c, "read", "read_file\n读取文件", COLORS["tool"])
            node(c, "write", "write_file\n写入文件", COLORS["tool"])
            node(c, "edit", "edit_file\n编辑文件", COLORS["tool"])

        with row.subgraph(name="cluster_search") as c:
            c.attr(style="filled", fillcolor=COLORS["bg_user"], label="搜索工具", fontname="Arial", fontsize="13")
            node(c, "glob", "glob_search\n按文件名搜索", COLORS["user"])
            node(c, "grep", "grep_search\n按内容搜索", COLORS["user"])

        with row.subgraph(name="cluster_exec") as c:
            c.attr(style="filled", fillcolor=COLORS["bg_core"], label="执行工具", fontname="Arial", fontsize="13")
            node(c, "bash", "bash\n执行命令", COLORS["core"])
            node(c, "repl", "REPL\n执行代码", COLORS["core"])
            node(c, "pwsh", "PowerShell\nWindows 命令", COLORS["core"])

    # 第二行：网络 + 其他
    with dot.subgraph(name="cluster_row2") as row:
        row.attr(style="invis")

        with row.subgraph(name="cluster_web") as c:
            c.attr(style="filled", fillcolor="#F4ECF7", label="网络工具", fontname="Arial", fontsize="13")
            node(c, "fetch", "WebFetch\n抓取网页", "#9B59B6")
            node(c, "search", "WebSearch\n搜索互联网", "#9B59B6")

        with row.subgraph(name="cluster_other") as c:
            c.attr(style="filled", fillcolor="#FEF9E7", label="其他工具", fontname="Arial", fontsize="13")
            node(c, "agent", "Agent\n子代理", COLORS["data"])
            node(c, "skill", "Skill\n技能加载", COLORS["data"])
            node(c, "todo", "TodoWrite\n任务列表", COLORS["data"])
            node(c, "nb", "NotebookEdit\n编辑笔记本", COLORS["data"])
            node(c, "ts", "ToolSearch\n搜索工具", COLORS["data"])
            node(c, "cfg", "Config\n配置管理", COLORS["data"])
            node(c, "slp", "Sleep\n等待", COLORS["data"])
            node(c, "msg", "SendUserMessage\n发消息", COLORS["data"])
            node(c, "so", "StructuredOutput\n结构化输出", COLORS["data"])

    save(dot, "ch05_tool_categories")


def ch05_tool_spec():
    """第5章: ToolSpec 三要素"""
    dot = make_dot("ch05_tool_spec", "ToolSpec: 每个工具的身份证")
    dot.attr(rankdir="LR", nodesep="0.4", ranksep="0.4")

    node(dot, "spec", "ToolSpec\n工具规范", COLORS["core"])
    node(dot, "name", "name\n工具名称\n\"read_file\"", COLORS["user"])
    node(dot, "desc", "description\n工具描述\n\"读取文件内容\"", COLORS["llm"])
    node(dot, "schema", "input_schema\n参数格式\nJSON Schema", COLORS["tool"])
    node(dot, "ai", "AI 看到的\n工具列表", "#9B59B6")
    node(dot, "exec", "execute_tool()\n执行分发", COLORS["data"])

    edge(dot, "spec", "name")
    edge(dot, "spec", "desc")
    edge(dot, "spec", "schema")
    edge(dot, "name", "ai", "发送给 AI\nAI 据此决定\n调用哪个工具")
    edge(dot, "ai", "exec", "AI 回复包含\n工具调用")
    edge(dot, "schema", "exec", "验证输入参数")

    save(dot, "ch05_tool_spec")


def ch05_file_ops_flow():
    """第5章: 文件操作流程"""
    dot = make_dot("ch05_file_ops_flow", "文件操作的完整流程")
    dot.attr(rankdir="TB", nodesep="0.3", ranksep="0.4")

    node(dot, "input", "AI 调用工具\n{tool_name, input}", COLORS["llm"], icon="🤖")
    node(dot, "parse", "反序列化 input\nserde_json::from_value", COLORS["data"], icon="🔍")
    node(dot, "dispatch", "match name 分发\n\"read_file\" → run_read_file()", COLORS["core"], icon="🔀")
    node(dot, "exec", "执行底层函数\nfile_ops::read_file()", COLORS["tool"], icon="⚡")
    node(dot, "result", "返回结构化输出\nReadFileOutput (JSON)", COLORS["user"], icon="📤")

    edge(dot, "input", "parse")
    edge(dot, "parse", "dispatch")
    edge(dot, "dispatch", "exec")
    edge(dot, "exec", "result")

    save(dot, "ch05_file_ops_flow")


# ── 第6章配图 ──────────────────────────────────────────────

def ch06_message_model():
    """第6章: 消息模型结构"""
    dot = make_dot("ch06_message_model", "消息模型: Session → Message → ContentBlock")
    dot.attr(rankdir="TB", nodesep="0.4", ranksep="0.4")

    node(dot, "session", "Session\n{version, messages}", COLORS["core"])
    node(dot, "msg1", "ConversationMessage\nrole: User\nblocks: [...]", COLORS["user"])
    node(dot, "msg2", "ConversationMessage\nrole: Assistant\nblocks: [...] + usage", COLORS["llm"])
    node(dot, "msg3", "ConversationMessage\nrole: Tool\nblocks: [...]", COLORS["tool"])

    node(dot, "text", "ContentBlock::Text\n{text: \"内容\"}", COLORS["data"])
    node(dot, "tooluse", "ContentBlock::ToolUse\n{id, name, input}", COLORS["tool"])
    node(dot, "toolresult", "ContentBlock::ToolResult\n{tool_use_id, tool_name,\n output, is_error}", COLORS["security"])

    edge(dot, "session", "msg1", "messages[0]")
    edge(dot, "session", "msg2", "messages[1]")
    edge(dot, "session", "msg3", "messages[2]")
    edge(dot, "msg1", "text", "blocks[0]")
    edge(dot, "msg2", "text", "blocks[0]")
    edge(dot, "msg2", "tooluse", "blocks[1]")
    edge(dot, "msg3", "toolresult", "blocks[0]")

    save(dot, "ch06_message_model")


def ch06_conversation_flow():
    """第6章: 一次对话的消息流"""
    dot = make_dot("ch06_conversation_flow", "消息在对话中的流转")
    dot.attr(rankdir="TB", nodesep="0.3", ranksep="0.3")

    node(dot, "u1", "User: \"读取 main.py\"", COLORS["user"])
    node(dot, "a1", "Assistant: \"让我看看\"\n[Text + ToolUse(Read)]", COLORS["llm"])
    node(dot, "t1", "Tool: read_file → \"内容...\"", COLORS["tool"])
    node(dot, "a2", "Assistant: \"文件有 3 个 bug\"\n[Text]", COLORS["llm"])

    edge(dot, "u1", "a1", "AI 思考")
    edge(dot, "a1", "t1", "执行工具")
    edge(dot, "t1", "a2", "AI 再思考")
    edge(dot, "a2", "done", label="", style="invis")

    node(dot, "done", "对话结束", COLORS["user"], shape="oval", icon="✅")

    save(dot, "ch06_conversation_flow")


def ch06_serialization():
    """第6章: 序列化流程"""
    dot = make_dot("ch06_serialization", "Session 的保存和加载")
    dot.attr(rankdir="LR", nodesep="0.4", ranksep="0.4")

    node(dot, "session", "Session\n(Rust 结构体)", COLORS["core"])
    node(dot, "json", "JsonValue\n(内存中的 JSON)", COLORS["data"])
    node(dot, "string", "JSON 字符串\n\"{version:1,...}\"", COLORS["llm"])
    node(dot, "file", "磁盘文件\nsession-xxx.json", COLORS["tool"])

    edge(dot, "session", "json", "to_json()")
    edge(dot, "json", "string", "render()")
    edge(dot, "string", "file", "fs::write()")
    edge(dot, "file", "string", "fs::read_to_string()")
    edge(dot, "string", "json", "JsonValue::parse()")
    edge(dot, "json", "session", "from_json()")

    save(dot, "ch06_serialization")


# ── 第7章配图 ──────────────────────────────────────────────

def ch07_three_modes():
    """第7章: 权限三种模式"""
    dot = make_dot("ch07_three_modes", "权限系统的三种模式")
    dot.attr(rankdir="TB", nodesep="0.4", ranksep="0.4")

    node(dot, "check", "AI 想调用工具\nauthorize(tool_name, input)", COLORS["core"])

    node(dot, "allow", "Allow 模式\n自动放行\n所有操作", COLORS["tool"])
    node(dot, "deny", "Deny 模式\n自动拒绝\n所有操作", "#E74C3C")
    node(dot, "prompt", "Prompt 模式\n询问用户\n你来决定", COLORS["user"])

    node(dot, "yes", "用户同意\n→ 执行", COLORS["tool"])
    node(dot, "no", "用户拒绝\n→ 返回拒绝原因", "#E74C3C")

    edge(dot, "check", "allow", "mode_for(tool_name)")
    edge(dot, "check", "deny", "")
    edge(dot, "check", "prompt", "")
    edge(dot, "prompt", "yes", "Allow")
    edge(dot, "prompt", "no", "Deny { reason }")

    save(dot, "ch07_three_modes")


def ch07_policy_layers():
    """第7章: 权限策略的分层"""
    dot = make_dot("ch07_policy_layers", "PermissionPolicy: 先查工具级，再查默认级")
    dot.attr(rankdir="TB", nodesep="0.3", ranksep="0.3")

    node(dot, "lookup", "mode_for(\"bash\")", COLORS["core"])
    node(dot, "specific", "tool_modes BTreeMap\n{\"bash\": Prompt,\n \"read\": Allow,\n \"edit\": Deny}", COLORS["data"])
    node(dot, "found", "找到了!\n返回 Prompt", COLORS["user"])
    node(dot, "default", "default_mode\n全局默认\n(Deny / Prompt / Allow)", COLORS["llm"])
    node(dot, "result", "最终模式", COLORS["tool"])

    edge(dot, "lookup", "specific", "先查工具级")
    edge(dot, "specific", "found", "有 → 用工具级")
    edge(dot, "specific", "default", "没有 → 用默认级")
    edge(dot, "found", "result")
    edge(dot, "default", "result")

    save(dot, "ch07_policy_layers")


def ch07_auth_flow():
    """第7章: 完整权限检查流程"""
    dot = make_dot("ch07_auth_flow", "authorize() 的完整流程")
    dot.attr(rankdir="TB", nodesep="0.3", ranksep="0.4")

    node(dot, "start", "工具调用请求\ntool_name, input", COLORS["user"])
    node(dot, "mode", "mode_for(tool_name)\n确定权限模式", COLORS["core"])
    node(dot, "is_allow", "Allow?", COLORS["tool"], shape="diamond")
    node(dot, "is_deny", "Deny?", "#E74C3C", shape="diamond")
    node(dot, "prompter", "有 prompter 吗?", COLORS["user"], shape="diamond")
    node(dot, "ask_user", "prompter.decide()\n询问用户", COLORS["user"])
    node(dot, "user_yes", "用户同意", COLORS["tool"])
    node(dot, "user_no", "用户拒绝", "#E74C3C")
    node(dot, "no_prompter", "没有 prompter\n无法询问", "#E74C3C")
    node(dot, "ok", "PermissionOutcome::Allow", COLORS["tool"])
    node(dot, "err", "PermissionOutcome::Deny\n{ reason }", "#E74C3C")

    edge(dot, "start", "mode")
    edge(dot, "mode", "is_allow")
    edge(dot, "is_allow", "ok", "是")
    edge(dot, "is_allow", "is_deny", "否")
    edge(dot, "is_deny", "err", "是")
    edge(dot, "is_deny", "prompter", "否 → Prompt")
    edge(dot, "prompter", "ask_user", "有")
    edge(dot, "ask_user", "user_yes", "Allow")
    edge(dot, "ask_user", "user_no", "Deny")
    edge(dot, "user_yes", "ok")
    edge(dot, "user_no", "err")
    edge(dot, "prompter", "no_prompter", "没有")
    edge(dot, "no_prompter", "err")

    save(dot, "ch07_auth_flow")


# ── 第8章配图 ──────────────────────────────────────────────

def ch08_bootstrap_phases():
    """第8章: Bootstrap 12 阶段"""
    dot = make_dot("ch08_bootstrap_phases", "从输入 claude 到出现提示符：12 个阶段")
    dot.attr(rankdir="TB", nodesep="0.15", ranksep="0.15")

    phases = [
        ("p1", "1. CliEntry\n命令行入口", COLORS["user"]),
        ("p2", "2. FastPathVersion\n版本检查", COLORS["data"]),
        ("p3", "3. StartupProfiler\n性能分析启动", COLORS["data"]),
        ("p4", "4. SystemPromptFastPath\n快速构建 System Prompt", COLORS["llm"]),
        ("p5", "5. ChromeMcpFastPath\nMCP 浏览器通道", COLORS["tool"]),
        ("p6", "6. DaemonWorkerFastPath\n后台工作进程", COLORS["tool"]),
        ("p7", "7. BridgeFastPath\n桥接通信", COLORS["data"]),
        ("p8", "8. DaemonFastPath\n守护进程", COLORS["tool"]),
        ("p9", "9. BackgroundSessionFastPath\n后台会话", COLORS["data"]),
        ("p10", "10. TemplateFastPath\n模板加载", COLORS["llm"]),
        ("p11", "11. EnvironmentRunnerFastPath\n环境配置", COLORS["security"]),
        ("p12", "12. MainRuntime\n进入主循环!", COLORS["core"]),
    ]
    for nid, label, color in phases:
        node(dot, nid, label, color, shape="box")

    for i in range(len(phases) - 1):
        edge(dot, phases[i][0], phases[i+1][0])

    save(dot, "ch08_bootstrap_phases")


def ch08_fastpath_concept():
    """第8章: Fast Path 概念"""
    dot = make_dot("ch08_fastpath_concept", "Fast Path: 短路快速通道")
    dot.attr(rankdir="LR", nodesep="0.4", ranksep="0.5")

    node(dot, "entry", "用户输入\nclaude --version", COLORS["user"])
    node(dot, "check", "FastPath 阶段\n检查是否可以\n提前退出?", COLORS["core"], shape="diamond")
    node(dot, "fast", "Fast Path 退出!\n只执行必要阶段\n立即返回", COLORS["tool"])
    node(dot, "full", "完整启动流程\n执行所有 12 阶段\n进入主循环", COLORS["llm"])

    edge(dot, "entry", "check")
    edge(dot, "check", "fast", "可以提前退出", color=COLORS["tool"])
    edge(dot, "check", "full", "需要完整启动", color=COLORS["llm"])

    save(dot, "ch08_fastpath_concept")


# ── 第9章配图 ──────────────────────────────────────────────

def ch09_session_lifecycle():
    """第9章: Session 生命周期"""
    dot = make_dot("ch09_session_lifecycle", "Session 的完整生命周期")
    dot.attr(rankdir="TB", nodesep="0.3", ranksep="0.3")

    node(dot, "create", "创建 Session\nnew() → 空会话", COLORS["core"])
    node(dot, "use", "使用中\nrun_turn() × N", COLORS["llm"])
    node(dot, "save", "保存到磁盘\nsave_to_path()", COLORS["tool"])
    node(dot, "disk", "磁盘文件\nsession-xxx.json", COLORS["data"])
    node(dot, "load", "恢复会话\nload_from_path()", COLORS["user"])
    node(dot, "compact", "对话压缩\ncompact() → 新 Session", COLORS["security"])

    edge(dot, "create", "use")
    edge(dot, "use", "save", "主动保存")
    edge(dot, "use", "compact", "token 太多")
    edge(dot, "save", "disk")
    edge(dot, "disk", "load", "下次启动")
    edge(dot, "load", "use")
    edge(dot, "compact", "use", "继续对话")

    save(dot, "ch09_session_lifecycle")


def ch09_persistence_pattern():
    """第9章: 持久化模式"""
    dot = make_dot("ch09_persistence_pattern", "持久化: 内存 ↔ 磁盘的转换")
    dot.attr(rankdir="LR", nodesep="0.3", ranksep="0.3")

    node(dot, "mem", "内存\nSession 结构体\nRust 对象", COLORS["core"])
    node(dot, "json", "JSON\nJsonValue 树\n中间表示", COLORS["data"])
    node(dot, "file", "磁盘\nsession.json\n文本文件", COLORS["tool"])

    edge(dot, "mem", "json", "to_json()", color=COLORS["tool"])
    edge(dot, "json", "file", "render() + fs::write()", color=COLORS["tool"])
    edge(dot, "file", "json", "fs::read() + parse()", color=COLORS["user"])
    edge(dot, "json", "mem", "from_json()", color=COLORS["user"])

    save(dot, "ch09_persistence_pattern")


# ── 第10章配图 ─────────────────────────────────────────────

def ch10_compact_before_after():
    """第10章: 压缩前后对比"""
    dot = make_dot("ch10_compact_before_after", "对话压缩: 把长历史变成短摘要")
    dot.attr(rankdir="TB", nodesep="0.2", ranksep="0.3")

    with dot.subgraph(name="cluster_before") as c:
        c.attr(style="filled", fillcolor="#FDEBD0", label="压缩前（500+ tokens）", fontname="Arial", fontsize="13")
        node(c, "b1", "User: \"帮我改 bug\"", COLORS["user"])
        node(c, "b2", "Assistant: Text + ToolUse", COLORS["llm"])
        node(c, "b3", "Tool: read_file → ...", COLORS["tool"])
        node(c, "b4", "Assistant: Text + ToolUse", COLORS["llm"])
        node(c, "b5", "Tool: edit_file → ...", COLORS["tool"])
        node(c, "b6", "Assistant: \"改好了\"", COLORS["llm"])
        node(c, "b7", "User: \"测试一下\"", COLORS["user"])
        node(c, "b8", "Assistant: \"测试通过\" ✅", COLORS["llm"])

    with dot.subgraph(name="cluster_after") as c:
        c.attr(style="filled", fillcolor="#D5F5E3", label="压缩后（~200 tokens）", fontname="Arial", fontsize="13")
        node(c, "a1", "System: 摘要\n\"之前帮用户改了 bug,\n修改了 main.py,\n测试通过\"", COLORS["core"])
        node(c, "a2", "User: \"测试一下\"", COLORS["user"])
        node(c, "a3", "Assistant: \"测试通过\" ✅", COLORS["llm"])

    edge(dot, "b8", "a1", "compact_session()", style="dashed", color=COLORS["core"])

    save(dot, "ch10_compact_before_after")


def ch10_compact_algorithm():
    """第10章: 压缩算法流程"""
    dot = make_dot("ch10_compact_algorithm", "compact_session() 的算法流程")
    dot.attr(rankdir="TB", nodesep="0.3", ranksep="0.3")

    node(dot, "start", "Session\n(可能很长)", COLORS["user"])
    node(dot, "check", "should_compact()?\n消息数 > preserve_recent\n且 tokens >= max?", COLORS["core"], shape="diamond")
    node(dot, "noop", "不需要压缩\n直接返回", COLORS["data"])
    node(dot, "split", "分割消息列表\n旧消息 + 近期消息", COLORS["llm"])
    node(dot, "summarize", "summarize_messages()\n生成摘要", COLORS["data"])
    node(dot, "build", "构建新 Session\n[System 摘要] + [近期消息]", COLORS["tool"])
    node(dot, "result", "CompactionResult\n{summary, compacted_session}", COLORS["user"])

    edge(dot, "start", "check")
    edge(dot, "check", "noop", "否")
    edge(dot, "check", "split", "是")
    edge(dot, "split", "summarize", "旧消息 → 摘要")
    edge(dot, "summarize", "build")
    edge(dot, "split", "build", "近期消息 → 原样保留", style="dashed")
    edge(dot, "build", "result")

    save(dot, "ch10_compact_algorithm")


# ── 第11章配图 ─────────────────────────────────────────────

def ch11_token_breakdown():
    """第11章: Token 用量构成"""
    dot = make_dot("ch11_token_breakdown", "TokenUsage: 四种 token 类型")
    dot.attr(rankdir="LR", nodesep="0.4", ranksep="0.4")

    node(dot, "req", "一次 API 请求", COLORS["core"])
    node(dot, "input", "input_tokens\n你的输入\n(含聊天记录)", COLORS["user"])
    node(dot, "output", "output_tokens\nAI 的输出\n(文字+工具调用)", COLORS["llm"])
    node(dot, "cache_w", "cache_creation\n首次缓存\n(第一次发送时)", COLORS["data"])
    node(dot, "cache_r", "cache_read\n缓存命中\n(重复内容时)", COLORS["tool"])

    edge(dot, "req", "input")
    edge(dot, "req", "output")
    edge(dot, "req", "cache_w")
    edge(dot, "req", "cache_r")

    save(dot, "ch11_token_breakdown")


def ch11_pricing_comparison():
    """第11章: 三种模型定价对比"""
    dot = make_dot("ch11_pricing_comparison", "三种模型的定价对比 ($/百万 token)")
    dot.attr(rankdir="TB", nodesep="0.2", ranksep="0.2")

    node(dot, "haiku", "Haiku\n输入: $1 / 输出: $5\n最便宜，最快", "#2ECC71")
    node(dot, "sonnet", "Sonnet\n输入: $15 / 输出: $75\n均衡", "#F39C12")
    node(dot, "opus", "Opus\n输入: $15 / 输出: $75\n最强，最慢", "#E74C3C")

    edge(dot, "haiku", "sonnet", "15x 更贵")
    edge(dot, "sonnet", "opus", "同价但更强")

    save(dot, "ch11_pricing_comparison")


# ── 第12章配图 ─────────────────────────────────────────────

def ch12_mcp_naming():
    """第12章: MCP 工具命名规则"""
    dot = make_dot("ch12_mcp_naming", "MCP 工具命名: mcp__{server}__{tool}")
    dot.attr(rankdir="LR", nodesep="0.4", ranksep="0.3")

    node(dot, "raw", "原始名称\nserver: \"github.com\"\ntool: \"create issue\"", COLORS["user"])
    node(dot, "norm", "名称规范化\ngithub_com\ncreate_issue", COLORS["data"])
    node(dot, "full", "完整工具名\nmcp__github_com__create_issue", COLORS["tool"])

    edge(dot, "raw", "norm", "normalize_name_for_mcp()")
    edge(dot, "norm", "full", "mcp_tool_name()")

    save(dot, "ch12_mcp_naming")


def ch12_transport_types():
    """第12章: MCP 传输类型"""
    dot = make_dot("ch12_transport_types", "MCP 的 6 种传输类型")
    dot.attr(rankdir="LR", nodesep="0.3", ranksep="0.3")

    node(dot, "client", "MCP Client\n(Claude Code)", COLORS["core"])

    node(dot, "stdio", "Stdio\n标准输入输出\n本地进程", COLORS["tool"])
    node(dot, "sse", "SSE\nServer-Sent Events\nHTTP 长连接", COLORS["llm"])
    node(dot, "http", "HTTP\nHTTP 请求\n无状态", COLORS["user"])
    node(dot, "ws", "WebSocket\n双向通信\n实时", COLORS["data"])
    node(dot, "proxy", "ClaudeAiProxy\n代理转发\n云端集成", COLORS["security"])
    node(dot, "sdk", "SDK\n嵌入式\n编程接口", "#9B59B6")

    edge(dot, "client", "stdio")
    edge(dot, "client", "sse")
    edge(dot, "client", "http")
    edge(dot, "client", "ws")
    edge(dot, "client", "proxy")
    edge(dot, "client", "sdk")

    save(dot, "ch12_transport_types")


# ── 主入口 ──────────────────────────────────────────────

ALL_DIAGRAMS = {
    # 第1章
    "ch01_three_elements": ch01_agent_three_elements,
    "ch01_react_loop": ch01_react_loop,
    "ch01_evolution": ch01_evolution,
    # 第2章
    "ch02_full_journey": ch02_full_journey,
    "ch02_six_stages": ch02_six_stages,
    "ch02_crates": ch02_crate_architecture,
    # 第3章
    "ch03_prompt_layers": ch03_prompt_layers,
    "ch03_claude_md_discovery": ch03_claude_md_discovery,
    "ch03_budget": ch03_budget,
    # 第4章
    "ch04_loop_overview": ch04_loop_overview,
    "ch04_run_turn_dataflow": ch04_run_turn_dataflow,
    "ch04_event_types": ch04_event_types,
    # 第5章
    "ch05_tool_categories": ch05_tool_categories,
    "ch05_tool_spec": ch05_tool_spec,
    "ch05_file_ops_flow": ch05_file_ops_flow,
    # 第6章
    "ch06_message_model": ch06_message_model,
    "ch06_conversation_flow": ch06_conversation_flow,
    "ch06_serialization": ch06_serialization,
    # 第7章
    "ch07_three_modes": ch07_three_modes,
    "ch07_policy_layers": ch07_policy_layers,
    "ch07_auth_flow": ch07_auth_flow,
    # 第8章
    "ch08_bootstrap_phases": ch08_bootstrap_phases,
    "ch08_fastpath_concept": ch08_fastpath_concept,
    # 第9章
    "ch09_session_lifecycle": ch09_session_lifecycle,
    "ch09_persistence_pattern": ch09_persistence_pattern,
    # 第10章
    "ch10_compact_before_after": ch10_compact_before_after,
    "ch10_compact_algorithm": ch10_compact_algorithm,
    # 第11章
    "ch11_token_breakdown": ch11_token_breakdown,
    "ch11_pricing_comparison": ch11_pricing_comparison,
    # 第12章
    "ch12_mcp_naming": ch12_mcp_naming,
    "ch12_transport_types": ch12_transport_types,
}

# ── 别名映射 ──────────────────────────────────────────────

def ch04_loop_overview():
    pass


def main():
    if len(sys.argv) < 2:
        print("用法: python3 draw.py <图名>")
        print(f"可用的图: {', '.join(ALL_DIAGRAMS.keys())}")
        print("或: python3 draw.py all  (生成所有图)")
        sys.exit(1)

    name = sys.argv[1]
    if name == "all":
        for n, fn in ALL_DIAGRAMS.items():
            fn()
    elif name in ALL_DIAGRAMS:
        ALL_DIAGRAMS[name]()
    else:
        print(f"未知的图名: {name}")
        print(f"可用的图: {', '.join(ALL_DIAGRAMS.keys())}")
        sys.exit(1)


if __name__ == "__main__":
    main()
