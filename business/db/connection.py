import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# 加载 .env 文件，确保数据库连接信息受到保护
load_dotenv()

# 数据库连接配置
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "flow")
}


def get_connection():
    """
    获取数据库连接

    返回:
        mysql.connector.connection.MySQLConnection: 数据库连接对象
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise Exception(f"数据库连接失败: {str(e)}")


def close_connection(conn, cursor=None):
    """
    关闭数据库连接和游标

    参数:
        conn: 数据库连接对象
        cursor: 游标对象
    """
    if cursor:
        try:
            cursor.close()
        except Error:
            pass

    if conn:
        try:
            conn.close()
        except Error:
            pass
