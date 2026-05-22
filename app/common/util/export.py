# -*- coding: utf-8 -*-

import csv
import io
from flask import make_response
from app.common.util.log_handler import log


def export_csv(data, headers, filename='export.csv'):
    """导出 CSV 文件

    Args:
        data: 数据列表 (list of dict 或 list of list)
        headers: 表头 [{'key': 'name', 'label': '姓名'}, ...]
        filename: 下载文件名

    Returns:
        Flask Response (带文件下载头)

    Example:
        headers = [
            {'key': 'id', 'label': 'ID'},
            {'key': 'username', 'label': '用户名'},
            {'key': 'email', 'label': '邮箱'},
        ]
        users = UserService.get_all_users()
        return export_csv(users, headers, 'users.csv')
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([h['label'] for h in headers])

    for row in data:
        if isinstance(row, dict):
            writer.writerow([row.get(h['key'], '') for h in headers])
        else:
            writer.writerow(row)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def export_excel(data, headers, filename='export.xlsx', sheet_name='Sheet1'):
    """导出 Excel 文件

    依赖: pip install openpyxl

    Args:
        data: 数据列表 (list of dict)
        headers: 表头 [{'key': 'name', 'label': '姓名'}, ...]
        filename: 下载文件名
        sheet_name: 工作表名称

    Returns:
        Flask Response
    """
    try:
        from openpyxl import Workbook
    except ImportError:
        raise ImportError("请安装 openpyxl: pip install openpyxl")

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    ws.append([h['label'] for h in headers])

    for row in data:
        if isinstance(row, dict):
            ws.append([row.get(h['key'], '') for h in headers])
        else:
            ws.append(row)

    for col in ws.columns:
        max_length = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_length + 2, 50)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response
