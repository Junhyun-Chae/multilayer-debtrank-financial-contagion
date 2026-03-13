import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

excel_path = Path("./output/multilayer_results_BIS.xlsx")
out_dir = Path("./output/final_risk_timeseries_BIS")
out_dir.mkdir(parents=True, exist_ok=True)

xl = pd.ExcelFile(excel_path)

data = {}
for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    last_row = df.iloc[-1, 1:]  
    data[sheet] = last_row.values

countries = df.columns[1:].tolist() 
summary_df = pd.DataFrame(data, index=countries).T  
summary_df.index.name = "Period"

plt.figure(figsize=(16, 8))

for country in countries:
    plt.plot(summary_df.index, summary_df[country], marker="o", label=country)

plt.xticks(rotation=45, ha="right")
plt.ylabel("Final Risk (last step)", fontsize=13)
plt.xlabel("Period (Quarter)", fontsize=13)
plt.title("BIS Layer – Final Risk Time Series by Country", fontsize=15)
plt.grid(alpha=0.3)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=9)
plt.tight_layout()

out_png = out_dir / "BIS_final_risk_timeseries.png"
plt.savefig(out_png, dpi=300, bbox_inches="tight")
plt.show()

print(f"✅ 시계열 그래프 저장 완료: {out_png}")

summary_csv = out_dir / "BIS_final_risk_summary.csv"
summary_df.to_csv(summary_csv)
print(f"📄 요약 CSV 저장 완료: {summary_csv}")












import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import MaxNLocator

excel_path = Path("./output/multilayer_results_BIS.xlsx")
out_dir = Path("./output/BIS_clean_plots")
out_dir.mkdir(parents=True, exist_ok=True)
xl = pd.ExcelFile(excel_path)
data = {}
countries = None

for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    if countries is None:
        countries = df.columns[1:].tolist()
    last_row = df.iloc[-1, 1:] 
    data[sheet] = last_row.values

summary_df = pd.DataFrame(data, index=countries).T 
summary_df.index.name = "Period"

try:
    idx = []
    for s in summary_df.index:
        y, q = s.split("-Q")
        month = (int(q) - 1) * 3 + 1
        idx.append(pd.Timestamp(int(y), month, 1))
    summary_df.index = pd.to_datetime(idx)
    summary_df = summary_df.sort_index()
    x_labels = [f"{d.year}-Q{((d.month-1)//3)+1}" for d in summary_df.index]
except Exception:
    x_labels = summary_df.index.tolist()


topk = (summary_df.mean(axis=0)
        .sort_values(ascending=False)
        .head(k)).index.tolist()

plt.figure(figsize=(16, 8))
for c in summary_df.columns:
    plt.plot(summary_df.index, summary_df[c], color="lightgray", linewidth=1, alpha=0.7)

colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
for i, c in enumerate(topk):
    plt.plot(summary_df.index, summary_df[c], linewidth=2.5, label=c, color=colors[i % len(colors)], marker="o")

plt.title(f"Multilayer Risk Score\n(Top {k} highlighted)", fontsize=16)
plt.ylabel("Final Risk (last step)")
plt.xlabel("Period (Quarter)")
ax = plt.gca()
ax.xaxis.set_major_locator(MaxNLocator(nbins=18)) 
ax.set_xticklabels([x_labels[i] for i, _ in enumerate(summary_df.index)], rotation=45, ha="right")
plt.grid(alpha=0.25)
plt.legend(title="Top countries", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
p1 = out_dir / "bis_timeseries_highlight.png"
plt.savefig(p1, dpi=300, bbox_inches="tight")
plt.show()
print(f"✅ 저장: {p1}")

n = len(summary_df.columns)
cols = 5
rows = int(np.ceil(n / cols))
fig, axes = plt.subplots(rows, cols, figsize=(20, rows*2.8), sharex=True, sharey=True)
axes = axes.ravel()

for i, c in enumerate(summary_df.columns):
    ax = axes[i]
    ax.plot(summary_df.index, summary_df[c], color="tab:blue", linewidth=1.7, marker="o", markersize=2.5)
    ax.set_title(c, fontsize=10)
    ax.grid(alpha=0.2)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=4))

for j in range(i+1, rows*cols):
    fig.delaxes(axes[j])

for ax in fig.get_axes():
    ticks = ax.get_xticks()
    labels = []
    for t in ticks:
        idx = int(np.clip(round(t), 0, len(x_labels)-1))
        labels.append(x_labels[idx] if 0 <= idx < len(x_labels) else "")
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)

fig.suptitle("Multilayer Risk Score\nSmall Multiples by Country", fontsize=16, y=1.02)
fig.tight_layout()
p2 = out_dir / "bis_timeseries_small_multiples.png"
fig.savefig(p2, dpi=300, bbox_inches="tight")
plt.show()
print(f"✅ 저장: {p2}")

import matplotlib.ticker as ticker

plt.figure(figsize=(16, 8))
norm_df = (summary_df - summary_df.min()) / (summary_df.max() - summary_df.min())

plt.imshow(norm_df.values, aspect="auto", cmap="viridis", interpolation="nearest")
plt.colorbar(label="Normalized Final Risk")


ax = plt.gca()
step = 4 
yticks = np.arange(0, len(x_labels), step)
ax.set_yticks(yticks)
ax.set_yticklabels([x_labels[i] for i in yticks], fontsize=9)

plt.xticks(ticks=np.arange(len(summary_df.columns)),
           labels=summary_df.columns, rotation=45, ha="right")

plt.title("Multilayer Risk Score Heatmap", fontsize=16)
plt.tight_layout()
p3 = out_dir / "bis_final_risk_heatmap.png"
plt.savefig(p3, dpi=300, bbox_inches="tight")
plt.show()
print(f"✅ 저장: {p3}")



import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "Times New Roman"


plt.figure(figsize=(14, 7))  
norm_df = (summary_df - summary_df.min()) / (summary_df.max() - summary_df.min())

im = plt.imshow(norm_df.values, aspect="auto", cmap="viridis", interpolation="nearest")

cbar = plt.colorbar(im)
cbar.set_label("Normalized Final Risk", fontsize=20) 
cbar.ax.tick_params(labelsize=16)                   

ax = plt.gca()

step = 4
yticks = np.arange(0, len(x_labels), step)
ax.set_yticks(yticks)
ax.set_yticklabels([x_labels[i] for i in yticks], fontsize=16) 


plt.xticks(
    ticks=np.arange(len(summary_df.columns)),
    labels=summary_df.columns,
    rotation=45, ha="right", fontsize=16  
)


plt.title("Multilayer Risk Score Heatmap", fontsize=24, pad=25)

plt.tight_layout()
plt.savefig("./output/BIS_clean_plots/bis_final_risk_heatmap_bigfont.png",
            dpi=300, bbox_inches="tight")
plt.show()

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "Times New Roman"

plt.figure(figsize=(14, 7))
norm_df = (summary_df - summary_df.min()) / (summary_df.max() - summary_df.min())

im = plt.imshow(norm_df.values, aspect="auto", cmap="viridis", interpolation="nearest")

cbar = plt.colorbar(im)
cbar.set_label("Normalized Final Risk", fontsize=20)
cbar.ax.tick_params(labelsize=16)

ax = plt.gca()

step = 8
yticks = np.arange(0, len(x_labels), step)
ax.set_yticks(yticks)
ax.set_yticklabels([x_labels[i] for i in yticks], fontsize=16)

plt.xticks(
    ticks=np.arange(len(summary_df.columns)),
    labels=summary_df.columns,
    rotation=45, ha="right", fontsize=16
)

plt.title("Multilayer Risk Score Heatmap", fontsize=24, pad=25)

plt.tight_layout()
plt.savefig("./output/BIS_clean_plots/bis_final_risk_heatmap_bigfont.png",
            dpi=300, bbox_inches="tight")
plt.show()


import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "Times New Roman"
plt.figure(figsize=(14, 7))
norm_df = (summary_df - summary_df.min()) / (summary_df.max() - summary_df.min())

im = plt.imshow(norm_df.values, aspect="auto", cmap="viridis", interpolation="nearest")

cbar = plt.colorbar(im)
cbar.set_label("Normalized Final Risk", fontsize=24) 
cbar.ax.tick_params(labelsize=20)                    

ax = plt.gca()
step = 8
yticks = np.arange(0, len(x_labels), step)
ax.set_yticks(yticks)
ax.set_yticklabels([x_labels[i] for i in yticks], fontsize=20)  
plt.xticks(
    ticks=np.arange(len(summary_df.columns)),
    labels=summary_df.columns,
    rotation=45, ha="right", fontsize=20 
)


ax.tick_params(axis="both", which="major", labelsize=18)

plt.tight_layout()
plt.savefig("./output/BIS_clean_plots/bis_final_risk_heatmap_bigfont2.png",
            dpi=300, bbox_inches="tight")
plt.show()
