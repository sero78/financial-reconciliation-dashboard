import json
import pandas as pd
import numpy as np

print("İnşaat proje maliyet verileri sentezleniyor...")
projeler = ["Atakent Konutları A Blok", "Yenibosna Ticaret Merkezi", "Bahçeşehir Villaları", "Halkalı Rezidans", "Başakşehir Alışveriş Merkezi"]

data = []
np.random.seed(10)
for p in projeler:
    butce = np.random.randint(5000000, 25000000)
    gerceklesen = butce * np.random.uniform(0.85, 1.20) # Kimi bütçe altı, kimi üstü
    data.append({
        "proje_adi": p,
        "butce": int(butce),
        "gerceklesen_maliyet": int(gerceklesen),
        "sapma_orani": round(((gerceklesen - butce) / butce) * 100, 2)
    })

df = pd.DataFrame(data)

# JSON olarak dışarı aktar
json_veri = df.to_json(orient="records", force_ascii=False)

# Tek dosyalık şık bir HTML/JS Dashboard şablonu yazıyoruz
html_icerik = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>İnşaat Proje Maliyet & Bütçe Yönetim Paneli</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }}
        .container {{ max-width: 1100px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        h1 {{ color: #1e293b; font-size: 24px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 25px; }}
        .card {{ background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Kuzu Grup - Proje Bütçe ve Gerçekleşen Maliyet Analizi</h1>
        <p>Otomatik Python pipeline ile beslenen interaktif yönetim paneli.</p>
        
        <div class="grid">
            <div class="card">
                <canvas id="maliyetChart"></canvas>
            </div>
            <div class="card">
                <canvas id="sapmaChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        const hammVeri = {json_veri};

        const projeler = hammVeri.map(item => item.proje_adi);
        const butceler = hammVeri.map(item => item.butce);
        const maliyetler = hammVeri.map(item => item.gerceklesen_maliyet);
        const sapmalar = hammVeri.map(item => item.sapma_orani);

        // 1. Grafik: Bütçe vs Gerçekleşen
        new Chart(document.getElementById('maliyetChart'), {{
            type: 'bar',
            data: {{
                labels: projeler,
                datasets: [
                    {{ label: 'Planlanan Bütçe', data: butceler, backgroundColor: '#3b82f6' }},
                    {{ label: 'Gerçekleşen Maliyet', data: maliyetler, backgroundColor: '#f59e0b' }}
                ]
            }},
            options: {{ responsive: true, plugins: {{ title: {{ display: true, text: 'Proje Bazlı Bütçe Karşılaştırması (TL)' }} }} }}
        }});

        // 2. Grafik: Sapma Oranları (%)
        new Chart(document.getElementById('sapmaChart'), {{
            type: 'bar',
            data: {{
                labels: projeler,
                datasets: [{{
                    label: 'Bütçe Sapma Oranı (%)',
                    data: sapmalar,
                    backgroundColor: sapmalar.map(val => val > 0 ? '#ef4444' : '#10b981')
                }}]
            }},
            options: {{ responsive: true, plugins: {{ title: {{ display: true, text: 'Bütçe Sapma Yüzdeleri (Kırmızı: Aşıldı, Yeşil: Tasarruf)' }} }} }}
        }});
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_icerik)

print("Başarılı! 'index.html' dashboard dosyası oluşturuldu. Tarayıcıda açarak canlı inceleyebilirsin.")