# database/database.py
import mysql.connector
import logging
from mysql.connector import pooling
from mysql.connector import Error as MySQLError
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from contextlib import contextmanager
from datetime import datetime, date
import threading
from typing import Dict, List, Any, Optional
import logging
from mysql.connector import Error as MySQLError
from PyQt5.QtGui import QColor, QBrush

class DatabaseError(Exception):
    """自定义数据库异常类"""
    pass


class Database:
    """数据库管理类，实现数据库连接池和所有数据库操作"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化数据库连接池

        Args:
            config: 数据库配置字典，包含host, port, user, password, database等信息
        """
        if not hasattr(self, 'initialized'):
            # 从ConfigManager获取配置
            from config import get_config
            config_manager = get_config()
            self.logger = logging.getLogger(__name__)  # 添加这行

            # 使用配置文件中的数据库配置
            self.config = {
                'host': config_manager.database.host,
                'port': config_manager.database.port,
                'user': config_manager.database.user,
                'password': config_manager.database.password,
                'database': config_manager.database.database,
                'pool_name': 'mypool',
                'pool_size': config_manager.database.pool_size,
                'raise_on_warnings': True,
                'autocommit': True,
                'charset': config_manager.database.charset,
                'use_unicode': True,
                'connect_timeout': 60,
                'buffered': True
            }

            try:
                self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**self.config)
                logging.info("Database connection pool initialized successfully")
                self.initialized = True
            except MySQLError as e:
                logging.error(f"Failed to initialize database connection pool: {e}")
                raise DatabaseError(f"Database initialization error: {e}")

    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器

        Yields:
            connection: 数据库连接对象
        """
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            yield connection
        except MySQLError as e:
            logging.error(f"Failed to get database connection: {e}")
            raise DatabaseError(f"Connection error: {e}")
        finally:
            if connection:
                try:
                    connection.close()
                except MySQLError as e:
                    logging.error(f"Failed to close database connection: {e}")

    def execute_query(self, query: str, params: Union[tuple, list] = None) -> List[Dict[str, Any]]:
        """
        执行SELECT查询

        Args:
            query: SQL查询语句
            params: 查询参数(元组或列表)

        Returns:
            查询结果列表
        """
        try:
            # 规范化SQL语句格式：移除多余的空格和换行
            query = ' '.join(query.split())

            self.logger.info(f"执行SQL: {query}")
            if params:
                self.logger.info(f"参数: {params}")

            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                cursor.close()

                self.logger.info(f"查询返回 {len(result)} 条记录")
                return result
        except Exception as e:
            self.logger.error(f"查询执行失败: {str(e)}")
            raise DatabaseError(f"Query execution error: {str(e)}")

    def execute_write(self, query: str, params: Union[tuple, list] = None) -> int:
        """
        执行INSERT/UPDATE/DELETE操作

        Args:
            query: SQL语句
            params: 参数(元组或列表)

        Returns:
            受影响的行数
        """
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()

                # 将问号(?)替换为MySQL的参数占位符(%s)
                query = query.replace('?', '%s')

                cursor.execute(query, params or ())
                connection.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
            except MySQLError as e:
                logging.error(f"Write operation failed: {e}\nQuery: {query}\nParams: {params}")
                raise DatabaseError(f"Write operation error: {e}")

    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        执行批量操作

        Args:
            query: SQL语句
            params_list: 参数元组列表

        Returns:
            受影响的行数
        """
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                cursor.executemany(query, params_list)
                connection.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
            except MySQLError as e:
                logging.error(f"Batch operation failed: {e}\nQuery: {query}")
                raise DatabaseError(f"Batch operation error: {e}")

    def check_connection_pool(self) -> bool:
        """
        检查连接池状态

        Returns:
            bool: 连接池是否正常工作
        """
        try:
            with self.get_connection() as conn:
                return conn.is_connected()
        except DatabaseError:
            return False

    @contextmanager
    def transaction(self):
        """
        事务管理器，用于需要事务支持的操作

        Example:
            with db.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(query1)
                cursor.execute(query2)
        """
        with self.get_connection() as connection:
            try:
                connection.autocommit = False
                yield connection
                connection.commit()
            except Exception as e:
                connection.rollback()
                raise DatabaseError(f"Transaction failed: {e}")
            finally:
                connection.autocommit = True

    # 产品相关方法
    def get_all_products(self) -> List[Dict[str, Any]]:
        """获取所有产品"""
        query = "SELECT * FROM products ORDER BY product_id"
        return self.execute_query(query)

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取产品"""
        query = "SELECT * FROM products WHERE product_id = %s"
        result = self.execute_query(query, (product_id,))
        return result[0] if result else None

    def add_product(self, model: str, name: str, color: str) -> int:
        """添加新产品"""
        query = """
        INSERT INTO products (model, name, color)
        VALUES (%s, %s, %s)
        """
        return self.execute_write(query, (model, name, color))

    def update_product(self, product_id: int, model: str, name: str, color: str) -> int:
        """更新产品信息"""
        query = """
        UPDATE products 
        SET model = %s, name = %s, color = %s
        WHERE product_id = %s
        """
        return self.execute_write(query, (model, name, color, product_id))

    def delete_product(self, product_id: int) -> int:
        """删除产品"""
        query = "DELETE FROM products WHERE product_id = %s"
        return self.execute_write(query, (product_id,))

    # 展会相关方法
    def get_all_exhibitions(self) -> List[Dict[str, Any]]:
        """获取所有展会"""
        query = "SELECT * FROM exhibitions ORDER BY start_date"
        return self.execute_query(query)

    def get_exhibition_by_id(self, exhibition_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取展会"""
        query = "SELECT * FROM exhibitions WHERE exhibition_id = %s"
        result = self.execute_query(query, (exhibition_id,))
        return result[0] if result else None

    def add_exhibition(self, name: str, address: str, start_date: date, end_date: date) -> int:
        """添加新展会"""
        query = """
        INSERT INTO exhibitions (name, address, start_date, end_date)
        VALUES (%s, %s, %s, %s)
        """
        return self.execute_write(query, (name, address, start_date, end_date))

    def update_exhibition(self, exhibition_id: int, name: str, address: str,
                          start_date: date, end_date: date) -> int:
        """更新展会信息"""
        query = """
        UPDATE exhibitions 
        SET name = %s, address = %s, start_date = %s, end_date = %s
        WHERE exhibition_id = %s
        """
        return self.execute_write(query, (name, address, start_date, end_date, exhibition_id))

    def delete_exhibition(self, exhibition_id: int) -> int:
        """删除展会"""
        query = "DELETE FROM exhibitions WHERE exhibition_id = %s"
        return self.execute_write(query, (exhibition_id,))

    # 产品展会关联记录相关方法
    def get_all_records(self) -> List[Dict[str, Any]]:
        """获取所有关联记录"""
        query = """
        SELECT r.*, p.name as product_name, e.name as exhibition_name
        FROM product_exhibition_records r
        JOIN products p ON r.product_id = p.product_id
        JOIN exhibitions e ON r.exhibition_id = e.exhibition_id
        ORDER BY e.start_date DESC
        """
        return self.execute_query(query)

    def get_record_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取关联记录"""
        query = """
        SELECT r.*, p.name as product_name, e.name as exhibition_name
        FROM product_exhibition_records r
        JOIN products p ON r.product_id = p.product_id
        JOIN exhibitions e ON r.exhibition_id = e.exhibition_id
        WHERE r.record_id = %s
        """
        result = self.execute_query(query, (record_id,))
        return result[0] if result else None

    def add_record(self, product_id: int, exhibition_id: int, status: str = '待参展') -> int:
        """添加新关联记录"""
        query = """
        INSERT INTO product_exhibition_records (product_id, exhibition_id, status)
        VALUES (%s, %s, %s)
        """
        return self.execute_write(query, (product_id, exhibition_id, status))

    def update_record_status(self, record_id: int, status: str) -> int:
        """更新关联记录状态"""
        query = """
        UPDATE product_exhibition_records 
        SET status = %s
        WHERE record_id = %s
        """
        return self.execute_write(query, (status, record_id))

    def delete_record(self, record_id: int) -> int:
        """删除关联记录"""
        query = "DELETE FROM product_exhibition_records WHERE record_id = %s"
        return self.execute_write(query, (record_id,))

    def add_products_batch(self, products: List[Tuple[str, str, str]]) -> int:
        """
        批量添加产品

        Args:
            products: 产品信息列表，每个元素为(model, name, color)元组

        Returns:
            int: 成功添加的产品数量
        """
        query = "INSERT INTO products (model, name, color) VALUES (%s, %s, %s)"
        return self.execute_many(query, products)

    def add_exhibitions_batch(self, exhibitions: List[Tuple[str, str, date, date]]) -> int:
        """
        批量添加展会

        Args:
            exhibitions: 展会信息列表，每个元素为(name, address, start_date, end_date)元组

        Returns:
            int: 成功添加的展会数量
        """
        query = "INSERT INTO exhibitions (name, address, start_date, end_date) VALUES (%s, %s, %s, %s)"
        return self.execute_many(query, exhibitions)

    # 统计查询方法
    def get_exhibition_products_count(self, exhibition_id: int) -> int:
        """获取展会参展产品数量"""
        query = """
        SELECT COUNT(*) as count
        FROM product_exhibition_records
        WHERE exhibition_id = %s
        """
        result = self.execute_query(query, (exhibition_id,))
        return result[0]['count'] if result else 0

    def get_product_exhibitions_count(self, product_id: int) -> int:
        """获取产品参展次数"""
        query = """
        SELECT COUNT(*) as count
        FROM product_exhibition_records
        WHERE product_id = %s
        """
        result = self.execute_query(query, (product_id,))
        return result[0]['count'] if result else 0

    def get_exhibitions_by_date_range(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """获取日期范围内的展会"""
        query = """
        SELECT *
        FROM exhibitions
        WHERE (start_date BETWEEN %s AND %s)
           OR (end_date BETWEEN %s AND %s)
        ORDER BY start_date
        """
        return self.execute_query(query, (start_date, end_date, start_date, end_date))

    def get_records_by_status(self, status: str) -> List[Dict[str, Any]]:
        """获取指定状态的关联记录"""
        query = """
        SELECT r.*, p.name as product_name, e.name as exhibition_name
        FROM product_exhibition_records r
        JOIN products p ON r.product_id = p.product_id
        JOIN exhibitions e ON r.exhibition_id = e.exhibition_id
        WHERE r.status = %s
        ORDER BY e.start_date
        """
        return self.execute_query(query, (status,))

    def get_exhibition_status_summary(self) -> List[Dict[str, Any]]:
        """获取展会状态统计摘要"""
        query = """
        SELECT status, COUNT(*) as count
        FROM product_exhibition_records
        GROUP BY status
        """
        return self.execute_query(query)

    def get_product_model_summary(self) -> List[Dict[str, Any]]:
        """获取产品型号统计摘要"""
        query = """
        SELECT model, COUNT(*) as count
        FROM products
        GROUP BY model
        """
        return self.execute_query(query)


    def cleanup_old_records(self, days: int = 365) -> int:
        """
        清理指定天数前的历史记录

        Args:
            days: 要清理的天数阈值，默认为365天

        Returns:
            int: 清理的记录数量
        """
        query = """
        DELETE FROM product_exhibition_records 
        WHERE exhibition_id IN (
            SELECT exhibition_id 
            FROM exhibitions 
            WHERE end_date < DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)
        )
        """
        return self.execute_write(query, (days,))

    def vacuum_database(self) -> None:
        """
        数据库维护操作，优化表空间
        """
        queries = [
            "OPTIMIZE TABLE products",
            "OPTIMIZE TABLE exhibitions",
            "OPTIMIZE TABLE product_exhibition_records"
        ]
        with self.get_connection() as connection:
            try:
                cursor = connection.cursor()
                for query in queries:
                    cursor.execute(query)
                cursor.close()
            except MySQLError as e:
                logging.error(f"Database maintenance failed: {e}")
                raise DatabaseError(f"Maintenance error: {e}")
