from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Line(db.Model):
    __tablename__ = 'line'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, comment='条线名称')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class LineCatalogDept(db.Model):
    """条线-目录部门映射表（一对多：一个条线可对应多个目录部门）"""
    __tablename__ = 'line_catalog_dept'
    id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.Integer, db.ForeignKey('line.id', ondelete='CASCADE'), nullable=False)
    department = db.Column(db.String(200), nullable=False, comment='目录来源部门')
    line = db.relationship('Line', backref=db.backref('catalog_depts', lazy='dynamic', cascade='all, delete-orphan'))


class LineDutyDept(db.Model):
    """条线-职能部门映射表（一对一：一个职能部门只能对应一个条线）"""
    __tablename__ = 'line_duty_dept'
    id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.Integer, db.ForeignKey('line.id', ondelete='CASCADE'), nullable=False)
    department = db.Column(db.String(200), unique=True, nullable=False, comment='职能部门名称')
    line = db.relationship('Line', backref=db.backref('duty_depts', lazy='dynamic', cascade='all, delete-orphan'))


class Catalog(db.Model):
    __tablename__ = 'catalog'
    id = db.Column(db.Integer, primary_key=True)
    sequence = db.Column(db.Integer, comment='序号')
    name = db.Column(db.String(500), nullable=False, comment='目录名称')
    department = db.Column(db.String(200), comment='来源部门')
    line_id = db.Column(db.Integer, db.ForeignKey('line.id', ondelete='SET NULL'), nullable=True, comment='选定的条线ID')
    fields = db.Column(db.Text, comment='主要字段项(JSON数组)')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    line = db.relationship('Line', backref='catalogs')


class Duty(db.Model):
    __tablename__ = 'duty'
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(200), comment='部门名称')
    inner_org = db.Column(db.String(200), comment='内设机构')
    duty_name = db.Column(db.String(500), comment='职能名称')
    line_id = db.Column(db.Integer, db.ForeignKey('line.id', ondelete='SET NULL'), nullable=True, comment='映射条线ID')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    line = db.relationship('Line', backref='duties')


class MatchResult(db.Model):
    __tablename__ = 'match_result'
    id = db.Column(db.Integer, primary_key=True)
    catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id', ondelete='SET NULL'), nullable=True)
    duty_id = db.Column(db.Integer, db.ForeignKey('duty.id', ondelete='SET NULL'), nullable=True)
    catalog_name = db.Column(db.String(500), comment='目录名称')
    duty_name = db.Column(db.String(500), comment='职能名称')
    department = db.Column(db.String(200), comment='部门名称')
    line_name = db.Column(db.String(100), comment='条线名称')
    matched_data = db.Column(db.Text, comment='匹配结果JSON')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
