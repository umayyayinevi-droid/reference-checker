import re
import json
from typing import Dict, List, Tuple
import PyPDF2

class ReferenceParser:
    """Referans metinlerini ayrıştıran sınıf"""
    
    def __init__(self):
        # Referans format desenleri
        self.apa_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]*)*(?:\s*&\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]*)*)*)\s*\((\d{4})\)\.\s*([^.]+)\.'
        self.mla_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]*)*(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]*)*)*)\s*\.?\s*["\']?([^."\']*)'
        self.chicago_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]*)*(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]*)*)*)\s*\.\s*([^.]+)\.'
    
    def parse(self, text: str, ref_format: str = 'auto') -> Dict:
        """Referans metnini ayrıştır"""
        if ref_format == 'auto':
            ref_format = self._detect_format(text)
        
        if ref_format.lower() == 'apa':
            return self._parse_apa(text)
        elif ref_format.lower() == 'mla':
            return self._parse_mla(text)
        elif ref_format.lower() == 'chicago':
            return self._parse_chicago(text)
        elif ref_format.lower() == 'ieee':
            return self._parse_ieee(text)
        else:
            return self._parse_generic(text)
    
    def _detect_format(self, text: str) -> str:
        """Format otomatik algıla"""
        # Basit algılama kuralları
        if '(' in text and ')' in text and '.' in text:
            if re.search(r'\(\d{4}\)', text):
                return 'APA'
        if re.search(r'retrieved from', text, re.IGNORECASE):
            return 'MLA'
        if re.search(r'\d{1,3}\. ', text):
            return 'IEEE'
        return 'Generic'
    
    def _parse_apa(self, text: str) -> Dict:
        """APA formatını ayrıştır"""
        result = {
            'format': 'APA',
            'authors': [],
            'year': None,
            'title': None,
            'journal': None,
            'volume': None,
            'issue': None,
            'pages': None,
            'doi': None,
            'url': None
        }
        
        # Yazarları çıkar
        author_match = re.search(r'^([^(]+)', text)
        if author_match:
            authors_str = author_match.group(1).strip()
            result['authors'] = [a.strip() for a in authors_str.split('&')]
        
        # Yılı çıkar
        year_match = re.search(r'\((\d{4})\)', text)
        if year_match:
            result['year'] = int(year_match.group(1))
        
        # Başlığı çıkar
        title_match = re.search(r'\(\d{4}\)\.\s*([^.]+)\.', text)
        if title_match:
            result['title'] = title_match.group(1).strip()
        
        # DOI'yi çıkar
        doi_match = re.search(r'doi:\s*([\d.]+/[^\s,)]+)', text, re.IGNORECASE)
        if doi_match:
            result['doi'] = doi_match.group(1)
        
        # URL'yi çıkar
        url_match = re.search(r'https?://[^\s,)]+', text)
        if url_match:
            result['url'] = url_match.group(0)
        
        return result
    
    def _parse_mla(self, text: str) -> Dict:
        """MLA formatını ayrıştır"""
        result = {
            'format': 'MLA',
            'authors': [],
            'year': None,
            'title': None,
            'journal': None,
            'volume': None,
            'issue': None,
            'pages': None,
            'doi': None,
            'url': None
        }
        
        # Yazarları çıkar
        author_match = re.search(r'^([^.]+)\.', text)
        if author_match:
            authors_str = author_match.group(1).strip()
            result['authors'] = [a.strip() for a in authors_str.split(',')]
        
        # Yılı çıkar
        year_match = re.search(r'(\d{4})', text)
        if year_match:
            result['year'] = int(year_match.group(1))
        
        # URL'yi çıkar
        url_match = re.search(r'https?://[^\s,)]+', text)
        if url_match:
            result['url'] = url_match.group(0)
        
        return result
    
    def _parse_chicago(self, text: str) -> Dict:
        """Chicago formatını ayrıştır"""
        result = {
            'format': 'Chicago',
            'authors': [],
            'year': None,
            'title': None,
            'journal': None,
            'volume': None,
            'issue': None,
            'pages': None,
            'doi': None,
            'url': None
        }
        
        # Yazarları çıkar
        author_match = re.search(r'^([^.]+)\.', text)
        if author_match:
            authors_str = author_match.group(1).strip()
            result['authors'] = [a.strip() for a in authors_str.split(',')]
        
        # Yılı çıkar
        year_match = re.search(r'\(([\d]{4})\)', text)
        if year_match:
            result['year'] = int(year_match.group(1))
        
        return result
    
    def _parse_ieee(self, text: str) -> Dict:
        """IEEE formatını ayrıştır"""
        result = {
            'format': 'IEEE',
            'authors': [],
            'year': None,
            'title': None,
            'journal': None,
            'volume': None,
            'issue': None,
            'pages': None,
            'doi': None,
            'url': None
        }
        
        # [#] başına yazarlar gelir
        author_match = re.search(r'\[\d+\]\s+([^,]+)', text)
        if author_match:
            result['authors'] = [author_match.group(1).strip()]
        
        # Yılı çıkar
        year_match = re.search(r'(\d{4})', text)
        if year_match:
            result['year'] = int(year_match.group(1))
        
        return result
    
    def _parse_generic(self, text: str) -> Dict:
        """Genel biçimde ayrıştır"""
        result = {
            'format': 'Generic',
            'authors': [],
            'year': None,
            'title': None,
            'journal': None,
            'volume': None,
            'issue': None,
            'pages': None,
            'doi': None,
            'url': None,
            'original_text': text
        }
        
        # Yılı çıkar
        year_match = re.search(r'(\d{4})', text)
        if year_match:
            result['year'] = int(year_match.group(1))
        
        # DOI'yi çıkar
        doi_match = re.search(r'doi:\s*([\d.]+/[^\s,)]+)', text, re.IGNORECASE)
        if doi_match:
            result['doi'] = doi_match.group(1)
        
        # URL'yi çıkar
        url_match = re.search(r'https?://[^\s,)]+', text)
        if url_match:
            result['url'] = url_match.group(0)
        
        return result
    
    def parse_pdf(self, file) -> List[Dict]:
        """PDF dosyasından referansları çıkar"""
        references = []
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Referans bölümünü bul
            lines = text.split('\n')
            references = []
            for line in lines:
                if line.strip() and len(line.strip()) > 20:
                    parsed = self._parse_generic(line)
                    references.append(parsed)
        except Exception as e:
            print(f"PDF ayrıştırma hatası: {e}")
        
        return references
    
    def parse_text_file(self, file) -> List[Dict]:
        """Metin dosyasından referansları çıkar"""
        references = []
        try:
            content = file.read().decode('utf-8')
            lines = content.split('\n')
            
            for line in lines:
                if line.strip() and len(line.strip()) > 20:
                    parsed = self._parse_generic(line)
                    references.append(parsed)
        except Exception as e:
            print(f"Metin dosyası ayrıştırma hatası: {e}")
        
        return references
