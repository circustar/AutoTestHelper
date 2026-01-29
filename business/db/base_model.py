import json
import datetime
from abc import ABC
from typing import Dict, Any, Tuple

from business.db.connection import get_connection, close_connection


class BaseModel(ABC):
    """
    基础模型类，提供通用的CRUD操作
    """
    
    # 表名，子类必须重写
    table_name = ""
    
    # 主键字段名，子类必须重写
    primary_key = ""
    
    # 字段列表，子类必须重写
    fields = []
    
    # 必填字段列表，子类必须重写
    required_fields = []
    
    @classmethod
    def create(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建记录
        
        参数:
            data: 要创建的记录数据
            
        返回:
            Dict: 包含操作结果的字典
        """
        # 验证必填字段
        for field in cls.required_fields:
            if field not in data:
                return {
                    "success": False,
                    "message": f"缺少必填字段: {field}",
                    "data": None
                }
        
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 准备当前时间
            current_time = datetime.datetime.now()
            
            # 如果没有指定创建时间和更新时间，则使用当前时间
            if 'CREATE_TIME' not in data:
                data['CREATE_TIME'] = current_time
            if 'UPDATE_TIME' not in data:
                data['UPDATE_TIME'] = current_time
            
            # 如果没有指定逻辑删除标记，则默认为未删除
            if 'IS_DELETED' not in data:
                data['IS_DELETED'] = '0'
            
            # 构建SQL语句
            fields = []
            placeholders = []
            values = []
            
            for field, value in data.items():
                if field in cls.fields:
                    fields.append(field)
                    placeholders.append('%s')
                    values.append(value)
            
            fields_str = ', '.join(fields)
            placeholders_str = ', '.join(placeholders)
            
            query = f"""
            INSERT INTO {cls.table_name} ({fields_str})
            VALUES ({placeholders_str})
            """
            
            # 执行SQL
            cursor.execute(query, values)
            
            # 提交事务
            conn.commit()
            
            # 获取新插入记录的ID
            new_id = cursor.lastrowid
            
            result = {
                "success": True,
                "message": "创建成功",
                "data": {
                    cls.primary_key: new_id,
                    **data
                }
            }
            
            return result
            
        except Exception as e:
            if conn:
                conn.rollback()
            
            return {
                "success": False,
                "message": f"创建失败: {str(e)}",
                "data": None
            }
        finally:
            close_connection(conn, cursor)
    
    @classmethod
    def get_by_id(cls, id: int) -> Dict[str, Any]:
        """
        根据ID获取记录
        
        参数:
            id: 记录ID
            
        返回:
            Dict: 包含操作结果的字典
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 构建SQL语句
            query = f"""
            SELECT * FROM {cls.table_name}
            WHERE {cls.primary_key} = %s AND IS_DELETED = '0'
            """
            
            # 执行SQL
            cursor.execute(query, (id,))
            
            # 获取结果
            row = cursor.fetchone()
            
            if not row:
                return {
                    "success": False,
                    "message": f"未找到ID为{id}的记录",
                    "data": None
                }
            
            # 处理日期时间字段
            for key, value in row.items():
                if isinstance(value, datetime.datetime):
                    row[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            
            result = {
                "success": True,
                "message": "获取成功",
                "data": row
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"获取失败: {str(e)}",
                "data": None
            }
        finally:
            close_connection(conn, cursor)
    
    @classmethod
    def get_all(cls, where_clause: str = "", params: Tuple = (), order_clause:str = "", limit: int = 1000, offset: int = 0) -> Dict[str, Any]:
        """
        获取所有记录
        
        参数:
            where_clause: WHERE子句（不包含WHERE关键字）
            params: WHERE子句中的参数
            limit: 返回记录数量限制
            offset: 返回记录的偏移量
            
        返回:
            Dict: 包含操作结果的字典
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 构建SQL语句
            query = f"""
            SELECT * FROM {cls.table_name}
            WHERE IS_DELETED = '0'
            """

            if not order_clause :
                order_clause = cls.primary_key + " desc "
            
            if where_clause:
                query += f" AND {where_clause}"
            
            query += f"""
            ORDER BY {order_clause}
            LIMIT %s OFFSET %s
            """
            
            # 执行SQL
            cursor.execute(query, params + (limit, offset))
            
            # 获取结果
            rows = cursor.fetchall()
            
            # 处理日期时间字段
            for row in rows:
                for key, value in row.items():
                    if isinstance(value, datetime.datetime):
                        row[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            
            # 获取总记录数
            count_query = f"""
            SELECT COUNT(*) as total FROM {cls.table_name}
            WHERE IS_DELETED = '0'
            """
            
            if where_clause:
                count_query += f" AND {where_clause}"
            
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            result = {
                "success": True,
                "message": "获取成功",
                "data": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "records": rows
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"获取失败: {str(e)}",
                "data": None
            }
        finally:
            close_connection(conn, cursor)

    @classmethod
    def get_count(cls, where_clause: str = "", params: Tuple = ()) -> int:
        """
                获取所有记录

                参数:
                    where_clause: WHERE子句（不包含WHERE关键字）
                    params: WHERE子句中的参数
                    limit: 返回记录数量限制
                    offset: 返回记录的偏移量

                返回:
                    Dict: 包含操作结果的字典
                """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # 获取总记录数
            count_query = f"""
                    SELECT COUNT(*) as total FROM {cls.table_name}
                    WHERE IS_DELETED = '0'
                    """

            if where_clause:
                count_query += f" AND {where_clause}"

            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']

            return total

        except Exception as e:
            return 0
        finally:
            close_connection(conn, cursor)

    @classmethod
    def update(cls, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新记录
        
        参数:
            id: 记录ID
            data: 要更新的数据
            
        返回:
            Dict: 包含操作结果的字典
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 检查记录是否存在
            check_query = f"""
            SELECT {cls.primary_key} FROM {cls.table_name}
            WHERE {cls.primary_key} = %s AND IS_DELETED = '0'
            """
            
            cursor.execute(check_query, (id,))
            if not cursor.fetchone():
                return {
                    "success": False,
                    "message": f"未找到ID为{id}的记录",
                    "data": None
                }
            
            # 准备当前时间
            current_time = datetime.datetime.now()
            
            # 如果没有指定更新时间，则使用当前时间
            if 'UPDATE_TIME' not in data:
                data['UPDATE_TIME'] = current_time
            
            # 构建SQL语句
            set_clauses = []
            values = []
            
            for field, value in data.items():
                if field in cls.fields and field != cls.primary_key:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                return {
                    "success": False,
                    "message": "没有要更新的字段",
                    "data": None
                }
            
            set_clause_str = ', '.join(set_clauses)
            
            query = f"""
            UPDATE {cls.table_name}
            SET {set_clause_str}
            WHERE {cls.primary_key} = %s
            """
            
            # 执行SQL
            cursor.execute(query, values + [id])
            
            # 提交事务
            conn.commit()
            
            result = {
                "success": True,
                "message": "更新成功",
                "data": {
                    cls.primary_key: id,
                    **data
                }
            }
            
            return result
            
        except Exception as e:
            if conn:
                conn.rollback()
            
            return {
                "success": False,
                "message": f"更新失败: {str(e)}",
                "data": None
            }
        finally:
            close_connection(conn, cursor)
    
    @classmethod
    def delete(cls, id: int, hard_delete: bool = False) -> Dict[str, Any]:
        """
        删除记录
        
        参数:
            id: 记录ID
            hard_delete: 是否物理删除，默认为逻辑删除
            
        返回:
            Dict: 包含操作结果的字典
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 检查记录是否存在
            check_query = f"""
            SELECT {cls.primary_key} FROM {cls.table_name}
            WHERE {cls.primary_key} = %s
            """
            
            if not hard_delete:
                check_query += " AND IS_DELETED = '0'"
            
            cursor.execute(check_query, (id,))
            if not cursor.fetchone():
                return {
                    "success": False,
                    "message": f"未找到ID为{id}的记录",
                    "data": None
                }
            
            # 构建SQL语句
            if hard_delete:
                query = f"""
                DELETE FROM {cls.table_name}
                WHERE {cls.primary_key} = %s
                """
                params = (id,)
            else:
                query = f"""
                UPDATE {cls.table_name}
                SET IS_DELETED = '1', UPDATE_TIME = %s
                WHERE {cls.primary_key} = %s
                """
                params = (datetime.datetime.now(), id)
            
            # 执行SQL
            cursor.execute(query, params)
            
            # 提交事务
            conn.commit()
            
            result = {
                "success": True,
                "message": "删除成功",
                "data": {
                    cls.primary_key: id
                }
            }
            
            return result
            
        except Exception as e:
            if conn:
                conn.rollback()
            
            return {
                "success": False,
                "message": f"删除失败: {str(e)}",
                "data": None
            }
        finally:
            close_connection(conn, cursor)
    
    @classmethod
    def to_json(cls, data: Dict[str, Any]) -> str:
        """
        将数据转换为JSON字符串
        
        参数:
            data: 要转换的数据
            
        返回:
            str: JSON字符串
        """
        return json.dumps(data, ensure_ascii=False)
