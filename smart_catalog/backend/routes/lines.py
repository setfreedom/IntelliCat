"""条线管理路由 — 维护条线及其部门映射关系"""

from flask import Blueprint, request, jsonify
from models import db, Line, LineCatalogDept, LineDutyDept

lines_bp = Blueprint('lines', __name__, url_prefix='/api/lines')


@lines_bp.route('', methods=['GET'])
def list_lines():
    lines = Line.query.order_by(Line.name).all()
    return jsonify([{
        'id': l.id,
        'name': l.name,
        'created_at': l.created_at.isoformat() if l.created_at else None
    } for l in lines])


@lines_bp.route('', methods=['POST'])
def create_line():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': '条线名称不能为空'}), 400
    if Line.query.filter_by(name=name).first():
        return jsonify({'error': f'条线「{name}」已存在'}), 409
    line = Line(name=name)
    db.session.add(line)
    db.session.commit()
    return jsonify({'id': line.id, 'name': line.name}), 201


@lines_bp.route('/<int:line_id>', methods=['PUT'])
def update_line(line_id):
    line = db.session.get(Line, line_id)
    if not line:
        return jsonify({'error': '条线不存在'}), 404
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': '条线名称不能为空'}), 400
    if Line.query.filter(Line.name == name, Line.id != line_id).first():
        return jsonify({'error': f'条线「{name}」已存在'}), 409
    line.name = name
    db.session.commit()
    return jsonify({'id': line.id, 'name': line.name})


@lines_bp.route('/<int:line_id>', methods=['DELETE'])
def delete_line(line_id):
    line = db.session.get(Line, line_id)
    if not line:
        return jsonify({'error': '条线不存在'}), 404
    db.session.delete(line)
    db.session.commit()
    return jsonify({'message': '删除成功'})


# ---- 映射管理 ----

@lines_bp.route('/<int:line_id>/mappings', methods=['GET'])
def get_mappings(line_id):
    line = db.session.get(Line, line_id)
    if not line:
        return jsonify({'error': '条线不存在'}), 404
    catalog_depts = [{'id': m.id, 'department': m.department}
                     for m in line.catalog_depts.all()]
    duty_depts = [{'id': m.id, 'department': m.department}
                  for m in line.duty_depts.all()]
    return jsonify({'catalog_depts': catalog_depts, 'duty_depts': duty_depts})


@lines_bp.route('/<int:line_id>/catalog-depts', methods=['POST'])
def add_catalog_dept(line_id):
    line = db.session.get(Line, line_id)
    if not line:
        return jsonify({'error': '条线不存在'}), 404
    data = request.get_json(silent=True) or {}
    dept = data.get('department', '').strip()
    if not dept:
        return jsonify({'error': '部门名称不能为空'}), 400
    if LineCatalogDept.query.filter_by(department=dept).first():
        return jsonify({'error': f'目录部门「{dept}」已映射到其他条线'}), 409
    m = LineCatalogDept(line_id=line_id, department=dept)
    db.session.add(m)
    db.session.commit()
    return jsonify({'id': m.id, 'department': m.department}), 201


@lines_bp.route('/<int:line_id>/catalog-depts/<int:mapping_id>', methods=['DELETE'])
def delete_catalog_dept(line_id, mapping_id):
    m = db.session.get(LineCatalogDept, mapping_id)
    if not m or m.line_id != line_id:
        return jsonify({'error': '映射记录不存在'}), 404
    db.session.delete(m)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@lines_bp.route('/<int:line_id>/duty-depts', methods=['POST'])
def add_duty_dept(line_id):
    line = db.session.get(Line, line_id)
    if not line:
        return jsonify({'error': '条线不存在'}), 404
    data = request.get_json(silent=True) or {}
    dept = data.get('department', '').strip()
    if not dept:
        return jsonify({'error': '部门名称不能为空'}), 400
    if LineDutyDept.query.filter_by(department=dept).first():
        return jsonify({'error': f'职能部门「{dept}」已映射到其他条线（铁律一：一对一唯一映射）'}), 409
    m = LineDutyDept(line_id=line_id, department=dept)
    db.session.add(m)
    db.session.commit()
    return jsonify({'id': m.id, 'department': m.department}), 201


@lines_bp.route('/<int:line_id>/duty-depts/<int:mapping_id>', methods=['DELETE'])
def delete_duty_dept(line_id, mapping_id):
    m = db.session.get(LineDutyDept, mapping_id)
    if not m or m.line_id != line_id:
        return jsonify({'error': '映射记录不存在'}), 404
    db.session.delete(m)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@lines_bp.route('/lookup-catalog-line', methods=['POST'])
def lookup_catalog_line():
    """根据目录部门查询匹配的条线信息"""
    data = request.get_json(silent=True) or {}
    department = data.get('department', '').strip()
    if not department:
        return jsonify({'suggestion': None, 'count': 0, 'lines': []})

    mappings = LineCatalogDept.query.filter_by(department=department).all()
    lines = [{'id': m.line_id, 'name': m.line.name} for m in mappings if m.line]

    count = len(lines)
    if count == 0:
        return jsonify({'suggestion': None, 'count': 0, 'lines': [],
                        'message': '该部门未匹配到条线'})
    elif count == 1:
        return jsonify({'suggestion': lines[0], 'count': 1, 'lines': lines,
                        'message': ''})
    else:
        return jsonify({'suggestion': None, 'count': count, 'lines': lines,
                        'message': f'该部门对应 {count} 条条线'})


@lines_bp.route('/lookup-duty-line', methods=['POST'])
def lookup_duty_line():
    """根据职能部门查询映射条线（用于铁律一：唯一性校验）"""
    data = request.get_json(silent=True) or {}
    department = data.get('department', '').strip()
    if not department:
        return jsonify({'line': None, 'count': 0, 'error': None})

    mappings = LineDutyDept.query.filter_by(department=department).all()
    count = len(mappings)
    if count == 0:
        return jsonify({'line': None, 'count': 0,
                        'error': f'部门「{department}」在映射表中不存在（0条映射）'})
    elif count >= 2:
        return jsonify({'line': None, 'count': count,
                        'error': f'部门「{department}」存在 {count} 条映射（需唯一）'})
    else:
        m = mappings[0]
        return jsonify({'line': {'id': m.line_id, 'name': m.line.name}, 'count': 1, 'error': None})
