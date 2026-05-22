# -*- coding: utf-8 -*-

import pymysql
from dbutils.pooled_db import PooledDB
from pymysql import OperationalError, InterfaceError

from app.common.util.log_handler import log


class DBUtil:
    """MySQL 数据库连接池工具类"""

    _pool = None

    def __init__(self, host, user_name, password, db_name, port=3306,
                 min_cached=2, max_cached=5, max_connections=10):
        self.host = host
        self.user_name = user_name
        self.password = password
        self.db_name = db_name
        self.port = port

        if DBUtil._pool is None:
            DBUtil._pool = PooledDB(
                creator=pymysql,
                maxconnections=max_connections,
                mincached=min_cached,
                maxcached=max_cached,
                blocking=True,
                host=self.host,
                port=self.port,
                user=self.user_name,
                password=self.password,
                database=self.db_name,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )

    def get_connection(self):
        """从连接池获取连接"""
        return DBUtil._pool.connection()

    def execute_sql(self, sql, params=None):
        """执行 SQL 语句（INSERT/UPDATE/DELETE）"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"执行 SQL 失败: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def fetch_all(self, sql, params=None):
        """获取所有查询结果"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
        except (OperationalError, InterfaceError) as e:
            log.error(f"查询失败: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def fetch_one(self, sql, params=None):
        """获取单条查询结果"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchone()
        except (OperationalError, InterfaceError) as e:
            log.error(f"查询失败: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def execute_many(self, sql, params_list):
        """批量执行 SQL 语句"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.executemany(sql, params_list)
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            log.error(f"批量执行失败: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
