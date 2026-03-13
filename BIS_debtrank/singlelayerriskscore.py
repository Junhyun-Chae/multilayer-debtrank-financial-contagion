import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams["font.family"] = "Times New Roman"
excel_path = Path("BIS_debtrank/BIS_debtrank_fx_c_final.xlsx")
out_dir = Path("BIS_debtrank/output_plots")
out_dir.mkdir(parents=True, exist_ok=True)

countries = ['AT', 'AU', 'BE', 'BR', 'CA', 'CH', 'CL', 'DE', 'DK', 'ES',
             'FI', 'FR', 'GB', 'HK', 'IE', 'IT', 'NL', 'SE', 'US', 'JP']

xl = pd.ExcelFile(excel_path)
data = {}
countries_from_file = None

for sheet in xl.sheet_names:
    if not sheet.startswith("Period_"):
        continue

    period_label = sheet.replace("Period_", "") 

    df = xl.parse(sheet)
    if countries_from_file is None:
        countries_from_file = df.columns[1:].tolist()
    common_cols = [c for c in countries if c in df.columns[1:]]
    df = df[['Step'] + common_cols]
    last_row = df.iloc[-1, 1:] 
    data[period_label] = last_row.values


summary_df = pd.DataFrame(data, index=countries, columns=list(data.keys())).T 
summary_df.index.name = "Period"
summary_df.index = pd.PeriodIndex(summary_df.index, freq="Q")
summary_df = summary_df.sort_index()
quarter_labels = [f"{p.year}-Q{p.quarter}" for p in summary_df.index]
norm_df = (summary_df - summary_df.min()) / (summary_df.max() - summary_df.min())

plt.figure(figsize=(14, 7))

im = plt.imshow(
    norm_df.values,
    aspect="auto",
    cmap="viridis",
    interpolation="nearest"
)

cbar = plt.colorbar(im)
cbar.set_label(r"Normalized Systemic Risk $\bar{h}_i(t)$", fontsize=30) 
cbar.ax.tick_params(labelsize=25)                      
ax = plt.gca()
step = 8
yticks = np.arange(0, len(quarter_labels), step)
ax.set_yticks(yticks)
ax.set_yticklabels([quarter_labels[i] for i in yticks], fontsize=25) 


plt.xticks(
    ticks=np.arange(len(norm_df.columns)),
    labels=norm_df.columns,
    rotation=45,
    ha="right",
    rotation_mode="anchor",  
    fontsize=23
)
ax.tick_params(axis="both", which="major", labelsize=30)

plt.tight_layout()

out_png = out_dir / "BIS_singlelayer_risk_heatmap_fx_c_iso2_formatted.png"
plt.savefig(out_png, dpi=300, bbox_inches="tight")
plt.show()

print(f"BIS 히트맵 저장 완료: {out_png}")