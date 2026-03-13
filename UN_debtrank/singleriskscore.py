import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path



plt.rcParams["font.family"] = "Times New Roman"

excel_path = Path("UN_debtrank/UN_debtrank_e_final.xlsx")

out_dir = Path("UN_debtrank/output_plots")
out_dir.mkdir(parents=True, exist_ok=True)

country_2letter = {
    'AUT': 'AT',  # Austria
    'AUS': 'AU',  # Australia
    'BEL': 'BE',  # Belgium
    'BRA': 'BR',  # Brazil
    'CAN': 'CA',  # Canada
    'CHE': 'CH',  # Switzerland
    'CHL': 'CL',  # Chile
    'DEU': 'DE',  # Germany
    'DNK': 'DK',  # Denmark
    'ESP': 'ES',  # Spain
    'FIN': 'FI',  # Finland
    'FRA': 'FR',  # France
    'GBR': 'GB',  # United Kingdom
    'HKG': 'HK',  # Hong Kong
    'IRL': 'IE',  # Ireland
    'ITA': 'IT',  # Italy
    'NLD': 'NL',  # Netherlands
    'SWE': 'SE',  # Sweden
    'USA': 'US',  # United States
    'JPN': 'JP',  # Japan
}



xl = pd.ExcelFile(excel_path)
data = {}
countries_iso3 = None

for sheet in xl.sheet_names:
    period_label = sheet.replace("Period_", "") 
    df = xl.parse(sheet)

    if countries_iso3 is None:
        countries_iso3 = df.columns[1:].tolist()


    last_row = df.iloc[-1, 1:] 

    data[period_label] = last_row.values


summary_df = pd.DataFrame(data, index=countries_iso3).T  
summary_df.index.name = "Period"


summary_df.index = pd.to_datetime(summary_df.index, format="%Y-%m")
summary_df = summary_df.sort_index()

quarter_labels = [f"{d.year}-Q{((d.month - 1) // 3) + 1}" for d in summary_df.index]



iso2_columns = []
for c in summary_df.columns:
    if c in country_2letter:
        iso2_columns.append(country_2letter[c])
    else:
        iso2_columns.append(c)

summary_df.columns = iso2_columns

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
    fontsize=23
)

ax.tick_params(axis="both", which="major", labelsize=30)

plt.tight_layout()

out_png = out_dir / "UN_singlelayer_risk_heatmap_iso2_formatted.png"
plt.savefig(out_png, dpi=300, bbox_inches="tight")
plt.show()

print(f"✅ UN 히트맵 저장 완료: {out_png}")













################################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path



plt.rcParams["font.family"] = "Times New Roman"

excel_path = Path("UN_debtrank/UN_debtrank_e_final.xlsx")

out_dir = Path("UN_debtrank/output_plots")
out_dir.mkdir(parents=True, exist_ok=True)

country_2letter = {
    'AUT': 'AT',  # Austria
    'AUS': 'AU',  # Australia
    'BEL': 'BE',  # Belgium
    'BRA': 'BR',  # Brazil
    'CAN': 'CA',  # Canada
    'CHE': 'CH',  # Switzerland
    'CHL': 'CL',  # Chile
    'DEU': 'DE',  # Germany
    'DNK': 'DK',  # Denmark
    'ESP': 'ES',  # Spain
    'FIN': 'FI',  # Finland
    'FRA': 'FR',  # France
    'GBR': 'GB',  # United Kingdom
    'HKG': 'HK',  # Hong Kong
    'IRL': 'IE',  # Ireland
    'ITA': 'IT',  # Italy
    'NLD': 'NL',  # Netherlands
    'SWE': 'SE',  # Sweden
    'USA': 'US',  # United States
    'JPN': 'JP',  # Japan
}



xl = pd.ExcelFile(excel_path)
data = {}
countries_iso3 = None

for sheet in xl.sheet_names:
    period_label = sheet.replace("Period_", "")  

    df = xl.parse(sheet)

    if countries_iso3 is None:
        countries_iso3 = df.columns[1:].tolist()
    last_row = df.iloc[-1, 1:]  

    data[period_label] = last_row.values


summary_df = pd.DataFrame(data, index=countries_iso3).T 
summary_df.index.name = "Period"
summary_df.index = pd.to_datetime(summary_df.index, format="%Y-%m")
summary_df = summary_df.sort_index()

quarter_labels = [f"{d.year}-Q{((d.month - 1) // 3) + 1}" for d in summary_df.index]

iso2_columns = []
for c in summary_df.columns:
    if c in country_2letter:
        iso2_columns.append(country_2letter[c])
    else:
        iso2_columns.append(c)

summary_df.columns = iso2_columns

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

out_png = out_dir / "UN_singlelayer_risk_heatmap_iso2_formatted.png"
plt.savefig(out_png, dpi=300, bbox_inches="tight")
plt.show()

print(f"✅ UN 히트맵 저장 완료: {out_png}")