# 第 6 章 Channel 多平台系统

> 20 种方言，一个翻译官，靠的是一份标准化的"通用语言"。

## 6.1 从上一章到这里

上一章我们深入了 Gateway 的内部——WebSocket 和 HTTP 双协议、三种事件流、150ms 节流阀、注册表系统。Gateway 是整个系统的"分拣中心"，所有消息都从这里进出。

但分拣中心不直接接触客户——接触客户的是快递员。在 OpenClaw 里，这些"快递员"就是 Channel（通道）。

Channel 层是 OpenClaw 和外部世界之间的桥梁。它连接着 20 多个消息平台——WhatsApp、Telegram、Discord、Slack、iMessage、Signal、IRC、Google Chat、LINE、微信、飞书、Microsoft Teams、Matrix……每个平台都有自己的"方言"，Channel 层的工作就是把所有方言翻译成一种"通用语言"。

## 6.2 统一接口：适配器模式

### 问题：方言太多

想象你是一个国际会议的翻译。20 个国家的代表各自说母语——有人说英语，有人说中文，有人说阿拉伯语，有人说斯瓦希里语。如果每两个人之间都需要一个专属翻译，你需要 190 个翻译（20 选 2 的组合数）。这显然不可行。

聪明的做法是：**规定一种工作语言，每个人只需要把自己的母语翻译成工作语言就行**。这样只需要 20 个翻译。

OpenClaw 就是这么做的。它规定了一种"通用语言"——`StandardMessage`（标准消息格式），每个 Channel 只需要把自己的平台消息翻译成这种格式。

WhatsApp 的消息长这样：

```json
{
  "from": "8613800138000",
  "body": "今天天气怎么样?",
  "type": "text"
}
```

Telegram 的消息长这样：

```json
{
  "message": {
    "chat": { "id": 123456 },
    "text": "今天天气怎么样?"
  }
}
```

格式完全不同。但经过 Channel 适配器转换后，它们都变成了统一的格式：

```json
{
  "userId": "8613800138000",
  "content": "今天天气怎么样?",
  "timestamp": 1709312345,
  "metadata": { "platform": "whatsapp" }
}
```

Gateway 和 LLM 层只处理这种标准格式，完全不关心消息来自哪个平台。

![](diagrams/ch06_adapter_pattern.png)

### 9 个内置 Channel

从 `src/channels/ids.ts` 源码中可以看到 OpenClaw 内置的 9 个聊天通道：

```typescript
export const CHAT_CHANNEL_ORDER = [
  "telegram",     // Telegram
  "whatsapp",     // WhatsApp
  "discord",      // Discord
  "irc",          // IRC
  "googlechat",   // Google Chat
  "slack",        // Slack
  "signal",       // Signal
  "imessage",     // iMessage
  "line",         // LINE
] as const;
```

这个列表的顺序不是随意的——它定义了多通道同时可用时的优先级。当用户在多个平台上同时发消息时，Telegram 会被优先处理。

除了这 9 个内置通道，OpenClaw 还通过插件（plugin）机制支持更多平台——微信、飞书、Microsoft Teams、Matrix 等。

## 6.3 Channel 插件架构

每个 Channel 不只是一个简单的"翻译函数"，而是一个功能完整的插件（Plugin）。从 `src/channels/plugins/types.ts` 源码中可以看到，每个 Channel 插件可以实现多达 10 种适配器（adapter，即针对特定功能的接口实现）：

| 适配器 | 做什么 | 必需？ |
|--------|--------|--------|
| **MessagingAdapter** | 收发消息 | 是 |
| **DirectoryAdapter** | 查询用户、群组、成员 | 否 |
| **SecurityAdapter** | 解析 DM 安全策略 | 否 |
| **AllowlistAdapter** | 管理白名单 | 否 |
| **PairingAdapter** | 配对认证 | 否 |
| **ExecApprovalAdapter** | 工具执行审批 | 否 |
| **LifecycleAdapter** | 账号配置变更通知 | 否 |
| **CommandAdapter** | 命令处理 | 否 |
| **ResolveAdapter** | 解析目标 ID | 否 |
| **ConfiguredBindingProvider** | 编译和匹配绑定规则 | 否 |

这种设计的关键洞察是：**不是每个 Channel 都需要实现所有功能**。

比如：
- **WhatsApp** 有消息收发、目录查询、配对、白名单，但没有命令适配器
- **IRC** 只有消息收发——它太简单了，不需要配对、白名单这些复杂功能
- **Discord** 几乎全都有——它有丰富的服务器（Guild）、角色（Role）、频道（Channel）概念

每个 Channel 插件只需要实现自己需要的适配器。Gateway 在使用时会检查某个适配器是否存在——如果不存在，就跳过或使用默认行为。

### ChannelPlugin 接口

一个 Channel 插件的核心类型大致如下：

```typescript
type ChannelPlugin = {
  id: string;                    // "telegram", "whatsapp" 等
  messaging?: MessagingAdapter;  // 消息收发
  directory?: DirectoryAdapter;  // 目录查询
  pairing?: PairingAdapter;      // 配对
  security?: SecurityAdapter;    // 安全策略
  allowlist?: AllowlistAdapter;  // 白名单
  // ... 其他可选适配器
};
```

所有适配器都是可选的（用 `?` 标记）。这意味着一个最简单的 Channel 插件只需要一个 `id`——虽然这样它什么也做不了，但至少不会让系统崩溃。

## 6.4 消息路由：谁该被回复

消息从平台进来后，第一个问题不是"怎么回复"，而是"该不该回复"。

### 提及门控（Mention Gating）

在群聊里，如果机器人对每条消息都回复，那简直是一场灾难——想象一下你在一个 500 人的群里，每条消息都会触发机器人的回复。

OpenClaw 用**提及门控**（Mention Gating，即只在被 @ 提及时才回复的机制）来解决这个问题。从 `src/channels/mention-gating.ts` 源码中可以看到核心逻辑：

```typescript
export function resolveMentionGating(params: MentionGateParams): MentionGateResult {
  const implicit = params.implicitMention === true;
  const bypass = params.shouldBypassMention === true;
  const effectiveWasMentioned = params.wasMentioned || implicit || bypass;
  const shouldSkip = params.requireMention && params.canDetectMention && !effectiveWasMentioned;
  return { effectiveWasMentioned, shouldSkip };
}
```

这段代码的逻辑用大白话说就是：

1. **是否被 @ 了？**（`wasMentioned`）
2. **有没有"隐式提及"？**（`implicitMention`）——比如在 Discord 里直接回复机器人的消息
3. **能不能绕过提及检查？**（`bypass`）——比如管理员使用特殊命令
4. **综合判断**：三者取"或"——只要满足一个就算"被提及了"
5. **是否跳过？**：只有在"要求提及"且"能检测提及"且"实际没被提及"时才跳过

还有一个更复杂的版本 `resolveMentionGatingWithBypass`，专门处理群聊中的文本命令场景：

```typescript
const shouldBypassMention =
  params.isGroup &&                          // 在群聊中
  params.requireMention &&                   // 要求提及
  !params.wasMentioned &&                    // 没被提及
  !(params.hasAnyMention ?? false) &&        // 没有任何提及
  params.allowTextCommands &&                // 允许文本命令
  params.commandAuthorized &&                // 命令已授权
  params.hasControlCommand;                  // 包含控制命令
```

这允许在群聊中使用 `/weather 北京` 这样的命令来触发 AI，而不需要先 @ 机器人——前提是命令被授权。

## 6.5 访问控制：谁能和 AI 对话

决定了"该不该回复"之后，下一个问题是"这个用户有权限和 AI 对话吗？"

### DM 策略

对于私聊（DM，Direct Message），OpenClaw 支持 4 种策略：

| 策略 | 含义 | 安全级别 |
|------|------|----------|
| **pairing**（配对） | 需要先配对才能聊天 | 最高 |
| **allowlist**（白名单） | 只有白名单中的用户可以使用 | 高 |
| **open**（开放） | 所有人都可以使用 | 低 |
| **disabled**（禁用） | 关闭私聊功能 | 不适用 |

### 来源白名单

从 `src/channels/allow-from.ts` 源码中可以看到白名单的核心逻辑：

```typescript
export function isSenderIdAllowed(allow, senderId, allowWhenEmpty) {
  if (!allow.hasEntries) return allowWhenEmpty;  // 白名单为空，按默认策略
  if (allow.hasWildcard) return true;             // 有通配符 *，全部放行
  if (!senderId) return false;                    // 没有发送者 ID，拒绝
  return allow.entries.includes(senderId);        // 检查是否在白名单中
}
```

这段代码的精妙之处在于处理了三种边界情况：

1. **白名单为空**：按 `allowWhenEmpty` 参数决定——可能是"全部允许"（白名单为空=没有限制），也可能是"全部拒绝"（白名单为空=没有授权用户）
2. **通配符 `*`**：如果白名单中有 `*`，直接放行——相当于"open"模式
3. **没有发送者 ID**：直接拒绝——如果你连自己是谁都不说，我不会让你进来

群聊的白名单是独立的——群聊有自己的 `groupAllowFrom` 列表，和私聊的白名单互不影响。如果群聊没有设置专门的白名单，默认回退到私聊的白名单（除非配置了 `fallbackToAllowFrom: false`）。

## 6.6 配对机制

配对（Pairing）是 OpenClaw 最安全的认证方式。它要求用户在第一次使用前，通过一种安全的方式（比如扫码、输入配对码）和 Gateway 建立信任关系。

从 `src/channels/plugins/pairing.ts` 源码中可以看到配对的实现：

```typescript
export function listPairingChannels(): ChannelId[] {
  // 只返回支持配对的 Channel
  return listChannelPlugins()
    .filter((plugin) => plugin.pairing)    // 有配对适配器
    .map((plugin) => plugin.id);
}
```

不是所有 Channel 都支持配对——有些平台的技术限制不允许这种认证方式。`listPairingChannels` 函数列出所有支持配对的 Channel。

配对成功后，系统会通知对应的 Channel：

```typescript
export async function notifyPairingApproved(params) {
  const adapter = requirePairingAdapter(params.channelId);
  if (!adapter.notifyApproval) return;
  await adapter.notifyApproval({
    cfg: params.cfg,
    id: params.id,
    runtime: params.runtime,
  });
}
```

这就像你在酒店前台办理入住——前台确认你的身份后，会通知房间服务"这位客人已入住"。Channel 收到配对通过的通知后，就知道"这个用户已经验证过了，后续可以直接对话"。

## 6.7 会话记录

消息经过路由和权限检查后，Channel 层还需要做一件事：记录会话信息。

从 `src/channels/session.ts` 源码中可以看到 `recordInboundSession` 函数的工作流程：

```typescript
export async function recordInboundSession(params) {
  const canonicalSessionKey = normalizeSessionStoreKey(sessionKey);
  // 异步记录会话元数据
  void recordSessionMetaFromInbound({...}).catch(params.onRecordError);
  // 更新最后路由信息（同步等待）
  if (update) {
    if (shouldSkipPinnedMainDmRouteUpdate(update.mainDmOwnerPin)) return;
    await updateLastRoute({...});
  }
}
```

这里有两个关键设计：

1. **Session Key 标准化**：`normalizeSessionStoreKey` 函数把 session key 统一转换为小写并去掉空格。这防止了 "WhatsApp_123" 和 "whatsapp_123" 被当成两个不同的会话。

2. **主 DM Owner 保护**：`shouldSkipPinnedMainDmRouteUpdate` 函数防止非主人的用户"抢占"共享 DM 会话的路由。比如你和朋友共享一个 WhatsApp 号码的 DM 会话，如果朋友的更新把"最后回复路由"指向了他，你就收不到 AI 的回复了。这个保护机制确保只有会话的"主人"才能更新路由。

3. **异步 + 同步混合**：元数据记录是异步的（`void ... .catch()`），不会阻塞主流程；但路由更新是同步的（`await`），因为后续的消息发送依赖正确的路由信息。

## 6.8 目标规范化

不同平台的用户 ID 格式不同。WhatsApp 用电话号码，Telegram 用数字 ID，Discord 用雪花 ID。Channel 层还负责把这些格式各异的 ID 规范化为统一格式。

从 `src/channels/plugins/normalize/` 目录可以看到每个平台都有自己的规范化器：

- `whatsapp.ts`：规范化 WhatsApp 电话号码格式
- `slack.ts`：规范化 Slack 用户和频道 ID
- `signal.ts`：规范化 Signal 电话号码
- `imessage.ts`：规范化 iMessage 的 Apple ID 或电话号码

比如 WhatsApp 的规范化：

```typescript
export function normalizeWhatsAppMessagingTarget(raw: string): string | undefined {
  const trimmed = trimMessagingTarget(raw);
  if (!trimmed) return undefined;
  return normalizeWhatsAppTarget(trimmed) ?? undefined;
}
```

输入可能是 `"+86 138 0013 8000"`、`"8613800138000"` 或 `"whatsapp:+8613800138000"`——这些都要被规范化为统一的格式。

## 6.9 小结

这章我们看了 Channel 层——OpenClaw 连接 20+ 消息平台的桥梁：

1. **适配器模式**：用 `StandardMessage` 统一不同平台的消息格式，Gateway 和 LLM 层不需要关心平台差异
2. **插件架构**：每个 Channel 是一个插件，实现 10 种可选适配器，按需组合
3. **9 个内置 Channel**：Telegram、WhatsApp、Discord、IRC、Google Chat、Slack、Signal、iMessage、LINE
4. **提及门控**：群聊中只在被 @ 或使用授权命令时才回复，防止刷屏
5. **访问控制**：4 种 DM 策略 + 白名单机制 + 通配符支持
6. **配对机制**：最安全的认证方式，通过扫码或配对码建立信任
7. **会话记录**：标准化 session key，保护主 DM owner 路由
8. **目标规范化**：每个平台有专门的 ID 格式规范化器

下一章，我们将深入 Session 管理——OpenClaw 怎么跟踪和管理每个用户的对话状态、怎么把对话历史持久化到磁盘、以及当会话太多时怎么修剪。

---

## 术语速查表

| 术语 | 解释 |
|------|------|
| Adapter | 适配器，把不同接口统一成标准接口的组件 |
| Allow-from | 来源白名单，只允许列表中的发送者触发 AI |
| ChannelPlugin | 通道插件，一个平台的所有适配器集合 |
| DM Policy | 私聊策略，控制谁能通过私聊和 AI 对话 |
| DirectoryAdapter | 目录适配器，查询平台上的用户、群组、成员信息 |
| Implicit mention | 隐式提及，不需要 @ 但仍算作提及的情况（如直接回复） |
| Mention gating | 提及门控，只在被 @ 时才回复的机制 |
| MessagingAdapter | 消息适配器，负责消息的收发 |
| Normalize | 规范化，把不同格式统一为标准格式 |
| Pairing | 配对，通过安全验证建立信任关系的认证方式 |
| Plugin | 插件，可扩展的功能模块 |
| Session key | 会话键，唯一标识一个会话的字符串 |
| StandardMessage | 标准消息，OpenClaw 内部统一的消息格式 |
| Wildcard | 通配符，`*` 匹配所有对象的特殊字符 |
