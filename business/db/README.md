# 数据库操作模块

本模块提供了对数据库表的增删改查操作。

## 表结构

本模块支持以下表：

1. `flow.t_test_case` - 测试用例表
2. `flow.t_test_case_step` - 测试用例步骤表
3. `flow.t_test_case_result` - 测试用例结果表

## 使用方法

### 配置数据库连接

在项目根目录的 `.env` 文件中配置数据库连接信息：

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=flow
```

### 导入模块

```python
from business.db import TestCase, TestCaseStep, TestCaseResult
```

### 测试用例操作

#### 创建测试用例

```python
test_case_data = {
    "TEST_CASE_NAME": "测试用例示例",
    "TEST_CASE_USAGE": "这是一个示例测试用例",
    "TEST_CASE_PARAMS": json.dumps({"param1": "value1", "param2": "value2"}),
    "CREATE_USER": "test_user"
}

result = TestCase.create(test_case_data)
```

#### 获取测试用例

```python
# 根据ID获取
result = TestCase.get_by_id(test_case_id)

# 根据名称获取
result = TestCase.get_by_name("测试用例名称")

# 获取所有测试用例
result = TestCase.get_all(limit=10, offset=0)

# 搜索测试用例
result = TestCase.search("关键词", limit=10, offset=0)
```

#### 更新测试用例

```python
update_data = {
    "TEST_CASE_NAME": "更新后的测试用例名称",
    "UPDATE_USER": "test_user"
}

result = TestCase.update(test_case_id, update_data)
```

#### 删除测试用例

```python
# 逻辑删除（默认）
result = TestCase.delete(test_case_id)

# 物理删除
result = TestCase.delete(test_case_id, hard_delete=True)
```

### 测试用例步骤操作

#### 创建测试步骤

```python
step_data = {
    "TEST_CASE_ID": test_case_id,
    "TEST_CASE_STEP_NAME": "步骤名称",
    "STEP_ORDER": 1,
    "TEST_CASE_STEP_CONTENT": "步骤内容",
    "TEST_CASE_STEP_EXPECT": "期望结果",
    "CREATE_USER": "test_user"
}

result = TestCaseStep.create(step_data)
```

#### 获取测试步骤

```python
# 根据ID获取
result = TestCaseStep.get_by_id(step_id)

# 根据测试用例ID获取所有步骤
result = TestCaseStep.get_by_test_case_id(test_case_id)

# 根据测试用例名称获取所有步骤
result = TestCaseStep.get_by_test_case_name("测试用例名称")
```

#### 更新测试步骤

```python
update_data = {
    "TEST_CASE_STEP_CONTENT": "更新后的步骤内容",
    "UPDATE_USER": "test_user"
}

result = TestCaseStep.update(step_id, update_data)
```

#### 重新排序测试步骤

```python
step_orders = [
    {"step_id": 1, "order": 2},
    {"step_id": 2, "order": 1}
]

result = TestCaseStep.reorder_steps(test_case_id, step_orders)
```

#### 删除测试步骤

```python
result = TestCaseStep.delete(step_id)
```

### 测试用例结果操作

#### 创建测试结果

```python
# 成功结果
success_result_data = {
    "TEST_CASE_ID": test_case_id,
    "RESULT_OK": "1",  # 通过
    "CREATE_USER": "test_user"
}

result = TestCaseResult.create(success_result_data)

# 失败结果
failure_result_data = {
    "TEST_CASE_ID": test_case_id,
    "RESULT_OK": "0",  # 未通过
    "ERROR_TEST_CASE_STEP_ID": step_id,
    "ERROR_TEST_CASE_STEP_NAME": "步骤名称",
    "ERROR_INFO": "失败原因",
    "CREATE_USER": "test_user"
}

result = TestCaseResult.create(failure_result_data)

# 带截图的结果
result = TestCaseResult.create_with_screenshot(failure_result_data, "screenshot.png")
```

#### 获取测试结果

```python
# 根据ID获取
result = TestCaseResult.get_by_id(result_id)

# 根据测试用例ID获取所有结果
result = TestCaseResult.get_by_test_case_id(test_case_id, limit=10)

# 获取测试用例的最新结果
result = TestCaseResult.get_latest_by_test_case_id(test_case_id)

# 获取测试结果的截图
result = TestCaseResult.get_screenshot(result_id)
```

#### 更新测试结果

```python
update_data = {
    "ERROR_INFO": "更新后的错误信息",
    "UPDATE_USER": "test_user"
}

result = TestCaseResult.update(result_id, update_data)
```

#### 删除测试结果

```python
result = TestCaseResult.delete(result_id)
```

## 返回值格式

所有方法都返回统一格式的字典：

```python
{
    "success": True/False,  # 操作是否成功
    "message": "操作结果描述",  # 操作结果描述
    "data": {  # 操作返回的数据
        # 具体数据内容
    }
}
```

## 测试

运行测试脚本：

```bash
python -m db.test_db
```
