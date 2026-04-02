<div align="center">

# AI Agent 架构教程

**从零理解 Claude Code 的设计原理**

基于 [instructkr/claw-code](https://github.com/instructkr/claw-code) 仓库源码分析

[开始阅读](01-what-is-agent.md)

</div>

---

## 关于本书

这是一本面向普通人和程序员的 AI Agent 架构教程。你不需要有 Rust 编程经验，也不需要理解所有技术术语——每个专业概念首次出现时，都会用生活比喻来解释。

全书 14 章，从"Agent 是什么"到"用 Python 实现一个 Agent"，层层递进：

| 部分 | 章节 | 内容 |
|------|------|------|
| **入门** | 1-3 | Agent 概念、请求旅程、System Prompt |
| **核心机制** | 4-8 | Agent Loop、工具系统、消息模型、权限系统、启动流程 |
| **高级特性** | 9-12 | Session 持久化、对话压缩、Token 计费、MCP 协议 |
| **实战** | 13-14 | Python 实现最小 Agent、扩展为完整系统 |

## 源码对应关系

本教程所有源码分析来自 [instructkr/claw-code](https://github.com/instructkr/claw-code) —— 一个用 Rust 重写的 Claude Code 干净实现。

| 教程章节 | 源码文件 |
|---------|---------|
| 第3章 System Prompt | `runtime/src/prompt.rs` |
| 第4章 Agent Loop | `runtime/src/conversation.rs` |
| 第5章 工具系统 | `tools/src/lib.rs`、`runtime/src/file_ops.rs`、`runtime/src/bash.rs` |
| 第6章 消息模型 | `runtime/src/session.rs`、`runtime/src/json.rs` |
| 第7章 权限系统 | `runtime/src/permissions.rs` |
| 第8章 启动流程 | `runtime/src/bootstrap.rs`、`rusty-claude-cli/src/main.rs` |
| 第9章 Session 持久化 | `runtime/src/session.rs` |
| 第10章 对话压缩 | `runtime/src/compact.rs` |
| 第11章 Token 计费 | `runtime/src/usage.rs` |
| 第12章 MCP 协议 | `runtime/src/mcp.rs`、`runtime/src/mcp_stdio.rs` |

## 许可

本教程仅供学习交流使用。
