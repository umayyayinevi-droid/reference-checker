from flask import Blueprint, request, jsonify, send_file
from database import db, Reference, ReferenceCheck, CheckReport
from services.database_checker import DatabaseChecker
from services.report_generator import ReportGenerator
import json
import os

check_bp = Blueprint('checks', __name__)
db_checker = DatabaseChecker()
report_gen = ReportGenerator()

@check_bp.route('/reference/<int:ref_id>', methods=['POST'])
def check_reference(ref_id):
    """Referansı kontrol et"""
    reference = Reference.query.get_or_404(ref_id)
    
    # Mevcut kontrolü kontrol et
    existing_check = ReferenceCheck.query.filter_by(reference_id=ref_id).first()
    if existing_check:
        db.session.delete(existing_check)
        db.session.commit()
    
    # Yeni kontrol oluştur
    check = ReferenceCheck(reference_id=ref_id)
    
    # Yazarları kontrol et
    check.author_valid, check.author_match_score, check.author_notes = db_checker.check_authors(
        reference.title,
        json.loads(reference.authors) if reference.authors else []
    )
    
    # Tarihi kontrol et
    check.date_valid, check.date_notes = db_checker.check_date(reference.year)
    
    # URL'yi kontrol et
    if reference.url:
        check.url_valid, check.url_status_code, check.url_notes = db_checker.check_url(reference.url)
    
    # Veritabanlarında ara
    check.database_found, check.database_match_score, check.database_details = db_checker.search_databases(
        reference.title,
        json.loads(reference.authors) if reference.authors else [],
        reference.year
    )
    
    # İntihaslama kontrol et
    check.plagiarism_score, check.plagiarism_notes = db_checker.check_plagiarism(reference.title)
    
    # Genel durumu belirle
    check.overall_status = db_checker.determine_status(check)
    
    db.session.add(check)
    db.session.commit()
    
    return jsonify(check.to_dict()), 201

@check_bp.route('/reference/<int:ref_id>', methods=['GET'])
def get_check_result(ref_id):
    """Kontrol sonucunu getir"""
    check = ReferenceCheck.query.filter_by(reference_id=ref_id).first_or_404()
    return jsonify(check.to_dict())

@check_bp.route('/batch', methods=['POST'])
def batch_check():
    """Çoklu referansları kontrol et"""
    data = request.get_json()
    
    if not data.get('reference_ids'):
        return jsonify({'error': 'Reference IDs required'}), 400
    
    results = []
    for ref_id in data['reference_ids']:
        reference = Reference.query.get(ref_id)
        if reference:
            check = ReferenceCheck(reference_id=ref_id)
            
            check.author_valid, check.author_match_score, check.author_notes = db_checker.check_authors(
                reference.title,
                json.loads(reference.authors) if reference.authors else []
            )
            check.date_valid, check.date_notes = db_checker.check_date(reference.year)
            
            if reference.url:
                check.url_valid, check.url_status_code, check.url_notes = db_checker.check_url(reference.url)
            
            check.database_found, check.database_match_score, check.database_details = db_checker.search_databases(
                reference.title,
                json.loads(reference.authors) if reference.authors else [],
                reference.year
            )
            
            check.plagiarism_score, check.plagiarism_notes = db_checker.check_plagiarism(reference.title)
            check.overall_status = db_checker.determine_status(check)
            
            db.session.add(check)
            results.append(check.to_dict())
    
    db.session.commit()
    
    return jsonify({'total': len(results), 'results': results}), 201

@check_bp.route('/report', methods=['POST'])
def generate_report():
    """Rapor oluştur"""
    data = request.get_json()
    
    if not data.get('reference_ids'):
        return jsonify({'error': 'Reference IDs required'}), 400
    
    report_format = data.get('format', 'html')  # html, pdf, json
    report_name = data.get('name', f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    
    references = Reference.query.filter(Reference.id.in_(data['reference_ids'])).all()
    checks = ReferenceCheck.query.filter(ReferenceCheck.reference_id.in_(data['reference_ids'])).all()
    
    if report_format == 'html':
        file_path = report_gen.generate_html_report(references, checks, report_name)
    elif report_format == 'pdf':
        file_path = report_gen.generate_pdf_report(references, checks, report_name)
    elif report_format == 'json':
        file_path = report_gen.generate_json_report(references, checks, report_name)
    else:
        return jsonify({'error': 'Invalid format'}), 400
    
    # Raporu veritabanına kaydet
    report = CheckReport(
        name=report_name,
        total_references=len(references),
        verified_count=sum(1 for c in checks if c.overall_status == 'verified'),
        warning_count=sum(1 for c in checks if c.overall_status == 'warning'),
        error_count=sum(1 for c in checks if c.overall_status == 'error'),
        report_format=report_format,
        file_path=file_path
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify(report.to_dict()), 201

@check_bp.route('/report/<int:report_id>/download', methods=['GET'])
def download_report(report_id):
    """Raporu indir"""
    report = CheckReport.query.get_or_404(report_id)
    
    if not os.path.exists(report.file_path):
        return jsonify({'error': 'Report file not found'}), 404
    
    return send_file(
        report.file_path,
        as_attachment=True,
        download_name=f"{report.name}.{report.report_format}"
    )

from datetime import datetime
