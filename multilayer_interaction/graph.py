import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

bis_path = Path("./output/BIS_multiplex_results.xlsx")
un_path  = Path("./output/UN_multiplex_results.xlsx")

ISO2_TO_3 = {
    "AU":"AUS","AT":"AUT","BE":"BEL","BR":"BRA","CA":"CAN","CH":"CHE","CL":"CHL",
    "DE":"DEU","DK":"DNK","ES":"ESP","FI":"FIN","FR":"FRA","GB":"GBR","HK":"HKG",
    "IE":"IRL","IT":"ITA","JP":"JPN","NL":"NLD","SE":"SWE","US":"USA"
}
desired_order = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
                 "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]

def to_iso3(col):
    col = str(col).strip()
    return ISO2_TO_3.get(col, col)

bis_xl = pd.ExcelFile(bis_path)
un_xl  = pd.ExcelFile(un_path)
periods = sorted(set(bis_xl.sheet_names) & set(un_xl.sheet_names))
if not periods:
    raise RuntimeError("No common sheets (periods) in BIS and UN Excel files.")

raw_codes = bis_xl.parse(periods[0]).columns[1:]
countries = [to_iso3(c) for c in raw_codes]
pos = {c: i for i, c in enumerate(countries)}
idx_order = [pos[c] for c in desired_order if c in pos]
labels = [countries[i] for i in idx_order]

def agg_lastrow(xl):
    _sum = np.zeros(len(countries))
    _cnt = np.zeros(len(countries), int)
    for sheet in periods:
        df = xl.parse(sheet).iloc[-1, 1:].astype(float).values
        _sum += df
        _cnt += (df >= 1.0)
    return _sum[idx_order], _cnt[idx_order]

bis_sum, bis_cnt = agg_lastrow(bis_xl)
un_sum , un_cnt  = agg_lastrow(un_xl)

def minmax(x):
    x = np.asarray(x, float)
    return (x - x.min()) / (x.max() - x.min() + 1e-12)

def bubble(counts, emph=(29,32), base=4000, min_size=80):
    if counts.max() == 0:
        return np.full_like(counts, min_size)
    s = np.log1p(counts.astype(float))
    s[(counts >= emph[0]) & (counts <= emph[1])] *= 1.8
    scaled = base * s / s.max()
    return np.maximum(scaled, min_size)

bis_norm = minmax(bis_sum)
un_norm  = minmax(un_sum)
bis_bub  = bubble(bis_cnt)
un_bub   = bubble(un_cnt)

def plot_bis_un_comparison(norm_bis, norm_un, bub_bis, bub_un, labels, out_png):
    x = np.arange(len(labels))
    plt.figure(figsize=(20, 12))

    plt.scatter(x, norm_bis, s=bub_bis, c='blue', alpha=0.8, label="DebtRank BIS")
    plt.scatter(x, norm_un,  s=bub_un,  c='orange', alpha=0.8, label="DebtRank UN")

    plt.xticks(x, labels, rotation=45, fontsize=26)
    plt.ylabel("Normalized Risk Score", fontsize=30)
    plt.xlabel("Countries", fontsize=30)
    plt.title("DebtRank + Threshold (BIS vs UN)", fontsize=34, pad=18)
    plt.grid(alpha=0.25)
    plt.legend(fontsize=20, markerscale=0.6, loc='upper right')
    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.show()

plot_bis_un_comparison(bis_norm, un_norm, bis_bub, un_bub, labels,
                       "debt_rank_vertical_BIS_vs_UN.png")

print("✅ 그래프 저장 완료 → debt_rank_vertical_BIS_vs_UN.png")































import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path


bis_path = Path("./output/multilayer_results_BIS.xlsx")
un_path  = Path("./output/multilayer_results_UN.xlsx")

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
    raise RuntimeError("두 파일에 공통 분기 시트가 없습니다.")

def to_iso3(col):
    col = str(col).strip()
    if len(col) == 2 and col in ISO2_TO_3:
        return ISO2_TO_3[col]
    return col

raw_codes = bis_xl.parse(periods[0]).columns[1:]
countries = [to_iso3(c) for c in raw_codes]

pos = {c:i for i,c in enumerate(countries)}

idx_order = [pos[c] for c in desired_order if c in pos]
labels    = [countries[i] for i in idx_order]

def agg_lastrow(xl):
    _sum = np.zeros(len(countries))
    _cnt = np.zeros(len(countries), int)
    THR = 1.0
    for sheet in periods:
        last = xl.parse(sheet).iloc[-1, 1:].astype(float).values
        _sum += last
        _cnt += (last >= THR)
    return _sum[idx_order], _cnt[idx_order]

bis_sum, bis_cnt = agg_lastrow(bis_xl)
un_sum , un_cnt  = agg_lastrow(un_xl)

def minmax(x):
    x = np.asarray(x, float)
    return (x - x.min()) / (x.max() - x.min() + 1e-12)

def bubble(counts, emph=(29,32), base=4000, min_size=80):
    if counts.max() == 0:
        return np.full_like(counts, min_size)
    s = np.log1p(counts.astype(float))
    s[(counts >= emph[0]) & (counts <= emph[1])] *= 1.8
    scaled = base * s / s.max()
    return np.maximum(scaled, min_size) 


bis_norm = minmax(bis_sum)
un_norm  = minmax(un_sum)

bis_bub  = bubble(bis_cnt)
un_bub   = bubble(un_cnt)

def plot(layer, norm, bub, color, out_png):
    plt.figure(figsize=(20,12))
    plt.scatter(labels, norm, s=bub, c=color, alpha=.7)
    plt.title(f"{layer} Layer – Normalized DebtRank (All Periods, Last Row)",
              fontsize=40, pad=20)
    plt.xticks(range(len(labels)), labels, rotation=45, fontsize=35)
    plt.ylabel("Normalized Risk Score", fontsize=35)
    plt.xlabel("Countries", fontsize=35)
    plt.grid(alpha=.4)
    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.show()

plot("BIS", bis_norm, bis_bub, 'blue',   "bubble_BIS_all_periods.png")
plot("UN",  un_norm,  un_bub,  'orange', "bubble_UN_all_periods.png")

print("✅ 그래프 저장 완료: bubble_BIS_all_periods.png / bubble_UN_all_periods.png")









import numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path

bis_path = Path("./output/multilayer_results_BIS.xlsx")
un_path  = Path("./output/multilayer_results_UN.xlsx")
ISO2_TO_3 = {"AU":"AUS","AT":"AUT","BE":"BEL","BR":"BRA","CA":"CAN","CH":"CHE","CL":"CHL",
             "DE":"DEU","DK":"DNK","ES":"ESP","FI":"FIN","FR":"FRA","GB":"GBR","HK":"HKG",
             "IE":"IRL","IT":"ITA","JP":"JPN","NL":"NLD","SE":"SWE","US":"USA"}

order = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
         "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]

man_bis = np.array([250.6981,241.2684,158.2254,136.7064,131.7540,96.7809,96.1975,
                     85.4969,80.6707,77.6661,72.7587,69.0715,64.0819,52.3795,40.7269,
                     37.7269,33.7189,22.7910,22.1630,21.2920])
man_un  = np.array([9.2134,9.1952,7.8842,7.7336,7.1842,6.2963,5.3678,5.2920,
                     4.4875,4.2451,3.6266,3.3629,3.3041,2.5927,2.4395,2.0595,
                     1.3704,1.3555,1.2396,0.6009])

cnt_bis = np.array([31,32,3,3,4,3,2,1,6,3,2,1,0,1,2,1,1,0,0,0])
cnt_un  = np.array([0,32,0,1,29,0,0,0,10,3,7,0,0,0,13,0,0,0,0,1])

def iso3(c): c=str(c).strip(); return ISO2_TO_3.get(c,c)
def agg(path):
    xl = pd.ExcelFile(path)
    codes = [iso3(c) for c in xl.parse(xl.sheet_names[0]).columns[1:]]
    pos = {c:i for i,c in enumerate(codes)}
    idx = [pos[c] for c in order]
    s = np.zeros(len(codes)); cnt = np.zeros(len(codes),int)
    for sh in xl.sheet_names:
        last = xl.parse(sh).iloc[-1,1:].astype(float).values
        s += last;   cnt += (last>=1.0)
    return s[idx], cnt[idx]

exa_bis, cnt_exa_bis = agg(bis_path)
exa_un , cnt_exa_un  = agg(un_path)

def bubble(c, base=4000, min_size=80):
    if c.max()==0: return np.full_like(c, min_size)
    s = np.log1p(c.astype(float)); return np.maximum(base*s/s.max(), min_size)

b_bis_ex = bubble(cnt_exa_bis); b_un_ex = bubble(cnt_exa_un)
b_bis_m  = bubble(cnt_bis)    ; b_un_m = bubble(cnt_un)

x = np.arange(len(order))

def triple(layer_left, left_vals, left_bub, left_col,
           man_bis_vals, man_bis_bub,
           man_un_vals,  man_un_bub,
           outfile):
    fig, axL = plt.subplots(figsize=(20,12))
    axL.scatter(x, left_vals, s=left_bub, c=left_col, alpha=.85, label=f"Excel {layer_left}")
    axL.set_ylabel(f"Excel {layer_left} Risk (합계)", fontsize=26, color=left_col)
    axL.tick_params(axis='y', labelcolor=left_col)
    axL.grid(alpha=.25)

    axR1 = axL.twinx()
    axR1.scatter(x, man_bis_vals, s=man_bis_bub, c='red', alpha=.55, label="Manual BIS")
    axR1.set_ylabel("Manual Risk", fontsize=26, color='black')
    axR1.tick_params(axis='y', labelcolor='black')

    axR2 = axL.twinx()
    axR2.spines['right'].set_position(("outward", 60))  
    axR2.scatter(x, man_un_vals, s=man_un_bub, c='green', alpha=.55, label="Manual UN")
    axR2.tick_params(axis='y', labelcolor='black')
    axR2.set_ylabel("Manual UN", fontsize=26, color='green')

    axL.set_xticks(x); axL.set_xticklabels(order, rotation=45, fontsize=24)
    axL.set_xlabel("Countries", fontsize=28)

    handles, labels = [], []
    for ax in (axL, axR1, axR2):
        h,l = ax.get_legend_handles_labels()
        handles += h; labels += l
    axL.legend(handles, labels, loc='upper right', fontsize=18, markerscale=.6)

    plt.title(f"{layer_left} 기준 – Excel(왼쪽) vs Manual(BIS / UN)", fontsize=32, pad=18)
    plt.tight_layout(); plt.savefig(outfile, dpi=300, bbox_inches='tight'); plt.show()

triple("BIS", exa_bis, b_bis_ex, 'blue',
       man_bis, b_bis_m,
       man_un,  b_un_m,
       "triple_BIS_left.png")

triple("UN", exa_un, b_un_ex, 'orange',
       man_bis, b_bis_m,
       man_un,  b_un_m,
       "triple_UN_left.png")

print("✅ 저장 완료 → triple_BIS_left.png / triple_UN_left.png")
























import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

bis_path = Path("./output/multilayer_results_BIS.xlsx")
un_path  = Path("./output/multilayer_results_UN.xlsx")
ISO2_TO_3 = {"AU":"AUS","AT":"AUT","BE":"BEL","BR":"BRA","CA":"CAN","CH":"CHE","CL":"CHL",
             "DE":"DEU","DK":"DNK","ES":"ESP","FI":"FIN","FR":"FRA","GB":"GBR","HK":"HKG",
             "IE":"IRL","IT":"ITA","JP":"JPN","NL":"NLD","SE":"SWE","US":"USA"}

order = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
         "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]

man_bis = np.array([250.6981,241.2684,158.2254,136.7064,131.7540,96.7809,96.1975,
                    85.4969,80.6707,77.6661,72.7587,69.0715,64.0819,52.3795,40.7269,
                    37.7269,33.7189,22.7910,22.1630,21.2920])
man_un  = np.array([9.2134,9.1952,7.8842,7.7336,7.1842,6.2963,5.3678,5.2920,
                    4.4875,4.2451,3.6266,3.3629,3.3041,2.5927,2.4395,2.0595,
                    1.3704,1.3555,1.2396,0.6009])

cnt_bis = np.array([31,32,3,3,4,3,2,1,6,3,2,1,0,1,2,1,1,0,0,0])
cnt_un  = np.array([0,32,0,1,29,0,0,0,10,3,7,0,0,0,13,0,0,0,0,1])

def iso3(c): c=str(c).strip(); return ISO2_TO_3.get(c,c)

def agg_last(path):
    xl = pd.ExcelFile(path)
    codes = [iso3(c) for c in xl.parse(xl.sheet_names[0]).columns[1:]]
    pos   = {c:i for i,c in enumerate(codes)}
    idx   = [pos[c] for c in order]  
    s = np.zeros(len(codes)); cnt = np.zeros(len(codes),int)
    for sh in xl.sheet_names:
        last = xl.parse(sh).iloc[-1,1:].astype(float).values
        s += last; cnt += (last>=1.0)
    return s[idx], cnt[idx]

exa_bis, cnt_exa_bis = agg_last(bis_path)
exa_un , cnt_exa_un  = agg_last(un_path)

def bubble(counts, base=4000, min_size=80, emph=(29,32)):
    if counts.max()==0: return np.full_like(counts,min_size)
    scaled = np.log1p(counts.astype(float))
    scaled[(counts>=emph[0])&(counts<=emph[1])]*=1.8
    return np.maximum(base*scaled/scaled.max(), min_size)
bub_manual_bis = bubble(cnt_bis)
bub_manual_un  = bubble(cnt_un)
bub_excel_bis  = bubble(cnt_exa_bis)
bub_excel_un   = bubble(cnt_exa_un)


def norm(arr): arr=np.asarray(arr,float); return (arr-arr.min())/(arr.max()-arr.min()+1e-12)

def plot_single(title, arr_blue, bub_blue, arr_yellow, bub_yellow,
                arr_green, bub_green, outfile):
    plt.figure(figsize=(20,12))
    x = np.arange(len(order))

    plt.scatter(x, norm(arr_blue),   s=bub_blue,   c='blue',   alpha=.8, label="BIS")
    plt.scatter(x, norm(arr_yellow), s=bub_yellow, c='orange', alpha=.8, label="UN")
    plt.scatter(x, norm(arr_green),  s=bub_green,  c='green',  alpha=.8, label="New Multilayer Data")

    plt.xticks(x, order, rotation=45, fontsize=26)
    plt.ylabel("Normalized Risk Score", fontsize=30)
    plt.xlabel("Countries", fontsize=30)
    plt.title(title, fontsize=34, pad=18)
    plt.grid(alpha=.25)
    plt.legend(fontsize=20, markerscale=.6, loc='upper right')
    plt.tight_layout()
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    plt.show()

plot_single("BIS vs UN vs Multilayer(BIS)",
            man_bis, bub_manual_bis,
            man_un,  bub_manual_un,
            exa_bis, bub_excel_bis,
            "overlay_manual_vs_excel_BIS.png")

plot_single("BIS vs UN vs Multilayer(UN)",
            man_bis, bub_manual_bis,
            man_un,  bub_manual_un,
            exa_un,  bub_excel_un,
            "overlay_manual_vs_excel_UN.png")

print("✅ 저장 완료 → overlay_manual_vs_excel_BIS.png / overlay_manual_vs_excel_UN.png")



def plot_bis_un_comparison(norm_bis, norm_un, bub_bis, bub_un, labels, outfile):
    x = np.arange(len(labels))
    plt.figure(figsize=(20, 12))

    plt.scatter(x, norm_bis, s=bub_bis, c='blue', alpha=0.8, label="Excel BIS")
    plt.scatter(x, norm_un,  s=bub_un,  c='orange', alpha=0.8, label="Excel UN")

    plt.xticks(x, labels, rotation=45, fontsize=26)
    plt.ylabel("Normalized Risk Score", fontsize=30)
    plt.xlabel("Countries", fontsize=30)
    plt.title("BIS vs UN(previous research)", fontsize=34, pad=18)
    plt.grid(alpha=0.25)
    plt.legend(fontsize=20, markerscale=0.6, loc='upper right')
    plt.tight_layout()
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    plt.show()
plot_bis_un_comparison(bis_norm, un_norm, bis_bub, un_bub, labels,
                       "comparison_excel_BIS_vs_UN.png")

print("✅ 저장 완료 → comparison_excel_BIS_vs_UN.png")




import pandas as pd

df = pd.DataFrame({
    "Country"        : labels,
    "BIS_sum_raw"    : bis_sum,
    "UN_sum_raw"     : un_sum,
    "BIS_norm_0_1"   : bis_norm,
    "UN_norm_0_1"    : un_norm,
    "BIS_count_ge1"  : bis_cnt.astype(int),
    "UN_count_ge1"   : un_cnt.astype(int),
    "BIS_bubble"     : bis_bub,
    "UN_bubble"      : un_bub
})

pd.set_option("display.float_format", lambda x: f"{x:.6f}")
print("\n=== Values used in 'BIS vs UN (previous research)' plot ===")
print(df.to_string(index=False))








import numpy as np
import pandas as pd

multi_bis_raw    = exa_bis
multi_bis_count  = cnt_exa_bis
multi_bis_bubble = bub_excel_bis

multi_bis_norm = (multi_bis_raw - multi_bis_raw.min()) / (multi_bis_raw.max() - multi_bis_raw.min() + 1e-12)

pd.set_option("display.float_format", lambda x: f"{x:.6f}")
df_multi_bis = pd.DataFrame({
    "Country": order,                     
    "Multi_BIS_sum_raw": multi_bis_raw,  
    "Multi_BIS_norm_0_1": multi_bis_norm, 
    "Multi_BIS_count_ge1": multi_bis_count.astype(int),
    "Multi_BIS_bubble": multi_bis_bubble  
})
print("\n=== Multilayer (BIS) values used in the plot ===")
print(df_multi_bis.to_string(index=False))
