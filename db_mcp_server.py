from datetime import datetime
from typing import Dict, Any
import json

from mcp.server.fastmcp import FastMCP

from business.db.test_case import TestCase
from business.db.test_result import TestResult
from business.db.test_template_step import TestTemplateStep

# 初始化 FastMCP 服务器
mcp = FastMCP("database-server")

@mcp.tool(description="获取当前时间")
def get_current_time() -> datetime:
    return datetime.now()

@mcp.tool(description="将测试结果保存到测试结果表flow.t_test_result")
def save_test_case_result(test_result_id: int
                          ,result_ok: int
                          ,error_step_id: int = None
                          ,error_step_name: str = None
                          ,error_info: str = None) -> str:
    """
    将测试结果保存到测试结果表flow.t_test_result。

    参数:
    test_result_id (int): 测试用例结果ID
    result_ok (int): 测试结果；0:未通过，1：通过
    error_step_id (int, optional): 测试用例报错步骤ID
    error_step_name (int, optional): 测试用例报错步骤名称
    error_info (str, optional): 报错内容

    返回:
    str: JSON格式的操作结果信息
    """
    result = TestResult.update(test_result_id,{
                            "RESULT_OK" : result_ok
                           ,"ERROR_STEP_ID" : error_step_id
                           ,"ERROR_STEP_NAME": error_step_name
                           , "ERROR_INFO" : error_info
                                })

    return json.dumps(result)


@mcp.tool(description="获取测试步骤")
def get_test_template_steps(test_result_id: int) -> str:
    """
    获取测试用例的所有测试步骤，按TEST_ORDER排序。

    参数:
    test_result_id (int): 测试结果ID

    返回:
    str: JSON格式的测试模板步骤信息
    """
    test_result = TestResult.get_by_id(test_result_id)["data"]
    params = json.loads(test_result["PARAMS"])
    test_case = TestCase.get_by_id(test_result["TEST_CASE_ID"])["data"]

    result = TestTemplateStep.get_by_test_template_id(test_case["TEST_TEMPLATE_ID"])
    if not result["success"] :
        return ""
    steps = result["data"]["records"]

    for step in steps :
        step["TEST_CONTENT"] = step["TEST_CONTENT"].format(**params)
    print("测试步骤信息：")
    print(steps)
    return json.dumps(steps, ensure_ascii=False)

# ===== 主程序入口 =====
if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='stdio')