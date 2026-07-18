# REST HTTP Errors

只在项目存在 REST HTTP adapter 和稳定客户端错误契约时使用本参考。

## 状态码

- 成功使用合适的 `2xx`。
- 客户端输入、权限、资源不存在和状态冲突等可预期错误使用对应 `4xx`。
- 服务端内部错误使用 `5xx`，不向客户端暴露内部错误详情。

## 稳定错误码

响应 body 使用稳定的 `SCREAMING_SNAKE_CASE` 错误码和必要上下文字段：

```json
{
  "code": "PROBLEM_NOT_FOUND",
  "problem_id": "123"
}
```

客户端使用 `code` 查找文案模板；服务端记录可排障的详细错误。

需要多语言客户端文案时，在项目根目录按语言维护资源：

```text
locales/
  zh-CN/
    errors.json
  en-US/
    errors.json
```

`errors.json` 直接使用错误码作为 key：

```json
{
  "PROBLEM_NOT_FOUND": "题目 {problem_id} 不存在"
}
```
