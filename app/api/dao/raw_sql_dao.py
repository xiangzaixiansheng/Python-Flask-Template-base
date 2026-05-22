# -*- coding: utf-8 -*-

"""
原生 SQL 操作示例

适用场景:
- 复杂的多表 JOIN + 子查询
- 聚合统计报表
- 需要数据库特定语法 (窗口函数、CTE 等)
- 性能敏感的批量操作

使用 MySQLUtil 连接池，参数化查询防止 SQL 注入。
"""

from app.config import get_db_util
from app.common.util.log_handler import log


class RawSqlDao:

    @staticmethod
    def get_user_statistics():
        """用户统计报表 - 按日期聚合

        演示: GROUP BY + 聚合函数 + 日期格式化 + COALESCE

        Returns:
            list[dict]: 每日注册统计
            [
                {"date": "2026-05-22", "total": 15, "active": 12, "inactive": 3},
                ...
            ]
        """
        db = get_db_util()
        sql = """
            SELECT
                DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS `date`,
                COUNT(*) AS total,
                COALESCE(SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END), 0) AS active,
                COALESCE(SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END), 0) AS inactive
            FROM users
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE_FORMAT(created_at, '%%Y-%%m-%%d')
            ORDER BY `date` DESC
        """
        results = db.fetch_all(sql)
        log.info(f"用户统计查询完成, 共 {len(results)} 条记录")
        return results

    @staticmethod
    def get_user_activity_ranking(limit=10):
        """用户活跃排行 - 多表联查 + 窗口函数

        演示: JOIN + 子查询 + RANK() 窗口函数 + 参数化

        假设存在 audit_logs 表记录用户操作。
        统计最近7天内用户操作次数排名。

        Args:
            limit: 返回前 N 名

        Returns:
            list[dict]: 活跃排行
            [
                {"rank": 1, "user_id": 5, "username": "admin", "action_count": 128},
                ...
            ]
        """
        db = get_db_util()
        sql = """
            SELECT
                ranked.rank_num AS `rank`,
                ranked.user_id,
                u.username,
                ranked.action_count
            FROM (
                SELECT
                    a.user_id,
                    COUNT(*) AS action_count,
                    RANK() OVER (ORDER BY COUNT(*) DESC) AS rank_num
                FROM audit_logs a
                WHERE a.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                  AND a.user_id IS NOT NULL
                GROUP BY a.user_id
            ) ranked
            INNER JOIN users u ON u.id = ranked.user_id
            WHERE ranked.rank_num <= %s
            ORDER BY ranked.rank_num ASC
        """
        results = db.fetch_all(sql, (limit,))
        return results

    @staticmethod
    def batch_update_status(user_ids, is_active):
        """批量更新用户状态

        演示: 参数化 IN 查询 + 批量更新

        Args:
            user_ids: 用户 ID 列表
            is_active: 目标状态 (True/False)

        Returns:
            bool: 是否成功
        """
        if not user_ids:
            return False

        db = get_db_util()
        placeholders = ', '.join(['%s'] * len(user_ids))
        sql = f"""
            UPDATE users
            SET is_active = %s, updated_at = NOW()
            WHERE id IN ({placeholders})
        """
        params = [int(is_active)] + list(user_ids)
        success = db.execute_sql(sql, params)
        log.info(f"批量更新用户状态: ids={user_ids}, is_active={is_active}, success={success}")
        return success

    @staticmethod
    def search_users_fulltext(keyword, page=1, per_page=20):
        """用户搜索 - 模糊查询 + 分页 + 总数统计

        演示: LIKE 模糊查询 + COUNT 子查询 + LIMIT/OFFSET 分页

        Args:
            keyword: 搜索关键词
            page: 页码
            per_page: 每页数量

        Returns:
            dict: {"items": [...], "total": 100}
        """
        db = get_db_util()
        offset = (page - 1) * per_page
        like_pattern = f"%{keyword}%"

        count_sql = """
            SELECT COUNT(*) AS total
            FROM users
            WHERE is_active = 1
              AND (username LIKE %s OR email LIKE %s)
        """
        count_result = db.fetch_one(count_sql, (like_pattern, like_pattern))
        total = count_result['total'] if count_result else 0

        data_sql = """
            SELECT id, username, email, created_at, is_active
            FROM users
            WHERE is_active = 1
              AND (username LIKE %s OR email LIKE %s)
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        items = db.fetch_all(data_sql, (like_pattern, like_pattern, per_page, offset))

        return {"items": items, "total": total}
