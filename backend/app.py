from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from config import config
from database import db, Reference, ReferenceCheck, CheckReport
import os
from datetime import datetime

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Yapılandırma
    app.config.from_object(config[config_name])
    
    # Veritabanı
    db.init_app(app)
    
    # CORS
    CORS(app)
    
    # Dizinler
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
    
    # Blueprint'ler
    from controllers.reference_controller import reference_bp
    from controllers.check_controller import check_bp
    
    app.register_blueprint(reference_bp, url_prefix='/api/references')
    app.register_blueprint(check_bp, url_prefix='/api/checks')
    
    # Veritabanı komutları
    with app.app_context():
        db.create_all()
    
    # Ana sayfa
    @app.route('/')
    def index():
        return {
            'status': 'ok',
            'message': 'Reference Checker API v1.0',
            'endpoints': {
                'references': '/api/references',
                'checks': '/api/checks',
                'frontend': '/static'
            }
        }
    
    # Hata işleme
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
