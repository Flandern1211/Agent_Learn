1.package Agent

import "sync"

// 用户session
type UserSession struct {
	sessionId int
	username  string
}
type AgentState struct {
	session map[string][]*UserSession //用户会话
	mu      sync.RWMutex
}



2.1 代码正确性检查，格式验证，功能测试，单元测试

2.2 不知道

2.3 感觉是规则引擎

2.4 基于三个维度吧，最重要的就是正确性，其次是时间限制，最后是最大迭代次数

1. 我都不太知道

4.1 用户的所有输入都必须完整保存，压缩只针对llm的输出

4.2 当上下文窗口的内容已经是最大的3/4时，或者用户提出要压缩时

4.3 不能

4.3 异步

5.1 不会·

5.2 不会

5.3 不会

5.4 不会