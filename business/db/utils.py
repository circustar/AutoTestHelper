import json
import datetime
from typing import Dict, Any, List

def format_datetime(dt: datetime.datetime) -> str:
    """
    格式化日期时间
    
    参数:
        dt: 日期时间对象
        
    返回:
        str: 格式化后的日期时间字符串
    """
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return None

def to_json(data: Dict[str, Any]) -> str:
    """
    将数据转换为JSON字符串
    
    参数:
        data: 要转换的数据
        
    返回:
        str: JSON字符串
    """
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return format_datetime(obj)
            return super().default(obj)
    
    return json.dumps(data, ensure_ascii=False, cls=DateTimeEncoder)

def from_json(json_str: str) -> Dict[str, Any]:
    """
    将JSON字符串转换为数据
    
    参数:
        json_str: JSON字符串
        
    返回:
        Dict: 转换后的数据
    """
    return json.loads(json_str)

def paginate(items: List[Any], page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """
    分页处理
    
    参数:
        items: 要分页的列表
        page: 页码，从1开始
        page_size: 每页大小
        
    返回:
        Dict: 分页结果
    """
    total = len(items)
    
    # 计算起始和结束索引
    start = (page - 1) * page_size
    end = start + page_size
    
    # 获取当前页的数据
    paginated_items = items[start:end]
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "items": paginated_items
    }
