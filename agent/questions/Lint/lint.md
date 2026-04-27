# Lint 是什么？

## 一句话概括

**Lint** 是静态代码分析工具，用于在不运行代码的情况下检查代码中的潜在错误、不良风格、可疑结构，帮助你在 bug 被触发之前发现它们。

"Lint" 这个名字来源于 C 语言历史上的一个工具 `lint`（1980 年代），它像衣服上的毛絮（不是线本身的问题），比喻代码中微小但有问题的瑕疵。

---

## 用类比理解

> **Linter 就像文字处理软件中的拼写检查和语法检查。**
>
> 你写了一段英文："I has went to the store." —— 语法检查会立刻告诉你：
> - "has" 和 "went" 搭配有问题（潜在 bug）
> - 建议改成 "I have gone..."（建议修复）
>
> 它不用运行程序，不用等待编译，你还在打字的时候就告诉你了。这就是 linter 做的事情。

---

## 常见 Linter 工具（按语言）

| 语言 | 常用 Linter | 说明 |
|------|------------|------|
| JavaScript/TypeScript | **ESLint** | 事实标准，可配置规则、自动修复 |
| Python | **Ruff** / **Flake8** / **Pylint** | Ruff 是最新且最快的（Rust 编写） |
| Go | **staticcheck** / `go vet` | Go 内置 `go vet`，staticcheck 更全面 |
| Rust | **clippy** | 官方维护，集成在 Rust 工具链中 |
| Dockerfile | **hadolint** | 检查 Dockerfile 最佳实践 |

---

## 它能检查什么？（举例）

Linter 发现的问题可以分为几个层次：

### 1. 可能的 Bug（最重要）
```python
# Python 示例
if user = "admin":  # 应该是 ==，写成了 =
    print("hello")

# linter 会警告：可能是赋值错误，你确定想在这里赋值吗？
```

```go
// Go 示例
defer db.Close()  // 某些 linter 还能检查你是否忘了检查 error
```

### 2. 反模式 / 代码坏味
```python
# 用了可变对象作为默认参数
def add_item(item, lst=[]):  # 所有调用共享同一个列表！
    lst.append(item)
    return lst

# linter 会建议改为 lst=None 并在内部初始化
```

### 3. 风格一致性
```python
# 不一致的缩进
def hello():
	print("tab")
    print("spaces")  # 混用了 tab 和 space

# 未使用的变量
def calc(a, b):
    result = a + b
    return a  # 是不是忘记返回 result 了？
```

### 4. 复杂度警告
```python
# 函数太长了
def handle_request(data):  # 100 行...
    # linter 会警告：函数圈复杂度过高，建议拆分

# import 未使用
import os, sys, json, datetime  # 其中 json 和 datetime 根本没用到
```

---

## Linter vs Formatter（两者常被混淆）

| | Linter | Formatter |
|--|--------|-----------|
| 目的 | 发现问题和风险 | 统一格式风格 |
| 举例 | ESLint | Prettier |
| 检查 | 未使用变量、潜在 bug、反模式 | 缩进、括号换行、分号 |
| 是否可能发现 bug | ✅ 是 | ❌ 几乎不 |
| 能自动修复 | 部分可以 | 几乎所有可以 |

**最佳实践：linter + formatter 配合使用**。Formatter 管长相，Linter 管健康。

---

## 在编辑器中的体验（最常用的方式）

在 VS Code 中安装相应语言的 linter 插件后：

- 你在输入时，代码下方会出现波浪线（红色=错误，黄色=警告）
- 鼠标悬停会看到具体问题描述和建议
- 保存文件时自动修复部分问题
- 有些问题旁边会有"快速修复"链接

**你不需要刻意"运行"linter，它在你写代码时就默默工作。**

---

## 在 CI/CD 中的使用

除了编辑器中使用，项目通常还会在 CI（如 GitHub Actions）中运行 Linter：

```yaml
# 伪代码 - CI 流程
steps:
  - run: npm run lint   # 如果 lint 有错误，CI 构建失败
  - run: npm test       # 只有 lint 通过后才运行测试
```

这样做的好处是：**即使开发者本地忘了检查，CI 也会拦住有问题的代码。**

---

## Linter 的两面性

### 优点
- 在开发阶段发现 bug，而非线上
- 强制执行团队代码规范
- 减少代码审查中关于风格的争论
- 对新手友好，自动指出常见错误

### 需要注意的
- **规则太多可能让人烦躁** —— 新项目可以渐进式启用规则
- **有时误报** —— 不是你代码有问题，而是 linter 规则太严格
- **过度配置** —— 不要把时间花在微调规则上，够用就好
- **不要完全信 linter** —— 它只能发现模式匹配的问题，不是所有 bug

---

## Rust 中的参考（你感兴趣的话）

Rust 的 `clippy` 是 linter 的典范。它不仅是检查工具，还被当作学习工具：

```rust
// 不好的写法
let x = 1 + 2;
if x == 3 {  // clippy 会建议：对于简单计算，直接写结果更好
    ...
}

// clippy 会给出带"为什么这样更好"的解释
// 甚至有小黄鸭（Clippy）吉祥物
```

---

## 总结

| 角度 | 理解 |
|------|------|
| 是什么 | 静态分析工具，检查代码问题 |
| 做什么 | 发现潜在 bug、反模式、风格问题 |
| 何时用 | 写代码时（编辑器）+ 提交前（CI） |
| 典型工具 | ESLint（JS）、Ruff（Python）、staticcheck（Go）、clippy（Rust） |

**一句话**：Linter 是你代码的"体检医生"，在你感觉到问题之前就告诉你哪里可能有风险。
