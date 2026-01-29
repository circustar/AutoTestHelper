from typing import Dict, Any
from business.db.base_model import BaseModel


class TestTemplate(BaseModel):
    """
    测试用例模型
    """
    
    # 表名
    table_name = "flow.t_test_template"
    
    # 主键字段名
    primary_key = "TEST_TEMPLATE_ID"
    
    # 字段列表
    fields = [
        "TEST_TEMPLATE_ID",
        "TEST_TEMPLATE_NAME",
        "USAGE",
        "PARAMS",
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
    def get_by_name(cls, name: str) -> Dict[str, Any]:
        """
        根据名称获取测试用例
        
        参数:
            name: 测试用例名称
            
        返回:
            Dict: 包含操作结果的字典
        """
        return cls.get_all(
            where_clause="TEST_TEMPLATE_NAME like %s%",
            params=(name,),
        )

