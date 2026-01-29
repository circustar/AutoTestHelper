from typing import Dict, Any
from business.db.base_model import BaseModel


class TestResult(BaseModel):
    """
    测试用例结果模型
    """
    
    # 表名
    table_name = "flow.t_test_result"
    
    # 主键字段名
    primary_key = "TEST_RESULT_ID"
    
    # 字段列表
    fields = [
        "TEST_RESULT_ID",
        "TEST_CASE_ID",
        "PARAMS",
        "RESULT_OK",
        "ERROR_STEP_ID",
        "ERROR_STEP_NAME",
        "ERROR_INFO",
        "SCREEN_SHOT_PATH",
        "IS_DELETED",
        "CREATE_TIME",
        "CREATE_USER",
        "UPDATE_TIME",
        "UPDATE_USER"
    ]
    
    # 必填字段列表
    required_fields = [
        "TEST_CASE_ID"
    ]

    @classmethod
    def get_by_test_case_id(cls, test_case_id: int, limit: int = 10) -> Dict[str, Any]:
        """
        根据测试用例ID获取测试结果
        
        参数:
            test_case_id: 测试用例ID
            limit: 返回记录数量限制
            
        返回:
            Dict: 包含操作结果的字典
        """
        return cls.get_all(
            where_clause="TEST_CASE_ID = %s",
            params=(test_case_id,),
            limit=limit
        )

    @classmethod
    def get_by_test_template_id(cls, test_template_id: int, limit: int = 10) -> Dict[str, Any]:
        """
        根据测试用例ID获取测试结果

        参数:
            test_case_id: 测试用例ID
            limit: 返回记录数量限制

        返回:
            Dict: 包含操作结果的字典
        """
        return cls.get_all(
            where_clause="TEST_TEMPLATE_ID = %s",
            params=(test_template_id,),
            limit=limit
        )

