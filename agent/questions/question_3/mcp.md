# MCP（Model Context Protocol）

## 本质：AI 应用与外部工具/数据/资源之间的开放通信协议

MCP 是 AI 领域的"USB-C"——统一了 AI 模型与外部世界的交互方式。

---

## 解决的问题

### 1. M×N 集成问题（你理解的正确部分）

**没有 MCP 时**，每个模型需要为每个工具单独适配：

```
模型A → 自定义格式 → 工具1
模型A → 自定义格式 → 工具2
模型B → 另一套格式 → 工具1
```

复杂度 = M × N。

**有 MCP 时**，模型只需实现 MCP Client，工具只需实现 MCP Server：

```
模型A → MCP 协议 → MCP Server(工具1)
模型B → MCP 协议 → MCP Server(工具2)
```

复杂度 = M + N。

### 2. 工具调用格式碎片化

不同模型对工具调用的 Context 格式不同（OpenAI 的 function calling、Anthropic 的 tool use），MCP 统一了通信协议本身，使得工具开发者只需实现一次 MCP Server，所有兼容的 AI 应用都可以复用。

---

## 核心原语（不只是工具调用）

MCP 定义了三种交互原语：

| 原语 | 作用 | 类比 |
|------|------|------|
| **Tools** | 模型可以调用的函数/动作 | 你理解的工具调用 |
| **Resources** | 模型可以读取的数据/文件 | REST 中的 GET |
| **Prompts** | 预定义的提示词模板 | 可复用的交互模板 |

---

## 架构概览

```
Host（AI 应用，如 Claude Desktop）
  └── MCP Client（协议实现层）
        ├── MCP Server A（本地, stdio）— 文件系统工具
        ├── MCP Server B（远程, SSE）— GitHub API
        └── MCP Server C（本地, stdio）— 数据库查询
```

- **Host**：运行 AI 模型和 MCP Client 的应用程序
- **MCP Client**：与 MCP Server 建立一对一连接，处理通信
- **MCP Server**：提供工具、资源、提示词的服务端

---

## 传输层

- **stdio（本地）**：Client 启动 Server 子进程，通过 stdin/stdout 通信，安全且无需网络
- **SSE / Streamable HTTP（远程）**：通过 HTTP 通信，适用于远程服务

---

## 通信协议

底层使用 **JSON-RPC 2.0**，消息格式为标准 JSON。交互流程：

1. **工具发现**：Client 请求 Server 的能力列表（List Tools / Resources / Prompts）
2. **调用执行**：Client 发送调用请求，Server 执行并返回结果
3. **通知**：Server 主动推送状态变更（如资源更新）

---

## 类比理解

| | USB-C | MCP |
|---|---|---|
| 问题 | 每种设备用不同接口 | 每个模型用不同工具调用格式 |
| 方案 | 统一接口标准 | 统一协议标准 |
| 效果 | 一个充电器充所有设备 | 一个协议接入所有工具 |

---

## 补充说明

- MCP 的远程模式使得不同的 AI 应用对相同的工具调用只需要调用唯一的 MCP 服务，而不是一个应用对应一个服务（你理解的第1点）
- MCP 标准化了工具调用的 Context 规范，使得不同模型对同一种工具的调用结果都可以正确解析（你理解的第2点）
- 本地模式同样重要，适用于文件系统、数据库等本地工具的场景

# labuladong
1. 工具描述塞入上下文，模型决定是否要调用，外围程序实际执行工具并将结果喂回上下文。
2. MCP只是将【如何描述工具】【如何调用工具】这些接口标准化了
3. 2024 年 11 月，Anthropic 推出了 MCP（Model Context Protocol，模型上下文协议）。你可以把它理解为 AI 工具领域的「USB-C 标准」：按照 MCP 的规范写一个工具，所有支持 MCP 的 Agent 都能直接接入，不用关心底层是哪家的模型。
