import re
from typing import Tuple

class ReferenceValidator:
    """Referans verilerini doğrulayan sınıf"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Email doğrula"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_doi(doi: str) -> bool:
        """DOI doğrula"""
        pattern = r'^10\.\d{4,}/.*$'
        return re.match(pattern, doi) is not None
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """URL doğrula"""
        pattern = r'^https?://[^\s]+$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def validate_year(year: str) -> bool:
        """Yıl doğrula"""
        if not year.isdigit():
            return False
        year_int = int(year)
        return 1450 < year_int <= 2100  # Basılı yayınların başlangıcından sonra
    
    @staticmethod
    def validate_reference_format(format_name: str) -> bool:
        """Referans formatını doğrula"""
        valid_formats = ['APA', 'MLA', 'Chicago', 'IEEE']
        return format_name.upper() in valid_formats
