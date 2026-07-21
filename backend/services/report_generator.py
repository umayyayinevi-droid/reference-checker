import json
from datetime import datetime
from jinja2 import Template
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

class ReportGenerator:
    """Kontrol raporları oluşturan sınıf"""
    
    def __init__(self):
        self.reports_dir = 'reports'
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_html_report(self, references, checks, report_name):
        """HTML rapor oluştur"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{{ report_name }} - Referans Kontrol Raporu</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                .summary { background: #f0f0f0; padding: 10px; margin: 10px 0; }
                .verified { color: green; font-weight: bold; }
                .warning { color: orange; font-weight: bold; }
                .error { color: red; font-weight: bold; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
            </style>
        </head>
        <body>
            <h1>Referans Kontrol Raporu</h1>
            <p><strong>Rapor Adı:</strong> {{ report_name }}</p>
            <p><strong>Tarih:</strong> {{ date }}</p>
            
            <div class="summary">
                <h2>Özet</h2>
                <p>Toplam Referans: {{ total }}</p>
                <p><span class="verified">Doğrulanmış: {{ verified }}</span></p>
                <p><span class="warning">Uyarı: {{ warning }}</span></p>
                <p><span class="error">Hata: {{ error }}</span></p>
            </div>
            
            <h2>Detaylı Kontroller</h2>
            <table>
                <tr>
                    <th>Başlık</th>
                    <th>Yazarlar</th>
                    <th>Yıl</th>
                    <th>Yazar Kontrol</th>
                    <th>Tarih Kontrol</th>
                    <th>URL Kontrol</th>
                    <th>Durum</th>
                </tr>
                {% for ref, check in ref_check_pairs %}
                <tr>
                    <td>{{ ref.title[:50] }}</td>
                    <td>{{ ref.authors[:50] }}</td>
                    <td>{{ ref.year }}</td>
                    <td>
                        {% if check.author_valid %}
                            <span class="verified">✓</span>
                        {% elif check.author_valid == False %}
                            <span class="error">✗</span>
                        {% else %}
                            <span class="warning">?</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if check.date_valid %}
                            <span class="verified">✓</span>
                        {% elif check.date_valid == False %}
                            <span class="error">✗</span>
                        {% else %}
                            <span class="warning">?</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if check.url_valid %}
                            <span class="verified">✓</span>
                        {% elif check.url_valid == False %}
                            <span class="error">✗</span>
                        {% else %}
                            <span class="warning">?</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if check.overall_status == 'verified' %}
                            <span class="verified">Doğrulandi</span>
                        {% elif check.overall_status == 'warning' %}
                            <span class="warning">Uyarı</span>
                        {% else %}
                            <span class="error">Hata</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        
        template = Template(html_template)
        
        # Referans-Kontrol çiftlerini oluştur
        ref_check_pairs = []
        for ref in references:
            check = next((c for c in checks if c.reference_id == ref.id), None)
            if check:
                ref_check_pairs.append((ref, check))
        
        verified_count = sum(1 for _, c in ref_check_pairs if c.overall_status == 'verified')
        warning_count = sum(1 for _, c in ref_check_pairs if c.overall_status == 'warning')
        error_count = sum(1 for _, c in ref_check_pairs if c.overall_status == 'error')
        
        html_content = template.render(
            report_name=report_name,
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total=len(references),
            verified=verified_count,
            warning=warning_count,
            error=error_count,
            ref_check_pairs=ref_check_pairs
        )
        
        file_path = os.path.join(self.reports_dir, f"{report_name}.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return file_path
    
    def generate_pdf_report(self, references, checks, report_name):
        """PDF rapor oluştur"""
        file_path = os.path.join(self.reports_dir, f"{report_name}.pdf")
        
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Başlık
        story.append(Paragraph(f"<b>Referans Kontrol Raporu: {report_name}</b>", styles['Heading1']))
        story.append(Spacer(1, 0.3*inch))
        
        # Tarih
        story.append(Paragraph(f"<b>Tarih:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Özet
        verified_count = sum(1 for c in checks if c.overall_status == 'verified')
        warning_count = sum(1 for c in checks if c.overall_status == 'warning')
        error_count = sum(1 for c in checks if c.overall_status == 'error')
        
        summary_data = [
            ['Toplam Referans', str(len(references))],
            ['Doğrulanmış', str(verified_count)],
            ['Uyarı', str(warning_count)],
            ['Hata', str(error_count)]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        story.append(PageBreak())
        
        # Tablo
        story.append(Paragraph("<b>Detaylı Kontroller</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        table_data = [['Başlık', 'Yıl', 'Yazar', 'Tarih', 'URL', 'Durum']]
        
        for ref in references:
            check = next((c for c in checks if c.reference_id == ref.id), None)
            if check:
                row = [
                    ref.title[:30] + '...' if len(ref.title) > 30 else ref.title,
                    str(ref.year) if ref.year else '-',
                    '✓' if check.author_valid else ('✗' if check.author_valid == False else '?'),
                    '✓' if check.date_valid else ('✗' if check.date_valid == False else '?'),
                    '✓' if check.url_valid else ('✗' if check.url_valid == False else '?'),
                    check.overall_status.upper()
                ]
                table_data.append(row)
        
        table = Table(table_data, colWidths=[2*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        doc.build(story)
        return file_path
    
    def generate_json_report(self, references, checks, report_name):
        """JSON rapor oluştur"""
        verified_count = sum(1 for c in checks if c.overall_status == 'verified')
        warning_count = sum(1 for c in checks if c.overall_status == 'warning')
        error_count = sum(1 for c in checks if c.overall_status == 'error')
        
        report_data = {
            'name': report_name,
            'date': datetime.now().isoformat(),
            'summary': {
                'total': len(references),
                'verified': verified_count,
                'warning': warning_count,
                'error': error_count
            },
            'references': []
        }
        
        for ref in references:
            check = next((c for c in checks if c.reference_id == ref.id), None)
            if check:
                report_data['references'].append({
                    'reference': ref.to_dict(),
                    'check': check.to_dict()
                })
        
        file_path = os.path.join(self.reports_dir, f"{report_name}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return file_path
