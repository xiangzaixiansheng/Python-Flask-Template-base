# -*- coding: utf-8 -*-

from app.common.util.pagination import paginate_list


def test_paginate_list_first_page():
    """测试列表分页 - 第一页"""
    items = list(range(50))
    result = paginate_list(items, page=1, per_page=10)

    assert result["total"] == 50
    assert result["page"] == 1
    assert result["per_page"] == 10
    assert result["pages"] == 5
    assert result["items"] == list(range(10))


def test_paginate_list_last_page():
    """测试列表分页 - 最后一页"""
    items = list(range(25))
    result = paginate_list(items, page=3, per_page=10)

    assert result["total"] == 25
    assert result["pages"] == 3
    assert result["items"] == [20, 21, 22, 23, 24]


def test_paginate_list_empty():
    """测试空列表分页"""
    result = paginate_list([], page=1, per_page=10)

    assert result["total"] == 0
    assert result["pages"] == 0
    assert result["items"] == []


def test_paginate_list_overflow():
    """测试超出范围的页码"""
    items = list(range(5))
    result = paginate_list(items, page=10, per_page=10)

    assert result["total"] == 5
    assert result["items"] == []
