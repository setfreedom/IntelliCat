"""匹配结果路由 — 展示、搜索、修改、导出"""

import json
from flask import Blueprint, request, jsonify
from models import db, MatchResult
from utils import bad_request, paginate, jsonify_paginated

results_bp = Blueprint('results', __name__, url_prefix='/api/results')


@results_bp.route('', methods=['GET'])
def list_results():
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 1000, type=int)
    query = MatchResult.query.order_by(MatchResult.id)

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                MatchResult.catalog_name.like(like),
                MatchResult.duty_name.like(like),
                MatchResult.department.like(like),
                MatchResult.line_name.like(like)
            )
        )

    items, total, page, per_page, total_pages = paginate(query, page, per_page, default_per_page=1000)
    return jsonify_paginated([{
        'id': r.id,
        'catalog_id': r.catalog_id,
        'duty_id': r.duty_id,
        'catalog_name': r.catalog_name,
        'duty_name': r.duty_name,
        'department': r.department,
        'line_name': r.line_name,
        'matched_data': json.loads(r.matched_data) if r.matched_data else {},
        'created_at': r.created_at.isoformat() if r.created_at else None
    } for r in items], total, page, per_page, total_pages)


@results_bp.route('/<int:result_id>', methods=['PUT'])
def update_result(result_id):
    result = db.session.get(MatchResult, result_id)
    if not result:
        return bad_request('结果不存在', 404)
    data = request.get_json(silent=True) or {}
    if 'catalog_name' in data:
        result.catalog_name = data['catalog_name'].strip()
    if 'duty_name' in data:
        result.duty_name = data['duty_name'].strip()
    if 'matched_data' in data:
        result.matched_data = json.dumps(data['matched_data'], ensure_ascii=False)
    db.session.commit()
    return jsonify({'message': '更新成功'})


@results_bp.route('/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    result = db.session.get(MatchResult, result_id)
    if not result:
        return bad_request('结果不存在', 404)
    db.session.delete(result)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@results_bp.route('/export', methods=['GET'])
def export_results():
    search = request.args.get('search', '').strip()
    query = MatchResult.query.order_by(MatchResult.id)

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                MatchResult.catalog_name.like(like),
                MatchResult.duty_name.like(like),
                MatchResult.department.like(like),
                MatchResult.line_name.like(like)
            )
        )

    results = query.all()
    export_data = [{
        '部门': r.department,
        '职能名称': r.duty_name,
        '目录名称': r.catalog_name,
        '条线': r.line_name,
    } for r in results]

    return jsonify({'data': export_data, 'total': len(export_data)})
