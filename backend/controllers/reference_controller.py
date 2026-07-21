from flask import Blueprint, request, jsonify
from database import db, Reference
from services.reference_parser import ReferenceParser
import json

reference_bp = Blueprint('references', __name__)
parser = ReferenceParser()

@reference_bp.route('/', methods=['GET'])
def get_references():
    """Tüm referansları getir"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    references = Reference.query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': references.total,
        'pages': references.pages,
        'current_page': page,
        'data': [ref.to_dict() for ref in references.items]
    })

@reference_bp.route('/<int:ref_id>', methods=['GET'])
def get_reference(ref_id):
    """Belirli referansı getir"""
    reference = Reference.query.get_or_404(ref_id)
    return jsonify(reference.to_dict())

@reference_bp.route('/', methods=['POST'])
def create_reference():
    """Yeni referans oluştur"""
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    reference = Reference(
        title=data.get('title'),
        authors=json.dumps(data.get('authors', [])),
        year=data.get('year'),
        doi=data.get('doi'),
        url=data.get('url'),
        journal=data.get('journal'),
        volume=data.get('volume'),
        issue=data.get('issue'),
        pages=data.get('pages'),
        format=data.get('format', 'APA'),
        original_text=data.get('original_text')
    )
    
    db.session.add(reference)
    db.session.commit()
    
    return jsonify(reference.to_dict()), 201

@reference_bp.route('/parse', methods=['POST'])
def parse_reference():
    """Referans metnini ayrıştır"""
    data = request.get_json()
    
    if not data.get('text'):
        return jsonify({'error': 'Text is required'}), 400
    
    ref_format = data.get('format', 'auto')
    
    try:
        parsed = parser.parse(data['text'], ref_format)
        return jsonify(parsed)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@reference_bp.route('/batch', methods=['POST'])
def batch_parse():
    """Çoklu referans ayrıştır"""
    data = request.get_json()
    
    if not data.get('references'):
        return jsonify({'error': 'References array is required'}), 400
    
    results = []
    for ref_text in data['references']:
        try:
            parsed = parser.parse(ref_text, data.get('format', 'auto'))
            results.append(parsed)
        except Exception as e:
            results.append({'error': str(e)})
    
    return jsonify({'total': len(results), 'results': results})

@reference_bp.route('/upload', methods=['POST'])
def upload_file():
    """PDF veya metin dosyası yükle"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Dosyayı ayrıştır
        if file.filename.endswith('.pdf'):
            references = parser.parse_pdf(file)
        else:
            references = parser.parse_text_file(file)
        
        return jsonify({
            'count': len(references),
            'references': references
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@reference_bp.route('/<int:ref_id>', methods=['PUT'])
def update_reference(ref_id):
    """Referansı güncelle"""
    reference = Reference.query.get_or_404(ref_id)
    data = request.get_json()
    
    reference.title = data.get('title', reference.title)
    reference.authors = json.dumps(data.get('authors', json.loads(reference.authors)))
    reference.year = data.get('year', reference.year)
    reference.doi = data.get('doi', reference.doi)
    reference.url = data.get('url', reference.url)
    reference.journal = data.get('journal', reference.journal)
    reference.format = data.get('format', reference.format)
    
    db.session.commit()
    
    return jsonify(reference.to_dict())

@reference_bp.route('/<int:ref_id>', methods=['DELETE'])
def delete_reference(ref_id):
    """Referansı sil"""
    reference = Reference.query.get_or_404(ref_id)
    db.session.delete(reference)
    db.session.commit()
    
    return '', 204
