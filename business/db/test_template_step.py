from typing import Dict, List, Any
from business.db.base_model import BaseModel


class TestTemplateStep(BaseModel):
    """
    测试用例步骤模型
    """
    
    # 表名
    table_name = "flow.t_test_template_step"
    
    # 主键字段名
    primary_key = "TEST_TEMPLATE_STEP_ID"
    
    # 字段列表
    fields = [
        "TEST_TEMPLATE_STEP_ID",
        "TEST_TEMPLATE_ID",
        "TEST_TEMPLATE_STEP_NAME",
        "TEST_ORDER",
        "TEST_CONTENT",
        "HTML_SELECTOR",
        "EXPECTED_RESULT",
        "IS_DELETED",
        "CREATE_TIME",
        "CREATE_USER",
        "UPDATE_TIME",
        "UPDATE_USER"
    ]
    
    # 必填字段列表
    required_fields = [
    ]
    
    @classmethod
    def get_by_test_template_id(cls, test_template_id: int) -> Dict[str, Any]:
        """
        根据测试模板ID获取所有步骤
        
        参数:
            test_template_id: 测试用例ID
            
        返回:
            Dict: 包含操作结果的字典
        """
        result = cls.get_all(
            where_clause="TEST_TEMPLATE_ID = %s",
            params=(test_template_id,),
            order_clause="TEST_ORDER",
            limit=1000  # 设置一个较大的限制，确保获取所有步骤
        )
        
        # 如果获取成功，按步骤顺序排序
        if result["success"] and result["data"]["records"]:
            result["data"]["records"] = sorted(
                result["data"]["records"],
                key=lambda x: x.get("STEP_ORDER", 0)
            )
        
        return result

