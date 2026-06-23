"""目录梳理路由 — 上传解析、自动匹配条线"""

import json
import os
import io
from flask import Blueprint, request, jsonify, send_file
import pandas as pd
import openpyxl
from models import db, Catalog, Line, LineCatalogDept
from utils import bad_request, paginate, jsonify_paginated

catalogs_bp = Blueprint('catalogs', __name__, url_prefix='/api/catalogs')


def _parse_upload(file_storage):
    """解析上传的 Excel/CSV 文件，返回 DataFrame"""
    _, ext = os.path.splitext(file_storage.filename.lower())
    try:
        if ext in ('.xlsx', '.xls'):
            df = pd.read_excel(file_storage, dtype=str)
        elif ext == '.csv':
            df = pd.read_csv(file_storage, dtype=str, encoding='utf-8')
        else:
            return None, '不支持的文件格式，请上传 xlsx/xls/csv'
    except Exception as e:
        return None, f'文件解析失败：{str(e)}'

    if df.empty:
        return None, '文件为空'

    # 智能识别列名
    col_map = {}
    for col in df.columns:
        col_lower = col.strip().lower().replace(' ', '').replace('　', '')
        if col_lower in ('序号', '序號', 'no', 'number', '序列号', '编号'):
            col_map['sequence'] = col
        elif col_lower in ('目录名称', '目錄名稱', '目录名', 'name', '目录'):
            col_map['name'] = col
        elif col_lower in ('来源部门', '來源部門', '部门', '部门名称', 'department', 'dept'):
            col_map['department'] = col
        elif col_lower in ('主要字段项', '字段项', '字段', '数据项', 'fields', 'field'):
            col_map['fields'] = col

    if 'name' not in col_map:
        return None, '未找到「目录名称」列，请检查表头'

    rows = []
    for idx, row in df.iterrows():
        item = {}
        for key, col in col_map.items():
            val = str(row[col]).strip() if pd.notna(row[col]) else ''
            if key == 'sequence':
                try:
                    item['sequence'] = int(float(val)) if val else None
                except ValueError:
                    item['sequence'] = None
            elif key == 'fields':
                # 字段项按常见分隔符拆分
                if val:
                    parts = [p.strip() for p in val.replace('、', ',').replace('，', ',').replace(';', ',').replace('；', ',').split(',') if p.strip()]
                    item['fields'] = parts
                else:
                    item['fields'] = []
            else:
                item[key] = val
        rows.append(item)

    return rows, None


@catalogs_bp.route('/parse', methods=['POST'])
def parse_upload():
    """上传并解析文件，返回预览数据（不保存到数据库）"""
    if 'file' not in request.files:
        return bad_request('请上传文件')
    file = request.files['file']
    if not file.filename:
        return bad_request('文件名为空')

    rows, err = _parse_upload(file)
    if err:
        return jsonify({'error': err}), 400

    # 查询每个来源部门匹配的条线
    for row in rows:
        dept = row.get('department', '')
        if dept:
            mappings = LineCatalogDept.query.filter_by(department=dept).all()
            matched_lines = [{'id': m.line_id, 'name': m.line.name} for m in mappings if m.line]
            cnt = len(matched_lines)
            if cnt == 0:
                row['_line_suggestion'] = None
                row['_line_message'] = '未匹配到条线'
            elif cnt == 1:
                row['_line_suggestion'] = matched_lines[0]
                row['_line_message'] = ''
            else:
                row['_line_suggestion'] = None
                row['_line_message'] = f'该部门对应 {cnt} 条条线'
            row['_matched_lines'] = matched_lines
        else:
            row['_line_suggestion'] = None
            row['_line_message'] = '无部门信息'
            row['_matched_lines'] = []

    return jsonify({'rows': rows, 'total': len(rows)})


@catalogs_bp.route('/save', methods=['POST'])
def save_catalogs():
    """保存目录数据"""
    data = request.get_json(silent=True) or {}
    rows = data.get('rows', [])

    if not rows:
        return bad_request('无数据可保存')

    invalid_rows = []
    for idx, row in enumerate(rows):
        line_id = row.get('line_id')
        if not line_id:
            name = row.get('name', f'第{idx + 1}行')
            invalid_rows.append(f'「{name}」未选择条线')
        else:
            line = db.session.get(Line, line_id)
            if not line:
                invalid_rows.append(f'「{row.get("name", "")}」选择的条线不存在')

    if invalid_rows:
        return bad_request('保存失败：' + '；'.join(invalid_rows))

    # 清除旧数据后重新插入
    Catalog.query.delete()

    for row in rows:
        catalog = Catalog(
            sequence=row.get('sequence'),
            name=row.get('name', '').strip(),
            department=row.get('department', '').strip(),
            line_id=row.get('line_id'),
            fields=json.dumps(row.get('fields', []), ensure_ascii=False)
        )
        db.session.add(catalog)

    db.session.commit()
    return jsonify({'message': f'成功保存 {len(rows)} 条目录', 'total': len(rows)})


@catalogs_bp.route('', methods=['GET'])
def list_catalogs():
    """获取已保存的目录列表（支持分页）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 1000, type=int)
    query = Catalog.query.order_by(Catalog.sequence)
    items, total, page, per_page, total_pages = paginate(query, page, per_page, default_per_page=1000)
    return jsonify_paginated([{
        'id': c.id,
        'sequence': c.sequence,
        'name': c.name,
        'department': c.department,
        'line_id': c.line_id,
        'line_name': c.line.name if c.line else None,
        'fields': json.loads(c.fields) if c.fields else []
    } for c in items], total, page, per_page, total_pages)


@catalogs_bp.route('/<int:catalog_id>', methods=['PUT'])
def update_catalog(catalog_id):
    catalog = db.session.get(Catalog, catalog_id)
    if not catalog:
        return bad_request('目录不存在', 404)
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        catalog.name = data['name'].strip()
    if 'department' in data:
        catalog.department = data['department'].strip()
    if 'line_id' in data:
        line_id = data['line_id']
        if line_id and not db.session.get(Line, line_id):
            return bad_request('条线不存在')
        catalog.line_id = line_id
    if 'fields' in data:
        catalog.fields = json.dumps(data['fields'], ensure_ascii=False)
    db.session.commit()
    return jsonify({'message': '更新成功'})


@catalogs_bp.route('/<int:catalog_id>', methods=['DELETE'])
def delete_catalog(catalog_id):
    catalog = db.session.get(Catalog, catalog_id)
    if not catalog:
        return bad_request('目录不存在', 404)
    db.session.delete(catalog)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@catalogs_bp.route('/template')
def download_catalog_template():
    output = io.BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '目录模板'
    ws.append(['序号', '目录名称', '来源部门', '主要字段项'])
    ws.append(['1', '例：财政预算信息', '例：财政局', '例：预算年度、收支分类'])
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 40
    wb.save(output)
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='目录模板.xlsx')
