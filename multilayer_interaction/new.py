import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

bis_path = Path("/Users/junhyunchae/Desktop/credit_/output/multilayer_results_BIS.xlsx")
un_path  = Path("/Users/junhyunchae/Desktop/credit_/output/multilayer_results_UN.xlsx")

ISO2_TO_3 = {
    "AU": "AUS", "AT": "AUT", "BE": "BEL", "BR": "BRA", "CA": "CAN", "CH": "CHE", "CL": "CHL",
    "DE": "DEU", "DK": "DNK", "ES": "ESP", "FI": "FIN", "FR": "FRA", "GB": "GBR", "HK": "HKG",
    "IE": "IRL", "IT": "ITA", "JP": "JPN", "NL": "NLD", "SE": "SWE", "US": "USA"
}

desired_order = ["GBR", "USA", "JPN", "FRA", "DEU", "SWE", "FIN", "CHE", "ITA", "ESP",
                 "IRL", "NLD", "CAN", "BEL", "BRA", "AUT", "DNK", "HKG", "AUS", "CHL"]

bis_xl = pd.ExcelFile(bis_path)
un_xl = pd.ExcelFile(un_path)
periods = sorted(set(bis_xl.sheet_names) & set(un_xl.sheet_names))
if not periods:
    raise RuntimeError("두 파일에 공통된 시트가 없습니다.")

def to_iso3(code):
    code = str(code).strip()
    return ISO2_TO_3.get(code, code)

raw_codes = bis_xl.parse(periods[0]).columns[1:]
countries = [to_iso3(c) for c in raw_codes]
pos = {c: i for i, c in enumerate(countries)}
idx_order = [pos[c] for c in desired_order if c in pos]
labels = [countries[i] for i in idx_order]

def threshold_model(xl, threshold=0.08):
    hit = np.zeros(len(countries), int)
    for sheet in periods:
        arr = xl.parse(sheet).iloc[-1, 1:].astype(float).values
        hit += (arr >= threshold)
    return hit

bis_hits = threshold_model(bis_xl)
un_hits  = threshold_model(un_xl)

def norm(x): return (x - x.min()) / (x.max() - x.min() + 1e-12)
def bubble(hits, base=3000, min_size=80):
    s = np.log1p(hits)
    return np.maximum(base * s / s.max(), min_size)

bis_bub = bubble(bis_hits)
un_bub  = bubble(un_hits)

def plot_thresh(title, hits, bub, color, out_file):
    plt.figure(figsize=(20,12))
    x = np.arange(len(labels))
    plt.scatter(x, hits[idx_order], s=bub[idx_order], c=color, alpha=0.75)
    plt.xticks(x, labels, rotation=45, fontsize=24)
    plt.ylabel("Number of Failures (≥8%)", fontsize=28)
    plt.title(title, fontsize=32, pad=15)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.show()

plot_thresh("Threshold Model – BIS Layer (≥8% Failure)", bis_hits, bis_bub, 'blue', "threshold_BIS.png")
plot_thresh("Threshold Model – UN Layer (≥8% Failure)",  un_hits,  un_bub,  'orange', "threshold_UN.png")

print("✅ 저장 완료: threshold_BIS.png / threshold_UN.png")

out_path = Path("/Users/junhyunchae/Desktop/credit_/output/threshold_hits.xlsx")

df_hits = pd.DataFrame({
    "Country"   : labels,         
    "BIS_hits"  : bis_hits[idx_order], 
    "UN_hits"   : un_hits[idx_order],
})

df_hits.to_excel(out_path, index=False)
print(f"✅ 엑셀 저장 완료 → {out_path}")






import pandas as pd

df_thresh = pd.DataFrame({
    "Country"   : labels,
    "BIS_hits"  : bis_hits[idx_order],   
    "UN_hits"   : un_hits[idx_order],    
    "BIS_bubble": bis_bub[idx_order],   
    "UN_bubble":  un_bub[idx_order],    
})

pd.set_option("display.float_format", lambda x: f"{x:.6f}")
print("\n=== Threshold Model (≥8% Failure) Values ===")
print(df_thresh.to_string(index=False))
