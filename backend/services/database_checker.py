import requests
import json
from typing import Tuple, Optional, List
from fuzzywuzzy import fuzz
import validators
from datetime import datetime

class DatabaseChecker:
    """Akademik veritabanlarından referans kontrol eden sınıf"""
    
    def __init__(self):
        self.crossref_url = "https://api.crossref.org/works"
        self.openalex_url = "https://api.openalex.org/works"
        self.pubmed_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.scholar_url = "https://scholar.google.com"
    
    def check_authors(self, title: str, authors: List[str]) -> Tuple[Optional[bool], float, str]:
        """Yazarları doğrula"""
        if not authors:
            return None, 0.0, "Yazar bilgisi bulunamadı"
        
        try:
            # CrossRef'ten kontrol et
            params = {'query': title, 'rows': 5}
            response = requests.get(self.crossref_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'items' in data['message']:
                    for item in data['message']['items']:
                        if 'author' in item:
                            db_authors = [author.get('family', '') for author in item['author']]
                            match_score = max([fuzz.token_set_ratio(auth, ' '.join(db_authors)) for auth in authors])
                            
                            if match_score > 70:
                                return True, match_score, f"Yazarlar doğrulandı (Skor: {match_score})"
                            else:
                                return False, match_score, f"Yazarlar eşleşmiyor (Skor: {match_score})"
        except Exception as e:
            return None, 0.0, f"Kontrol hatası: {str(e)}"
        
        return None, 0.0, "Veritabanında eşleşme bulunamadı"
    
    def check_date(self, year: Optional[int]) -> Tuple[Optional[bool], str]:
        """Yayın tarihini doğrula"""
        if not year:
            return None, "Yayın yılı bulunamadı"
        
        current_year = datetime.now().year
        
        if year > current_year:
            return False, f"Yayın yılı gelecekte ({year})"
        
        if year < 1450:  # Baskı makinesi icat edilmeden
            return False, f"Yayın yılı geçmişte çok ({year})"
        
        return True, f"Yayın yılı geçerli ({year})"
    
    def check_url(self, url: str) -> Tuple[Optional[bool], Optional[int], str]:
        """URL'yi kontrol et"""
        if not validators.url(url):
            return False, None, "Geçersiz URL formatı"
        
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            status_code = response.status_code
            
            if 200 <= status_code < 300:
                return True, status_code, f"URL erişilebilir ({status_code})"
            elif status_code == 404:
                return False, status_code, "URL bulunamadı (404)"
            else:
                return False, status_code, f"URL erişim sorunu ({status_code})"
        except requests.exceptions.Timeout:
            return False, None, "URL zaman aşımı"
        except requests.exceptions.ConnectionError:
            return False, None, "URL bağlantı hatası"
        except Exception as e:
            return None, None, f"URL kontrol hatası: {str(e)}"
    
    def search_databases(self, title: str, authors: List[str], year: Optional[int]) -> Tuple[str, float, str]:
        """Akademik veritabanlarında ara"""
        best_match = None
        best_score = 0
        details = {}
        
        # CrossRef arama
        try:
            cr_result, cr_score = self._search_crossref(title, authors, year)
            if cr_score > best_score:
                best_match = 'CrossRef'
                best_score = cr_score
                details['crossref'] = cr_result
        except Exception as e:
            details['crossref_error'] = str(e)
        
        # OpenAlex arama
        try:
            oa_result, oa_score = self._search_openalex(title, authors, year)
            if oa_score > best_score:
                best_match = 'OpenAlex'
                best_score = oa_score
                details['openalex'] = oa_result
        except Exception as e:
            details['openalex_error'] = str(e)
        
        # PubMed arama (biyomedikal kaynaklar)
        try:
            pm_result, pm_score = self._search_pubmed(title, authors, year)
            if pm_score > best_score:
                best_match = 'PubMed'
                best_score = pm_score
                details['pubmed'] = pm_result
        except Exception as e:
            details['pubmed_error'] = str(e)
        
        details_str = json.dumps(details, ensure_ascii=False)
        
        if best_match:
            return best_match, best_score, details_str
        else:
            return 'None', 0.0, json.dumps({'message': 'Veritabanında bulunamadı'}, ensure_ascii=False)
    
    def _search_crossref(self, title: str, authors: List[str], year: Optional[int]) -> Tuple[dict, float]:
        """CrossRef'te ara"""
        params = {'query': title, 'rows': 5}
        if year:
            params['query'] += f" {year}"
        
        response = requests.get(self.crossref_url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'message' in data and 'items' in data['message']:
                for item in data['message']['items']:
                    title_match = fuzz.token_set_ratio(title, item.get('title', [''])[0])
                    if title_match > 50:
                        return item, title_match / 100
        
        return {}, 0.0
    
    def _search_openalex(self, title: str, authors: List[str], year: Optional[int]) -> Tuple[dict, float]:
        """OpenAlex'te ara"""
        params = {'search': title}
        response = requests.get(self.openalex_url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                item = data['results'][0]
                title_match = fuzz.token_set_ratio(title, item.get('title', ''))
                if title_match > 50:
                    return item, title_match / 100
        
        return {}, 0.0
    
    def _search_pubmed(self, title: str, authors: List[str], year: Optional[int]) -> Tuple[dict, float]:
        """PubMed'de ara"""
        params = {
            'db': 'pubmed',
            'term': title,
            'rettype': 'json',
            'retmax': 5
        }
        
        response = requests.get(self.pubmed_url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                if len(data['esearchresult']['idlist']) > 0:
                    return {'found': True, 'count': len(data['esearchresult']['idlist'])}, 0.8
        
        return {}, 0.0
    
    def check_plagiarism(self, text: str) -> Tuple[float, str]:
        """İntihası kontrol et (basit benzerlik kontrol)"""
        # Gerçek intihas tespiti için ek servislerin integrasyonu gerekir
        # Şimdilik basit bir skoru döndürüyoruz
        
        if len(text) < 10:
            return 0.0, "Metin çok kısa"
        
        # Gerçek uygulamada Turnitin, Copyscape gibi servislere entegre edilir
        # Şimdilik 0 döndürüyoruz (intihas yok)
        return 0.0, "İntihas tespiti yapılamadı"
    
    def determine_status(self, check) -> str:
        """Genel kontrol durumunu belirle"""
        error_count = 0
        warning_count = 0
        
        if check.author_valid is False:
            error_count += 1
        elif check.author_valid is None:
            warning_count += 1
        
        if check.date_valid is False:
            error_count += 1
        
        if check.url_valid is False:
            error_count += 1
        
        if check.plagiarism_score and check.plagiarism_score > 30:
            warning_count += 1
        
        if error_count > 0:
            return 'error'
        elif warning_count > 0:
            return 'warning'
        else:
            return 'verified'
