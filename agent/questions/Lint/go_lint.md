# Go 中的 Lint 使用

## 核心工具一览

| 工具 | 安装方式 | 作用 |
|------|---------|------|
| `go vet` | Go 内置 | 基础检查，检查可疑构造 |
| `staticcheck` | `go install honnef.co/go/tools/cmd/staticcheck@latest` | 更全面的静态分析 |
| `golangci-lint` | 见下文 | 多种 linter 聚合器（推荐） |

---

## 1. `go vet` —— Go 自带的官方工具

不需要安装，随 Go 一起提供。

```bash
# 检查当前包
go vet

# 检查指定包
go vet ./...

# 详细模式（显示被调用的分析器）
go vet -v ./...
```

**能发现什么问题：**

```go
package main

import "fmt"

func main() {
    // 问题 1：Printf 格式字符串不匹配
    name := "Alice"
    fmt.Printf("Hello %d", name) // go vet: 期望整数，但传入了字符串

    // 问题 2：无意义的赋值（自己赋值给自己）
    var x int
    x = x // go vet: 自己赋值给自己，无意义

    // 问题 3：锁的值传递（复制了互斥锁）
    type SafeCounter struct {
        mu sync.Mutex
    }
    c := SafeCounter{}
    c2 := c // go vet: 复制了包含 sync.Mutex 的值，锁不会被复制
    _ = c2
}
```

`go vet` 是大多数项目的基线 —— 至少保证 `go vet ./...` 通过。

---

## 2. `staticcheck` —— 更强大的第三方检查器

在 `go vet` 基础上增加了更多的检查规则。

```bash
# 安装
go install honnef.co/go/tools/cmd/staticcheck@latest

# 使用（和 go vet 一样的用法）
staticcheck ./...
```

**能发现 `go vet` 发现不了的问题：**

```go
package main

import "fmt"

// 问题 1：未使用的函数参数
func process(a int, b int) int { // staticcheck: b 未使用
    return a * 2
}

// 问题 2：永远不会被执行的代码
func check(x int) int {
    return 1
    fmt.Println("never runs") // 死代码
}

// 问题 3：可以从 error 中忽略掉有用的信息
func do() error {
    return fmt.Errorf("something went wrong") // 建议使用 errors.New 替代（没有格式化的必要）
}
```

---

## 3. `golangci-lint` —— 推荐方案（整合所有 linter）

这是一个 linter 聚合器，运行 50+ 个 linter，还能并行执行。**这是大多数 Go 项目的选择。**

### 安装

```bash
# macOS/Linux（推荐）
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin v1.60.1

# Windows（用 Go install）
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# macOS（Homebrew）
brew install golangci-lint
```

### 基本使用

```bash
# 运行全部启用的 linter
golangci-lint run

# 仅检查改动的文件（节省时间）
golangci-lint run --new-from-rev=HEAD~1

# 快速模式（只运行一部分 linter）
golangci-lint run --fast

# 输出更详细的信息
golangci-lint run -v
```

### 配置文件 `.golangci.yml`

在项目根目录创建此文件，可以精确控制哪些检查开启、哪些关闭：

```yaml
# .golangci.yml
linters:
  # 启用哪些 linter（不写就启用默认集）
  enable:
    - gofmt         # 代码格式
    - govet         # go vet
    - staticcheck   # staticcheck
    - errcheck      # 检查未处理的 error
    - gosimple      # 简化代码的建议
    - ineffassign   # 检查无效赋值
    - unused        # 检查未使用的代码
    - misspell      # 拼写检查

  # 显式禁用某些 linter
  disable:
    - exhaustivestruct  # 太严格，要求结构体所有字段都初始化

linters-settings:
  errcheck:
    # 忽略哪些函数的未处理 error
    exclude-functions:
      - fmt.Println
      - fmt.Fprintf

issues:
  # 排除某些规则的警告
  exclude-rules:
    - path: _test\.go
      linters:
        - errcheck
      text: ".*"  # 测试文件中不对 error 检查那么严格

  # 每行最大长度（某些 linter 需要）
  max-line-length: 120

run:
  # 超时时间
  timeout: 5m
  # 排除某些目录
  skip-dirs:
    - vendor
    - third_party
```

---

## 4. 实际使用场景举例

### 场景 1：VS Code 中自动检查

安装 `golangci-lint` 后，VS Code 的 Go 插件会自动检测并使用它。你会在编辑器中直接看到：

- 红色波浪线 = 错误（必须修复）
- 黄色波浪线 = 警告（建议修复）
- 绿色波浪线 = 风格建议

鼠标悬停即可看到具体问题描述，有些问题可以通过点击"快速修复"自动解决。

### 场景 2：提交前检查（pre-commit hook）

```bash
# 在项目根目录创建 .git/hooks/pre-commit
#!/bin/sh
echo "Running linter..."
golangci-lint run ./...
if [ $? -ne 0 ]; then
    echo "❌ Lint 检查未通过，请修复后再次提交"
    exit 1
fi
```

### 场景 3：CI 中检查

```yaml
# .github/workflows/lint.yml
name: Lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - name: golangci-lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: v1.60
```

---

## 5. 一个完整的工作流

```bash
# 日常开发
go vet ./...        # 快速检查
golangci-lint run   # 全面检查（提交前必须通过）

# 只检查新增/修改的代码（大项目中节省时间）
golangci-lint run --new-from-rev=HEAD~1

# 自动修复一些简单问题
golangci-lint run --fix
```

---

## 6. 常见 Lint 问题及修复（Go 示例）

```go
// ❌ 有问题的代码
package main

import "fmt"   // 未使用的 import

func main() {
    a := 1
    a := 2      // 重复声明
    b := 1
    _ = b       // b 赋值后只使用了一次，考虑直接使用

    data, _ := os.Open("file.txt")  // error 被忽略了
    fmt.Println(data)
}
```

```go
// ✅ 修复后
package main

import "os"

func main() {
    a := 2  // 直接写最终值

    data, err := os.Open("file.txt")
    if err != nil {
        panic(err)
    }
    defer data.Close()
}
```

---

## 总结

| 工具 | 何时用 | 原因 |
|------|--------|------|
| `go vet` | 任何时候 | Go 官方工具，零配置 |
| `staticcheck` | 个人项目 | 比 go vet 检查更全面 |
| `golangci-lint` | **团队项目（推荐）** | 一站式工具，配置灵活，CI 集成方便 |

**推荐做法**：新项目直接配置 `golangci-lint` + `.golangci.yml`，在 CI 中强制检查。已有项目可以从 `go vet` 开始，再逐步引入更严格的检查。
