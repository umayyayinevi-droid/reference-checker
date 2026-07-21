// API Base URL
const API_BASE = 'http://localhost:5000/api';

// Global değişkenler
let checkedReferences = [];
let currentReports = [];

// Tab Switching
function switchTab(tabName) {
    // Tab butonlarını güncelle
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Tab içeriklerini güncelle
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
}

// Yapıştırılan Referansları Kontrol Et
async function checkPastedReferences() {
    const text = document.getElementById('paste-area').value;
    const format = document.getElementById('format-select').value;
    
    if (!text.trim()) {
        alert('Lütfen referans metni giriniz');
        return;
    }
    
    // Satırları böl
    const references = text.split('\n').filter(ref => ref.trim().length > 0);
    
    try {
        // Her referansı ayrıştır
        const parseResponse = await fetch(`${API_BASE}/references/batch`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                references: references,
                format: format
            })
        });
        
        const parseData = await parseResponse.json();
        
        // Referansları veritabanına kaydet
        for (let parsed of parseData.results) {
            const createResponse = await fetch(`${API_BASE}/references/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(parsed)
            });
            const reference = await createResponse.json();
            
            // Kontrol et
            const checkResponse = await fetch(`${API_BASE}/checks/reference/${reference.id}`, {
                method: 'POST'
            });
            const check = await checkResponse.json();
            
            checkedReferences.push({
                reference: reference,
                check: check
            });
        }
        
        displayResults();
    } catch (error) {
        console.error('Hata:', error);
        alert('Referanslar kontrol edilirken hata oluştu');
    }
}

// Dosya Yükle
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = '#f0f0f0';
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.backgroundColor = '';
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = '';
        handleFileUpload(e.dataTransfer.files[0]);
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/references/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Referansları kaydet ve kontrol et
        for (let parsed of data.references) {
            const createResponse = await fetch(`${API_BASE}/references/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(parsed)
            });
            const reference = await createResponse.json();
            
            const checkResponse = await fetch(`${API_BASE}/checks/reference/${reference.id}`, {
                method: 'POST'
            });
            const check = await checkResponse.json();
            
            checkedReferences.push({
                reference: reference,
                check: check
            });
        }
        
        displayResults();
    } catch (error) {
        console.error('Hata:', error);
        alert('Dosya yüklenirken hata oluştu');
    }
}

// Manuel Referans Ekle
async function addManualReference(event) {
    event.preventDefault();
    
    const reference = {
        title: document.getElementById('title').value,
        authors: document.getElementById('authors').value.split(',').map(a => a.trim()),
        year: parseInt(document.getElementById('year').value) || null,
        journal: document.getElementById('journal').value,
        doi: document.getElementById('doi').value,
        url: document.getElementById('url').value,
        format: 'Generic'
    };
    
    try {
        const createResponse = await fetch(`${API_BASE}/references/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(reference)
        });
        const refData = await createResponse.json();
        
        const checkResponse = await fetch(`${API_BASE}/checks/reference/${refData.id}`, {
            method: 'POST'
        });
        const check = await checkResponse.json();
        
        checkedReferences.push({
            reference: refData,
            check: check
        });
        
        document.getElementById('manualForm').reset();
        displayResults();
    } catch (error) {
        console.error('Hata:', error);
        alert('Referans eklenirken hata oluştu');
    }
}

// Sonuçları Görüntüle
function displayResults() {
    const resultsSection = document.getElementById('results');
    const resultsList = document.getElementById('resultsList');
    
    resultsList.innerHTML = '';
    
    for (let item of checkedReferences) {
        const ref = item.reference;
        const check = item.check;
        
        const card = document.createElement('div');
        card.className = 'result-card';
        card.innerHTML = `
            <h3>${ref.title}</h3>
            <p><strong>Yazarlar:</strong> ${ref.authors.join(', ') || 'Belirtilmemiş'}</p>
            <p><strong>Yıl:</strong> ${ref.year || 'Belirtilmemiş'}</p>
            <p><strong>Format:</strong> ${ref.format}</p>
            
            <div style="margin-top: 1rem; border-top: 1px solid #ddd; padding-top: 1rem;">
                <p><strong>Kontrol Sonuçları:</strong></p>
                <p>Yazarlar: ${check.author_valid === true ? '✓' : check.author_valid === false ? '✗' : '?'} ${check.author_match_score ? `(${check.author_match_score.toFixed(0)}%)` : ''}</p>
                <p>Tarih: ${check.date_valid === true ? '✓' : check.date_valid === false ? '✗' : '?'}</p>
                <p>URL: ${check.url_valid === true ? '✓' : check.url_valid === false ? '✗' : '?'}</p>
                <p>Veritabanı: ${check.database_found || 'Bulunamadı'}</p>
            </div>
            
            <span class="status ${check.overall_status}">${check.overall_status.toUpperCase()}</span>
        `;
        resultsList.appendChild(card);
    }
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Rapor Oluştur
async function generateReport(format) {
    if (checkedReferences.length === 0) {
        alert('Kontrol edilmiş referans bulunmuyor');
        return;
    }
    
    const referenceIds = checkedReferences.map(item => item.reference.id);
    
    try {
        const response = await fetch(`${API_BASE}/checks/report`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                reference_ids: referenceIds,
                format: format,
                name: `rapor_${new Date().getTime()}`
            })
        });
        
        const report = await response.json();
        currentReports.push(report);
        
        // Raporu indir
        downloadReport(report.id, format);
    } catch (error) {
        console.error('Hata:', error);
        alert('Rapor oluşturulurken hata oluştu');
    }
}

// Raporu İndir
async function downloadReport(reportId, format) {
    try {
        const response = await fetch(`${API_BASE}/checks/report/${reportId}/download`);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `rapor.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Hata:', error);
        alert('Rapor indirilirken hata oluştu');
    }
}

// Sayfa Yüklendiğinde
window.addEventListener('DOMContentLoaded', () => {
    setupFileUpload();
});
