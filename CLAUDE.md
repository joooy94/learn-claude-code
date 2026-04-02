# learn_claude_code

AI Agent 架构教程项目，基于 instructkr/claw-code 仓库。

## 项目状态

正在写一本 14 章的教程，目标 15-20 万字。当前进度：第 1-3 章完成，第 4 章开始写。

### 已完成
- 第1章：Agent 是什么 (`tutorial/01-what-is-agent.md`)
- 第2章：一次请求的完整旅程 (`tutorial/02-request-journey.md`)
- 第3章：System Prompt (`tutorial/03-system-prompt.md`)
- 9 张 Graphviz 配图 (`tutorial/diagrams/`)
- PDF 转换脚本 (`tutorial/build_pdf.py`)

### 待写 (4-14)
- 04: Agent Loop → 05: 工具系统 → 06: 消息模型 → 07: 权限系统 → 08: 启动流程
- 09: Session 持久化 → 10: 对话压缩 → 11: Token 计费 → 12: MCP 协议
- 13: Python 实现最小 Agent → 14: 扩展 Agent

## 写作风格要求

- **目标读者**: 普通人 + 程序员都能看懂
- **通俗优先**: 每个专业术语首次出现时用括号标注简单解释
- **生活比喻多**: 餐厅、厨师、维修师傅等类比贯穿全文
- **过渡自然**: 知识点之间需要过渡段，不能生硬切换
- **章末有术语速查表**
- **配图用 Graphviz**: `draw.py` 生成 PNG，Markdown 中用 `![](diagrams/xxx.png)` 嵌入
- **深度渐进**: 第1-3章入门，4-8章中级（读源码），9-12章高级（算法细节），13-14章实战

## 排版要求

- 最终转 PDF 打印，A4 纸
- 图片最大 140mm 宽 x 100mm 高，按比例缩放，居中显示
- draw.py 设置: `size="7.5,4.5!"`, `dpi=150`, `ratio="fill"`

## claw-code 仓库关键源码

所有源码来自 GitHub instructkr/claw-code，通过 ZRead MCP 读取：

| 文件 | 内容 | 对应章节 |
|------|------|---------|
| `rust/crates/runtime/src/prompt.rs` | System Prompt 构建 | 第3章 ✅ |
| `rust/crates/runtime/src/conversation.rs` | Agent Loop 核心 | 第4章 |
| `rust/crates/runtime/src/tools/` | 工具定义 | 第5章 |
| `rust/crates/runtime/src/session.rs` | 消息模型 & Session | 第6/9章 |
| `rust/crates/runtime/src/permissions.rs` | 权限系统 | 第7章 |
| `rust/crates/runtime/src/bootstrap.rs` | 启动流程 | 第8章 |
| `rust/crates/runtime/src/compact.rs` | 对话压缩 | 第10章 |
| `rust/crates/runtime/src/usage.rs` | Token 计费 | 第11章 |
| `rust/crates/runtime/src/mcp.rs` | MCP 协议 | 第12章 |
| `src/tools.py` | 工具系统(Python层) | 第5章 |

## 关键工具

```bash
cd tutorial
python3 diagrams/draw.py all        # 重新生成所有配图
python3 build_pdf.py 01 02 03       # 指定章节转 PDF
python3 build_pdf.py                 # 全部章节转 PDF
```

已知问题：emoji 显示为方框（STHeiti 字体不支持），后续需要把 Markdown 中的 emoji 替换成文字标签。
