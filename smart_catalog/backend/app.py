"""智能编目 — Flask 后端入口"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# 确保模块可以被正确导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


def create_app():
    app = Flask(__name__, static_folder=None)

    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'intellicat-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'intellicat.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MATCH_API_URL'] = os.getenv('MATCH_API_URL', '')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

    CORS(app)

    from models import db
    db.init_app(app)

    with app.app_context():
        from routes.lines import lines_bp
        from routes.catalogs import catalogs_bp
        from routes.duties import duties_bp
        from routes.results import results_bp

        app.register_blueprint(lines_bp)
        app.register_blueprint(catalogs_bp)
        app.register_blueprint(duties_bp)
        app.register_blueprint(results_bp)

        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
