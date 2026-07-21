# Reference Checker - Akademik Referans Kontrol Yazılımı

Modern, açık kaynaklı bir akademik referans kontrol ve doğrulama aracı. Referanslarınızı otomatik olarak doğrulayın ve kapsamlı raporlar oluşturun.

## Özellikler

✅ **Çoklu Format Desteği**: APA, MLA, Chicago, IEEE
✅ **Akademik Veritabanları**: Google Scholar, CrossRef, PubMed, OpenAlex
✅ **Akıllı Ayrıştırma**: Metin, PDF, ve yapıştırma alanından referans okuma
✅ **Kapsamlı Kontroller**: 
   - Yazarları doğrulama
   - Yayın tarihini kontrol etme
   - URL geçerliliğini denetleme
   - İktibaslama tespiti
✅ **Detaylı Raporlar**: PDF/HTML/JSON çıktı
✅ **Yerel Depolama**: Tüm veriler güvenli şekilde saklanır

## Kurulum

```bash
git clone https://github.com/umayyayinevi-droid/reference-checker.git
cd reference-checker
bash setup.sh
```

## Kullanım

```bash
python backend/app.py
# http://localhost:5000 adresinde açılır
```

## Teknoloji

- **Backend**: Python 3.10+, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Veritabanlar**: SQLite (yerel)
- **API'ler**: CrossRef, OpenAlex, Google Scholar, PubMed

## Lisans

MIT License
