from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Reference(db.Model):
    """Referans modeli"""
    __tablename__ = 'references'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    authors = db.Column(db.String(1000))  # JSON formatında
    year = db.Column(db.Integer)
    doi = db.Column(db.String(100), unique=True, sparse=True)
    url = db.Column(db.String(500))
    journal = db.Column(db.String(300))
    volume = db.Column(db.String(50))
    issue = db.Column(db.String(50))
    pages = db.Column(db.String(50))
    format = db.Column(db.String(20))  # APA, MLA, Chicago, IEEE
    original_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    checks = db.relationship('ReferenceCheck', backref='reference', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'authors': json.loads(self.authors) if self.authors else [],
            'year': self.year,
            'doi': self.doi,
            'url': self.url,
            'journal': self.journal,
            'volume': self.volume,
            'issue': self.issue,
            'pages': self.pages,
            'format': self.format,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ReferenceCheck(db.Model):
    """Referans kontrol sonuçları"""
    __tablename__ = 'reference_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    reference_id = db.Column(db.Integer, db.ForeignKey('references.id'), nullable=False)
    
    author_valid = db.Column(db.Boolean, default=None)
    author_match_score = db.Column(db.Float)
    author_notes = db.Column(db.Text)
    
    date_valid = db.Column(db.Boolean, default=None)
    date_notes = db.Column(db.Text)
    
    url_valid = db.Column(db.Boolean, default=None)
    url_status_code = db.Column(db.Integer)
    url_notes = db.Column(db.Text)
    
    plagiarism_score = db.Column(db.Float)  # 0-100
    plagiarism_notes = db.Column(db.Text)
    
    database_found = db.Column(db.String(100))  # CrossRef, OpenAlex, PubMed, vb.
    database_match_score = db.Column(db.Float)
    database_details = db.Column(db.Text)  # JSON
    
    overall_status = db.Column(db.String(20))  # verified, warning, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'reference_id': self.reference_id,
            'author_valid': self.author_valid,
            'author_match_score': self.author_match_score,
            'date_valid': self.date_valid,
            'url_valid': self.url_valid,
            'url_status_code': self.url_status_code,
            'plagiarism_score': self.plagiarism_score,
            'database_found': self.database_found,
            'overall_status': self.overall_status,
            'created_at': self.created_at.isoformat()
        }

class CheckReport(db.Model):
    """Kontrol raporları"""
    __tablename__ = 'check_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    total_references = db.Column(db.Integer)
    verified_count = db.Column(db.Integer, default=0)
    warning_count = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    report_format = db.Column(db.String(20))  # HTML, PDF, JSON
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'total_references': self.total_references,
            'verified_count': self.verified_count,
            'warning_count': self.warning_count,
            'error_count': self.error_count,
            'created_at': self.created_at.isoformat()
        }
