#!/bin/bash

echo "🚀 Reference Checker Kurulumu Başlıyor..."
echo ""

# Python versiyonu kontrolü
echo "✓ Python versiyonu kontrol ediliyor..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 bulunamadı. Lütfen Python 3.10+ kurun."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION bulundu"
echo ""

# Virtual environment oluştur
echo "✓ Virtual environment oluşturuluyor..."
python3 -m venv venv
source venv/bin/activate
echo "✓ Virtual environment aktif edildi"
echo ""

# Gereksinimleri yükle
echo "✓ Bağımlılıklar yükleniyor..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Bağımlılıklar başarıyla yüklendi"
echo ""

# Dizin yapısı oluştur
echo "✓ Dizin yapısı oluşturuluyor..."
mkdir -p backend/controllers backend/services backend/utils
mkdir -p frontend/css frontend/js
mkdir -p uploads reports
echo "✓ Dizinler oluşturuldu"
echo ""

echo "✨ Kurulum tamamlandı!"
echo ""
echo "Başlamak için:"
echo "  1. source venv/bin/activate"
echo "  2. python backend/app.py"
echo ""
echo "Tarayıcıda açın: http://localhost:5000"