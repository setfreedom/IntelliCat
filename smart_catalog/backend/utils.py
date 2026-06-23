"""工具函数 — 请求校验、分页等"""

from functools import wraps
from flask import request, jsonify


def bad_request(message, status=400):
    """简化的错误响应"""
    return jsonify({'error': message}), status


def expect_body(*names):
    """
    校验 JSON body 中必填字段，注入到视图函数。
    usage:  @expect_body('name', 'department')
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True) or {}
            missing = [n for n in names if not data.get(n)]
            if missing:
                return bad_request(f'缺少必填字段：{"、".join(missing)}')
            return f(data, *args, **kwargs)
        return wrapper
    return decorator


def expect_file(name='file'):
    """
    校验上传文件中必填字段。
    usage:  @expect_file('file')
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if name not in request.files or not request.files[name].filename:
                return bad_request(f'请上传文件')
            return f(*args, **kwargs)
        return wrapper
    return decorator


def paginate(query, page=None, per_page=None, max_per_page=200, default_per_page=50):
    """
    对 SQLAlchemy query 做分页，返回 (items, total, page, per_page, total_pages)。
    """
    if page is None or page < 1:
        page = 1
    if per_page is None or per_page < 1:
        per_page = default_per_page
    if per_page > max_per_page:
        per_page = max_per_page

    total = query.count()
    total_pages = max(1, (total + per_page - 1) // per_page)

    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return items, total, page, per_page, total_pages


def jsonify_paginated(items, total, page, per_page, total_pages, **extra):
    """返回带分页 headers 的 JSON 响应，body 保持为数组（向后兼容）。"""
    body = jsonify(items)
    body.headers['X-Total-Count'] = total
    body.headers['X-Page'] = page
    body.headers['X-Per-Page'] = per_page
    body.headers['X-Total-Pages'] = total_pages
    for k, v in extra.items():
        body.headers[k] = v
    return body
