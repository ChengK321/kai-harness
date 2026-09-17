# Governance Validation Freeze — V0.8-D3.6-2

## Alignment：防止契约与实现漂移

```text
Before:
Schema
  |
  v
Validator       两者可能独立漂移

After:
Schema Contract
  |
  v
Alignment Test  必填字段 / risk 枚举 / 禁止字段
  |
  v
Validator
```

标准库 unittest 核对 Schema 声明和 Validator 行为，并检查固定 risk 枚举表达式，
防止实现偷偷增加等级。风险检查实现重构时须同步审阅该测试。
所有对象的封闭字段规则均接受负例检查；静态 import 检查防止新增第三方依赖。
这是指定边界的回归保护，不是完整 JSON Schema 引擎或对所有输入的等价性证明。

## Negative Corpus：拒绝行为冻结

```text
Developer 修改 Validator
          |
          v
       Run Tests
          |
          +----允许危险字段或缺少拒绝原因？----> CI Fail
          |
          v
      全部符合预期 → Tests Pass
```

八个固定 JSON 用例分别覆盖 command、executor、workflow、prompt、伪造审批结构、
高风险免审批、未知属性和非法风险。测试防止空目录假通过，检查 deny、失败项及非空 reason。
现有 API 使用 status=allow/deny；status==allow 为 false 即本测试的拒绝判断。

fake-approval 使用额外的 approved=true 自报批准字段，属于结构非法。
它不表示能够识别结构合法但实际伪造的审批 reference；真实身份与审批真实性仍不在离线范围。

运行（从 apps/kai-governance-validator）：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

本轮不修改 CI 配置；图中 CI Fail 指 CI 运行该测试命令时应以失败退出。

## 边界

Validator 可以发现契约和声明错误，不能授权、执行、审批或修复。
测试通过不代表真实执行安全。Harness、Registry、MCP、Executor 和执行开关均保持不变。
