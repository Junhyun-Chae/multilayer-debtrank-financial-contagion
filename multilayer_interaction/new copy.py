

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

bis_path = Path("/Users/junhyunchae/Desktop/credit_/output/multilayer_results_BIS.xlsx")
un_path  = Path("/Users/junhyunchae/Desktop/credit_/output/multilayer_results_UN.xlsx")
out_dir  = Path("/Users/junhyunchae/Desktop/credit_/output")
out_dir.mkdir(parents=True, exist_ok=True)

ISO2_TO_3 = {
    "AU":"AUS","AT":"AUT","BE":"BEL","BR":"BRA","CA":"CAN","CH":"CHE","CL":"CHL",
    "DE":"DEU","DK":"DNK","ES":"ESP","FI":"FIN","FR":"FRA","GB":"GBR","HK":"HKG",
    "IE":"IRL","IT":"ITA","JP":"JPN","NL":"NLD","SE":"SWE","US":"USA"
}

desired_order = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
                 "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]

bis_xl = pd.ExcelFile(bis_path)
un_xl  = pd.ExcelFile(un_path)
periods = sorted(set(bis_xl.sheet_names) & set(un_xl.sheet_names))
if not periods:
    raise RuntimeError("두 파일에 공통 시트가 없습니다.")

def to_iso3(code: str) -> str:
    return ISO2_TO_3.get(code.strip(), code.strip())

raw_codes = bis_xl.parse(periods[0]).columns[1:]
countries = [to_iso3(c) for c in raw_codes]

countries = [c for c in desired_order if c in countries]
idx_order = [raw_codes.get_loc(c) if c in raw_codes else None for c in countries]


def hits_by_period(xl: pd.ExcelFile, threshold=0.08) -> pd.DataFrame:
    """
    Returns (country × period) DataFrame of 0/1 hits.
    """
    dfs = []
    for sh in periods:                        
        arr = xl.parse(sh).iloc[-1, 1:].astype(float).values
        hit = (arr >= threshold).astype(int)
        dfs.append(pd.Series(hit, name=sh, index=[to_iso3(c) for c in raw_codes]))
    tbl = pd.concat(dfs, axis=1)                   
    return tbl.loc[countries]                       

bis_tbl = hits_by_period(bis_xl)
un_tbl  = hits_by_period(un_xl)


by_q_path = out_dir / "threshold_hits_by_quarter.xlsx"
with pd.ExcelWriter(by_q_path) as writer:
    for q in periods:
        pd.DataFrame({
            "Country"  : countries,
            "BIS_hits" : bis_tbl[q].values,
            "UN_hits"  : un_tbl[q].values,
        }).to_excel(writer, sheet_name=q[:31], index=False)
print(f"✅ 분기별 hit 저장 → {by_q_path}")

bis_hits = bis_tbl.sum(axis=1).values
un_hits  = un_tbl.sum(axis=1).values

summary_path = out_dir / "threshold_hits_summary.xlsx"
pd.DataFrame({
    "Country"  : countries,
    "BIS_hits" : bis_hits,
    "UN_hits"  : un_hits,
}).to_excel(summary_path, index=False)
print(f"✅ 누적 hit 요약 저장 → {summary_path}")

def bubble(hits, base=3000, min_size=80):
    s = np.log1p(hits)
    return np.maximum(base * s / s.max(), min_size)

def plot_thresh(title, hits, color, outfile):
    plt.figure(figsize=(20,12))
    x = np.arange(len(countries))
    plt.scatter(x, hits, s=bubble(hits), c=color, alpha=.75)
    plt.xticks(x, countries, rotation=45, fontsize=24)
    plt.ylabel("Number of Failures (≥8%)", fontsize=28)
    plt.title(title, fontsize=32, pad=15)
    plt.grid(alpha=.3)
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()

plot_thresh("Threshold Model – BIS Layer (≥8% Failure)",
            bis_hits, 'blue',   out_dir/"threshold_BIS.png")
plot_thresh("Threshold Model – UN Layer (≥8% Failure)",
            un_hits,  'orange', out_dir/"threshold_UN.png")

print("✅ 그래프 저장 완료: threshold_BIS.png / threshold_UN.png")
