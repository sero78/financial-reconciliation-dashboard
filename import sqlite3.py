import sqlite3
import pandas as pd
import numpy as np

print("[1/4] Örnek ERP ve Banka verileri sentezleniyor...")
np.random.seed(42)
n_records = 100

fatura_ids = [f"FT-2026-{i:03d}" for i in range(1, n_records + 1)]
tutar_erp = np.round(np.random.uniform(1000, 50000, n_records), 2)

# ERP kayıtları DataFrame'i
df_erp = pd.DataFrame({
    "fatura_id": fatura_ids,
    "tutar_erp": tutar_erp,
    "cari_unvan": np.random.choice(["Kuzey İnşaat A.Ş.", "Mega Beton Ltd.", "Atlas Altyapı", "Zirve Mimarlık"], n_records)
})

# Banka ekstreleri (Kasıtlı olarak bazı kuruş farkları ve eksik/fazla kayıtlar ekliyoruz)
df_banka = df_erp.copy()
# Rastgele 5 kayıtta tutar farkı yaratalım (Mutabakatsizlik simülasyonu)
fark_indexleri = [12, 34, 56, 78, 90]
for idx in fark_indexleri:
    df_banka.loc[idx, "tutar_erp"] += np.random.choice([-15.50, 100.00, 5.25])

df_banka.rename(columns={"tutar_erp": "tutar_banka"}, inplace=True)
# 3 faturayı bankadan uçuralım (Eksik kayıt simülasyonu)
df_banka = df_banka.drop([5, 45, 88]).reset_index(drop=True)

print("[2/4] SQLite veritabanı oluşturulup tablolar yükleniyor...")
conn = sqlite3.connect(":memory:") # Bellekte geçici DB
df_erp.to_sql("erp_kayitlari", conn, index=False, if_exists="replace")
df_banka.to_sql("banka_ekstresi", conn, index=False, if_exists="replace")

print("[3/4] SQL tabanlı mutabakat analizi gerçekleştiriliyor...")
merged_df = pd.merge(df_erp, df_banka, on="fatura_id", how="outer", suffixes=("_erp", "_banka"))
merged_df["tutar_erp"] = merged_df["tutar_erp"].fillna(0)
merged_df["tutar_banka"] = merged_df["tutar_banka"].fillna(0)
merged_df["fark"] = merged_df["tutar_erp"] - merged_df["tutar_banka"]

def durum_belirle(row):
    if row["tutar_banka"] == 0:
        return "ERP Kaydı Var, Bankada Yok (Eksik)"
    elif row["tutar_erp"] == 0:
        return "Banka Kaydı Var, ERP'de Yok (Fazla)"
    elif abs(row["fark"]) > 0.01:
        return "Tutar Uyuşmazlığı (Kuruş/Tutar Farkı)"
    else:
        return "Mutabık"

merged_df["mutabakat_durumu"] = merged_df.apply(durum_belirle, axis=1)

print("[4/4] Sonuçlar 'mutabakat_raporu.xlsx' olarak kaydediliyor...")
try:
    merged_df.to_excel("mutabakat_raporu.xlsx", index=False)
    print("Başarılı! 'mutabakat_raporu.xlsx' dosyası oluşturuldu.")
except Exception as e:
    print(f"Excel kaydedilemedi, CSV olarak kaydediliyor: {e}")
    merged_df.to_csv("mutabakat_raporu.csv", index=False)

print("\nÖzet Durum Dağılımı:")
print(merged_df["mutabakat_durumu"].value_counts())