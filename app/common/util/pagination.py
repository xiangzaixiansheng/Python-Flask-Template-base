# -*- coding: utf-8 -*-

from flask import request


def get_page_params():
    """从请求参数中获取分页参数"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    page = max(1, page)
    per_page = min(max(1, per_page), 100)
    return page, per_page


def paginate_query(query, page, per_page):
    """对 SQLAlchemy query 进行分页"""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page > 0 else 0
    }


def paginate_list(items, page, per_page):
    """对普通列表进行分页"""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    paged_items = items[start:end]
    return {
        "items": paged_items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page > 0 else 0
    }
