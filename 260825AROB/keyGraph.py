import matplotlib.pyplot as plt
import pandas as pd

data = [
    ("Australia", 2.57),
    ("Austria", 0.90),
    ("Belgium", 1.62),
    ("Canada", 3.49),
    ("Finland", 1.24),
    ("France", 6.59),
    ("Germany", 3.65),
    ("Greece", 0.73),
    ("Ireland", 2.29),
    ("Italy", 24.57),
    ("Japan", 15.02),
    ("Netherlands", 5.64),
    ("Portugal", 0.49),
    ("Spain", 4.19),
    ("Sweden", 0.77),
    ("Switzerland", 1.78),
    ("United Kingdom", 45.03),
    ("United States", 96.23),
]

df = pd.DataFrame(data, columns=["Country", "FailedCapitalPct"])

df_sorted = df.sort_values("FailedCapitalPct", ascending=False)

plt.figure(figsize=(12, 6))
plt.scatter(df_sorted["Country"], df_sorted["FailedCapitalPct"], color="darkred", s=100)
plt.xticks(rotation=60, ha="right")
plt.ylabel("Failed Capital (% of Total)")
plt.title("Failed Capital by Country — Simulation 1 (Credit Channel) [Scatter Plot]")

for i, val in enumerate(df_sorted["FailedCapitalPct"]):
    plt.text(i, val + 1, f"{val:.1f}", ha="center", fontsize=8)

plt.tight_layout()
plt.show()















import matplotlib.pyplot as plt

countries = ["AT","AU","BE","BR","CA","CH","CL","DE","DK","ES",
             "FI","FR","GB","HK","IE","IT","NL","SE","US","JP"]

values = [0.041324,0.052019,0.030118,0.027851,0.070547,
          0.279063,0.000467,0.125476,0.090995,0.361115,
          0.027988,0.165386,1.000000,0.057331,0.029742,
          0.205336,0.495789,0.062068,1.000000,0.591547]

plt.figure(figsize=(14,7))
plt.scatter(countries, values, s=120, c="blue", alpha=0.7)

plt.xticks(rotation=45)
plt.ylabel("Final Risk Value (Last Row)", fontsize=14)
plt.title("Scatter Plot of Final Risk Values", fontsize=16)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()



















import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text


df1 = pd.DataFrame([
    ("AU", 2.57), ("AT", 0.90), ("BE", 1.62), ("CA", 3.49), ("FI", 1.24),
    ("FR", 6.59), ("DE", 3.65), ("IE", 2.29), ("IT", 24.57), ("JP", 15.02),
    ("NL", 5.64), ("ES", 4.19), ("SE", 0.77), ("CH", 1.78), ("GB", 45.03), ("US", 96.23),
], columns=["ISO2","FailedCapitalPct"])

df2 = pd.DataFrame({
    "ISO2": ["AT","AU","BE","BR","CA","CH","CL","DE","DK","ES","FI","FR","GB","HK","IE","IT","NL","SE","US","JP"],
    "RiskValue": [0.041324,0.052019,0.030118,0.027851,0.070547,0.279063,0.000467,0.125476,0.090995,0.361115,
                  0.027988,0.165386,1.000000,0.057331,0.029742,0.205336,0.495789,0.062068,1.000000,0.591547]
})

df = pd.merge(df1, df2, on="ISO2", how="inner")

plt.rcParams["font.family"] = "Times New Roman"

fig, ax = plt.subplots(figsize=(10, 7))

ax.scatter(df["RiskValue"], df["FailedCapitalPct"], s=150, c="tab:blue", alpha=0.8)

x_vals = df["RiskValue"]
y_vals = df["FailedCapitalPct"]
texts = []
for iso, x, y in zip(df["ISO2"], x_vals, y_vals):
    texts.append(ax.text(x, y, iso, ha='center', va='bottom', fontsize=14))

adjust_text(texts,
            x=x_vals,
            y=y_vals,
            force_points=(1.5, 1.5),
            force_text=(1.5, 1.5),
            expand_points=(1.2, 1.2),
            arrowprops=dict(arrowstyle="-", color='gray', lw=0.5))
ax.set_xlabel("Multilayer Risk Value", fontsize=20)
ax.set_ylabel("Failed Capital (% of Total)", fontsize=20)
ax.tick_params(axis="both", which="major", labelsize=14)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()






















import matplotlib.pyplot as plt
import pandas as pd

df1 = pd.DataFrame([
    ("AU", 2.57), ("AT", 0.90), ("BE", 1.62), ("CA", 3.49), ("FI", 1.24),
    ("FR", 6.59), ("DE", 3.65), ("IE", 2.29), ("IT", 24.57), ("JP", 15.02),
    ("NL", 5.64), ("ES", 4.19), ("SE", 0.77), ("CH", 1.78), ("GB", 45.03), ("US", 96.23),
], columns=["ISO2","FailedCapitalPct"])

df2 = pd.DataFrame({
    "ISO2": ["AT","AU","BE","BR","CA","CH","CL","DE","DK","ES","FI","FR","GB","HK","IE","IT","NL","SE","US","JP"],
    "RiskValue": [0.041324,0.052019,0.030118,0.027851,0.070547,0.279063,0.000467,0.125476,0.090995,0.361115,
                  0.027988,0.165386,1.000000,0.057331,0.029742,0.205336,0.495789,0.062068,1.000000,0.591547]
})

df = pd.merge(df1, df2, on="ISO2", how="inner")

plt.rcParams["font.family"] = "Times New Roman"

fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(df["RiskValue"], df["FailedCapitalPct"], s=150, c="tab:blue", alpha=0.8)

offsets = [(0,10), (10,0), (-10,0), (0,-10)]  
for i, (iso, x, y) in enumerate(zip(df["ISO2"], df["RiskValue"], df["FailedCapitalPct"])):
    dx, dy = offsets[i % len(offsets)] 
    ax.annotate(iso, xy=(x, y), xytext=(dx, dy),
                textcoords="offset points", ha="center", fontsize=14,
                arrowprops=dict(arrowstyle="-", lw=0.5, color="gray", alpha=0.6))

ax.set_xlabel("Multilayer Risk Value", fontsize=20)
ax.set_ylabel("Failed Capital (% of Total)", fontsize=20)
ax.set_title("Failed Capital vs Multilayer Risk Value", fontsize=27)
ax.tick_params(axis="both", which="major", labelsize=14)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.show()



import matplotlib.pyplot as plt
import pandas as pd

df1 = pd.DataFrame([
    ("AU", 2.57), ("AT", 0.90), ("BE", 1.62), ("CA", 3.49), ("FI", 1.24),
    ("FR", 6.59), ("DE", 3.65), ("IE", 2.29), ("IT", 24.57), ("JP", 15.02),
    ("NL", 5.64), ("ES", 4.19), ("SE", 0.77), ("CH", 1.78), ("GB", 45.03), ("US", 96.23),
], columns=["ISO2","FailedCapitalPct"])

df2 = pd.DataFrame({
    "ISO2": ["AT","AU","BE","BR","CA","CH","CL","DE","DK","ES","FI","FR","GB","HK","IE","IT","NL","SE","US","JP"],
    "RiskValue": [0.041324,0.052019,0.030118,0.027851,0.070547,0.279063,0.000467,0.125476,0.090995,0.361115,
                  0.027988,0.165386,1.000000,0.057331,0.029742,0.205336,0.495789,0.062068,1.000000,0.591547]
})
df = pd.merge(df1, df2, on="ISO2", how="inner")

plt.rcParams["font.family"] = "Times New Roman"

fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(df["RiskValue"], df["FailedCapitalPct"], s=150, c="tab:blue", alpha=0.8)

for i, (iso, x, y) in enumerate(zip(df["ISO2"], df["RiskValue"], df["FailedCapitalPct"])):
    offset_y = 12 if i % 2 == 0 else -12  
    ax.annotate(iso, xy=(x, y), xytext=(0, offset_y),
                textcoords="offset points", ha="center", fontsize=14,
                arrowprops=dict(arrowstyle="-", lw=0.5, color="gray"))

ax.set_xlabel("Final Risk Value", fontsize=20)
ax.set_ylabel("Failed Capital (% of Total)", fontsize=20)
ax.set_title("Failed Capital vs Final Risk Value", fontsize=27)
ax.tick_params(axis="both", which="major", labelsize=14)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.show()









import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df1 = pd.DataFrame([
    ("AU", 2.57), ("AT", 0.90), ("BE", 1.62), ("CA", 3.49), ("FI", 1.24),
    ("FR", 6.59), ("DE", 3.65), ("IE", 2.29), ("IT", 24.57), ("JP", 15.02),
    ("NL", 5.64), ("ES", 4.19), ("SE", 0.77), ("CH", 1.78), ("GB", 45.03), ("US", 96.23),
], columns=["ISO2","FailedCapitalPct"])

df2 = pd.DataFrame({
    "ISO2": ["AT","AU","BE","BR","CA","CH","CL","DE","DK","ES","FI","FR","GB","HK","IE","IT","NL","SE","US","JP"],
    "RiskValue": [0.041324,0.052019,0.030118,0.027851,0.070547,0.279063,0.000467,0.125476,0.090995,0.361115,
                  0.027988,0.165386,1.000000,0.057331,0.029742,0.205336,0.495789,0.062068,1.000000,0.591547]
})
df = pd.merge(df1, df2, on="ISO2", how="inner")

plt.rcParams["font.family"] = "Times New Roman"

fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(df["RiskValue"], df["FailedCapitalPct"], s=150, c="tab:blue", alpha=0.85)

ax.set_xlabel("Final Risk Value", fontsize=20)
ax.set_ylabel("Failed Capital (% of Total)", fontsize=20)
ax.set_title("Failed Capital vs Final Risk Value", fontsize=27)
ax.tick_params(axis="both", which="major", labelsize=14)
ax.grid(alpha=0.3)

top_iso = {"US","GB","IT","JP","NL"}
top_df = df[df["ISO2"].isin(top_iso)]
for iso, x, y in zip(top_df["ISO2"], top_df["RiskValue"], top_df["FailedCapitalPct"]):
    ax.annotate(iso, xy=(x, y), xytext=(0, 10), textcoords="offset points",
                ha="center", va="bottom", fontsize=14)

low_df = df[~df["ISO2"].isin(top_iso)].sort_values(["FailedCapitalPct","RiskValue"])
offsets = [(0,14),(0,-14),(-14,10),(14,10),(-14,-10),(14,-10),
           (-18,6),(18,6),(-18,-6),(18,-6)]
for i, (iso, x, y) in enumerate(zip(low_df["ISO2"], low_df["RiskValue"], low_df["FailedCapitalPct"])):
    dx, dy = offsets[i % len(offsets)]
    ax.annotate(
        iso, xy=(x, y), xytext=(dx, dy), textcoords="offset points",
        ha="center", va="center", fontsize=13,
        arrowprops=dict(arrowstyle="-", lw=0.6, color="gray", shrinkA=0, shrinkB=0)
    )

plt.tight_layout()
plt.show()







import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df1 = pd.DataFrame([
    ("AU", 2.57), ("AT", 0.90), ("BE", 1.62), ("CA", 3.49), ("FI", 1.24),
    ("FR", 6.59), ("DE", 3.65), ("IE", 2.29), ("IT", 24.57), ("JP", 15.02),
    ("NL", 5.64), ("ES", 4.19), ("SE", 0.77), ("CH", 1.78), ("GB", 45.03), ("US", 96.23),
], columns=["ISO2","FailedCapitalPct"])

df2 = pd.DataFrame({
    "ISO2": ["AT","AU","BE","BR","CA","CH","CL","DE","DK","ES","FI","FR","GB","HK","IE","IT","NL","SE","US","JP"],
    "RiskValue": [0.041324,0.052019,0.030118,0.027851,0.070547,0.279063,0.000467,0.125476,0.090995,0.361115,
                  0.027988,0.165386,1.000000,0.057331,0.029742,0.205336,0.495789,0.062068,1.000000,0.591547]
})
df = pd.merge(df1, df2, on="ISO2", how="inner")

plt.rcParams["font.family"] = "Times New Roman"

fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(df["RiskValue"], df["FailedCapitalPct"], s=150, c="tab:blue", alpha=0.85)
ax.set_xlabel("Final Risk Value", fontsize=20)
ax.set_ylabel("Failed Capital (% of Total)", fontsize=20)
ax.set_title("Failed Capital vs Final Risk Value", fontsize=27)
ax.tick_params(axis="both", which="major", labelsize=14)
ax.grid(alpha=0.3)

XR = ax.get_xlim(); YR = ax.get_ylim()
dx_unit = (XR[1]-XR[0]) * 0.015  
dy_unit = (YR[1]-YR[0]) * 0.012  
radius_x = (XR[1]-XR[0]) * 0.018 
radius_y = (YR[1]-YR[0]) * 0.025
iters = 400
step = 0.35                     
X = df["RiskValue"].to_numpy()
Y = df["FailedCapitalPct"].to_numpy()
labels = df["ISO2"].to_numpy()

low_mask = Y <= 6.0
angles = np.linspace(0, 2*np.pi, low_mask.sum(), endpoint=False)
pos = np.vstack([X, Y]).T.astype(float)

k = 0
for i in range(len(pos)):
    if low_mask[i]:
        pos[i,0] += dx_unit*0.6*np.cos(angles[k])
        pos[i,1] += dy_unit*0.6*np.sin(angles[k])
        k += 1
    else:
        pos[i,0] += 0.0
        pos[i,1] += dy_unit*0.6

for _ in range(iters):
    moved = False
    for i in range(len(pos)):
        for j in range(i+1, len(pos)):
            dx = pos[i,0] - pos[j,0]
            dy = pos[i,1] - pos[j,1]
            if abs(dx) < radius_x and abs(dy) < radius_y:
                sx = step * np.sign(dx if dx != 0 else (1 if i%2==0 else -1))
                sy = step * np.sign(dy if dy != 0 else (1 if j%2==0 else -1))
                pos[i,0] += sx*dx_unit; pos[j,0] -= sx*dx_unit
                pos[i,1] += sy*dy_unit; pos[j,1] -= sy*dy_unit
                moved = True

    for i in range(len(pos)):
        dx = pos[i,0] - X[i]; dy = pos[i,1] - Y[i]
        if abs(dx) < radius_x*0.6 and abs(dy) < radius_y*0.6:
            pos[i,1] += dy_unit * step
            moved = True
    if not moved:
        break

for i in range(len(pos)):
    ax.annotate(
        labels[i], xy=(X[i], Y[i]), xytext=(pos[i,0], pos[i,1]),
        fontsize=14, ha="center", va="center",
        arrowprops=dict(arrowstyle="-", lw=0.7, color="gray",
                        connectionstyle="arc3,rad=0.1")
    )

plt.tight_layout()
plt.show()































import matplotlib.pyplot as plt

countries = ["AUT","AUS","BEL","BRA","CAN","CHE","CHL","DEU","DNK","ESP",
             "FIN","FRA","GBR","HKG","IRL","ITA","NLD","SWE","USA","JPN"]

values = [0.020696, -0.01132, 0.021817, 0.027672, 0.004225,
          -0.00517, 0.0, 0.018633, 0.008566, 0.02104,
          0.020798, 0.020649, -0.00116, 0.0, 0.021677,
          0.023751, 0.020332, 0.005249, 0.018346, 0.011332]

plt.figure(figsize=(12,6))
plt.scatter(countries, values, color="blue", s=120, alpha=0.7)

for i, val in enumerate(values):
    plt.text(i, val + (0.001 if val >= 0 else -0.002), f"{val:.3f}",
             ha="center", fontsize=8, color="black")

plt.axhline(0, color="gray", linestyle="--", linewidth=0.8) 
plt.xticks(rotation=45)
plt.ylabel("Default Probability")
plt.title("Scatter Plot of Default Probabilities by Country")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()






import matplotlib.pyplot as plt
import numpy as np

countries = [
    "AT","AU","BE","BR","CA","CH","CL","DE","DK","ES",
    "FI","FR","GB","HK","IE","IT","NL","SE","US","JP"
]

values = [
    0.022851, 0.000912, 0.029077, 0.028429, 0.005052,
    0.003555, 0.000804, 0.030397, 0.009544, 0.027039,
    0.021417, 0.031387, 0.885291, 0.000982, 0.022131,
    0.030208, 0.025966, 0.006824, 0.839988, 0.149529
]

x = np.arange(len(countries))

plt.figure(figsize=(16, 7))
sc = plt.scatter(x, values, s=120, alpha=0.8, edgecolor="k")
plt.xticks(x, countries, rotation=45, ha="right", fontsize=12)
plt.ylabel("Risk (final value)", fontsize=13)
plt.title("Final Risk by Country (AT → JP order)", fontsize=15)
plt.grid(alpha=0.3)

for i, v in enumerate(values):
    plt.text(i, v * 1.02 + (1e-4 if v < 0.01 else 0), f"{v:.6f}",
             ha="center", va="bottom", fontsize=9)

plt.tight_layout()
plt.savefig("final_risk_scatter.png", dpi=300, bbox_inches="tight")
plt.show()











import matplotlib.pyplot as plt
import pandas as pd

table1_data = {
    "Australia": 2.57,
    "Austria": 0.90,
    "Belgium": 1.62,
    "Canada": 3.49,
    "Finland": 1.24,
    "France": 6.59,
    "Germany": 3.65,
    "Greece": 0.73,
    "Ireland": 2.29,
    "Italy": 24.57,
    "Japan": 15.02,
    "Netherlands": 5.64,
    "Portugal": 0.49,
    "Spain": 4.19,
    "Sweden": 0.77,
    "Switzerland": 1.78,
    "United Kingdom": 45.03,
    "United States": 96.23,
}

un_values = {
    "AT": 0.022851, "AU": 0.000912, "BE": 0.029077, "BR": 0.028429, "CA": 0.005052,
    "CH": 0.003555, "CL": 0.000804, "DE": 0.030397, "DK": 0.009544, "ES": 0.027039,
    "FI": 0.021417, "FR": 0.031387, "GB": 0.885291, "HK": 0.000982, "IE": 0.022131,
    "IT": 0.030208, "NL": 0.025966, "SE": 0.006824, "US": 0.839988, "JP": 0.149529
}

iso2_to_name = {
    "AT": "Austria", "AU": "Australia", "BE": "Belgium", "BR": "Brazil",
    "CA": "Canada", "CH": "Switzerland", "CL": "Chile", "DE": "Germany",
    "DK": "Denmark", "ES": "Spain", "FI": "Finland", "FR": "France",
    "GB": "United Kingdom", "HK": "Hong Kong", "IE": "Ireland",
    "IT": "Italy", "NL": "Netherlands", "SE": "Sweden",
    "US": "United States", "JP": "Japan"
}

records = []
for iso2, risk_val in un_values.items():
    name = iso2_to_name[iso2]
    if name in table1_data:
        records.append((name, risk_val, table1_data[name]))

df = pd.DataFrame(records, columns=["Country", "UN_Risk", "FailedCapitalPct"])

plt.figure(figsize=(10, 7))
plt.scatter(df["UN_Risk"], df["FailedCapitalPct"], s=120, color="darkblue", alpha=0.7, edgecolor="k")

for _, row in df.iterrows():
    plt.text(row["UN_Risk"]*1.01, row["FailedCapitalPct"]*1.01,
             row["Country"], fontsize=9, alpha=0.8)

plt.xlabel("UN DebtRank Final Risk", fontsize=13)

plt.ylabel("Failed Capital (% of Total)", fontsize=13)
plt.title("Failed Capital vs UN DebtRank Risk", fontsize=15)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()







import matplotlib.pyplot as plt
import numpy as np

countries = [
    "AT","AU","BE","BR","CA","CH","CL","DE","DK","ES",
    "FI","FR","GB","HK","IE","IT","NL","SE","US","JP"
]

values = [
    0.019529, 0.000402, 0.021387, 0.004766, 0.00043,
    0.001452, 0.00023, 0.025004, 0.004682, 0.021914,
    0.019097, 0.024023, 0.517508, 0.000473, 0.000306,
    0.023337, 0.020283, 0.012031, 0.004194, 0.012356
]

x = np.arange(len(countries))

plt.figure(figsize=(16, 7))
sc = plt.scatter(x, values, s=120, alpha=0.8, edgecolor="k", color="darkgreen")
plt.xticks(x, countries, rotation=45, ha="right", fontsize=12)
plt.ylabel("Risk (final value)", fontsize=13)
plt.title("Final Risk by Country (AT → JP order)", fontsize=15)
plt.grid(alpha=0.3)

for i, v in enumerate(values):
    plt.text(i, v * 1.05 + (1e-4 if v < 0.01 else 0), f"{v:.6f}",
             ha="center", va="bottom", fontsize=9)

plt.tight_layout()
plt.savefig("final_risk_scatter_v2.png", dpi=300, bbox_inches="tight")
plt.show()
















import numpy as np
import matplotlib.pyplot as plt

countries = ["AT","AU","BE","BR","CA","CH","CL","DE","DK","ES",
             "FI","FR","GB","HK","IE","IT","NL","SE","US","JP"]

vals_2009Q2 = [
    0.794038, 0.352396, 0.078577, 0.472990, 0.035432,
    0.858892, 0.481226, 0.988440, 0.030631, 0.867883,
    0.040789, 0.375728, 0.953423, 0.006477, 0.943267,
    0.892239, 0.720245, 0.015508, 0.849759, 0.927505
]

vals_2011Q3 = [
    0.034387, 0.013071, 0.985417, 0.863770, 0.894912,
    0.816177, 0.006971, 0.977254, 0.863387, 0.985152,
    0.021268, 0.982632, 0.936597, 0.818224, 0.999182,
    0.067579, 0.020458, 1.000000, 0.648148, 0.648148
]

vals_2023Q1 = [
    0.900297, 0.009475, 0.890009, 0.756437, 0.878834,
    0.875302, 0.004178, 0.950182, 0.577260, 0.856151,
    0.758002, 0.956296, 0.937846, 0.465278, 0.443852,
    0.849200, 0.892394, 0.777636, 1.000000, 0.749894
]

series = [
    ("2009-Q2", np.array(vals_2009Q2, dtype=float)),
    ("2011-Q3", np.array(vals_2011Q3, dtype=float)),
    ("2023-Q1", np.array(vals_2023Q1, dtype=float)),
]


fig, axes = plt.subplots(3, 1, figsize=(16, 14), sharex=True)

for ax, (title, vals) in zip(axes, series):
    x = np.arange(len(countries))
    mask = ~np.isnan(vals)
    ax.scatter(x[mask], vals[mask], s=140, c="tab:blue", alpha=0.8, edgecolor="k")
    for i in np.where(mask)[0]:
        ax.text(i, vals[i] + 0.015, f"{vals[i]:.3f}", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Risk (final step)")
    ax.set_title(f"Final Risk by Country — {title}")
    ax.grid(alpha=0.3, linestyle="--")
    ax.set_ylim(0, 1.05) 

axes[-1].set_xticks(np.arange(len(countries)))
axes[-1].set_xticklabels(countries, rotation=0, fontsize=11)
plt.tight_layout()
plt.show()











import matplotlib.pyplot as plt
import pandas as pd

data = [
    ("Australia", 2.57),
    ("Austria", 0.90),
    ("Belgium", 1.62),
    ("Canada", 3.49),
    ("Finland", 1.24),
    ("France", 6.59),
    ("Germany", 3.65),
    ("Greece", 0.73),
    ("Ireland", 2.29),
    ("Italy", 24.57),
    ("Japan", 15.02),
    ("Netherlands", 5.64),
    ("Portugal", 0.49),
    ("Spain", 4.19),
    ("Sweden", 0.77),
    ("Switzerland", 1.78),
    ("United Kingdom", 45.03),
    ("United States", 96.23),
]
df = pd.DataFrame(data, columns=["Country", "FailedCapitalPct"])

countries = ["AT","AU","BE","BR","CA","CH","CL","DE","DK","ES",
             "FI","FR","GB","HK","IE","IT","NL","SE","US","JP"]

vals_2009Q2 = [
    0.794038, 0.352396, 0.078577, 0.472990, 0.035432,
    0.858892, 0.481226, 0.988440, 0.030631, 0.867883,
    0.040789, 0.375728, 0.953423, 0.006477, 0.943267,
    0.892239, 0.720245, 0.015508, 0.849759, 0.927505
]


iso2_to_name = {
    "AT":"Austria","AU":"Australia","BE":"Belgium","BR":"Brazil","CA":"Canada",
    "CH":"Switzerland","CL":"Chile","DE":"Germany","DK":"Denmark","ES":"Spain",
    "FI":"Finland","FR":"France","GB":"United Kingdom","HK":"Hong Kong","IE":"Ireland",
    "IT":"Italy","NL":"Netherlands","SE":"Sweden","US":"United States","JP":"Japan"
}
df2 = pd.DataFrame({
    "Country": [iso2_to_name[c] for c in countries],
    "Risk2009Q2": vals_2009Q2
})
df_merge = pd.merge(df, df2, on="Country", how="inner")

plt.figure(figsize=(10,7))
plt.scatter(df_merge["Risk2009Q2"], df_merge["FailedCapitalPct"], s=120, c="blue", alpha=0.7, edgecolor="k")

for i, row in df_merge.iterrows():
    iso = [k for k,v in iso2_to_name.items() if v == row["Country"]][0]
    plt.text(row["Risk2009Q2"]+0.01, row["FailedCapitalPct"]+0.5, iso, fontsize=9)

plt.xlabel("Final Risk Value (2009-Q2)", fontsize=12)

plt.ylabel("Failed Capital (% of Total)", fontsize=12)
plt.yscale("log")

plt.title("Failed Capital vs 2009-Q2 Risk Value (Country-level Comparison)", fontsize=14)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()




import matplotlib.pyplot as plt
import pandas as pd

data = [
    ("Australia", 2.57), ("Austria", 0.90), ("Belgium", 1.62), ("Canada", 3.49),
    ("Finland", 1.24), ("France", 6.59), ("Germany", 3.65), ("Greece", 0.73),
    ("Ireland", 2.29), ("Italy", 24.57), ("Japan", 15.02), ("Netherlands", 5.64),
    ("Portugal", 0.49), ("Spain", 4.19), ("Sweden", 0.77), ("Switzerland", 1.78),
    ("United Kingdom", 45.03), ("United States", 96.23),
]
df = pd.DataFrame(data, columns=["Country", "FailedCapitalPct"])

iso2_to_name = {
    "AT":"Austria","AU":"Australia","BE":"Belgium","BR":"Brazil","CA":"Canada",
    "CH":"Switzerland","CL":"Chile","DE":"Germany","DK":"Denmark","ES":"Spain",
    "FI":"Finland","FR":"France","GB":"United Kingdom","HK":"Hong Kong","IE":"Ireland",
    "IT":"Italy","NL":"Netherlands","SE":"Sweden","US":"United States","JP":"Japan"
}
countries = list(iso2_to_name.keys())

vals_2009Q2 = [
    0.794038, 0.352396, 0.078577, 0.472990, 0.035432,
    0.858892, 0.481226, 0.988440, 0.030631, 0.867883,
    0.040789, 0.375728, 0.953423, 0.006477, 0.943267,
    0.892239, 0.720245, 0.015508, 0.849759, 0.927505
]
valuesbubble = [
    0.041324,0.052019,0.030118,0.027851,0.070547,
    0.279063,0.000467,0.125476,0.090995,0.361115,
    0.027988,0.165386,1.000000,0.057331,0.029742,
    0.205336,0.495789,0.062068,1.000000,0.591547
]

df2 = pd.DataFrame({
    "Country": [iso2_to_name[c] for c in countries],
    "MultilayerScore": valuesbubble,   
    "BubbleSize": vals_2009Q2        
})
df_merge = pd.merge(df, df2, on="Country", how="inner")

plt.rcParams["font.family"] = "Times New Roman"
fig, ax = plt.subplots(figsize=(10, 7))

BUBBLE_COLOR = 'tab:blue'

sc = ax.scatter(
    df_merge["MultilayerScore"], 
    df_merge["FailedCapitalPct"], 
    s=150,  
    c=BUBBLE_COLOR, alpha=0.75, edgecolor="black", linewidth=0.8
)

name_to_iso = {v:k for k,v in iso2_to_name.items()}
for _, row in df_merge.iterrows():
    iso = name_to_iso[row["Country"]]
    ax.annotate(
        iso, xy=(row["MultilayerScore"], row["FailedCapitalPct"]),
        xytext=(0, 10), textcoords="offset points",
        ha="center", fontsize=14
    )

ax.set_xlabel("Multilayer Risk Score", fontsize=20)
ax.set_ylabel("Failed Capital (% of Total)", fontsize=20)

ax.tick_params(axis="both", which="major", labelsize=14)

ax.set_yscale("log")
ax.grid(alpha=0.3)



plt.tight_layout()
plt.show()






















import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = [
    ("Australia", 2.57), ("Austria", 0.90), ("Belgium", 1.62), ("Canada", 3.49),
    ("Finland", 1.24), ("France", 6.59), ("Germany", 3.65), ("Greece", 0.73),
    ("Ireland", 2.29), ("Italy", 24.57), ("Japan", 15.02), ("Netherlands", 5.64),
    ("Portugal", 0.49), ("Spain", 4.19), ("Sweden", 0.77), ("Switzerland", 1.78),
    ("United Kingdom", 45.03), ("United States", 96.23),
]
df = pd.DataFrame(data, columns=["Country", "FailedCapitalPct"])

iso2_to_name = {
    "AT":"Austria","AU":"Australia","BE":"Belgium","BR":"Brazil","CA":"Canada",
    "CH":"Switzerland","CL":"Chile","DE":"Germany","DK":"Denmark","ES":"Spain",
    "FI":"Finland","FR":"France","GB":"United Kingdom","HK":"Hong Kong","IE":"Ireland",
    "IT":"Italy","NL":"Netherlands","SE":"Sweden","US":"United States","JP":"Japan"
}
countries = list(iso2_to_name.keys())

vals_2009Q2 = [
    0.794038, 0.352396, 0.078577, 0.472990, 0.035432,
    0.858892, 0.481226, 0.988440, 0.030631, 0.867883,
    0.040789, 0.375728, 0.953423, 0.006477, 0.943267,
    0.892239, 0.720245, 0.015508, 0.849759, 0.927505
]
valuesbubble = [
    0.041324,0.052019,0.030118,0.027851,0.070547,
    0.279063,0.000467,0.125476,0.090995,0.361115,
    0.027988,0.165386,1.000000,0.057331,0.029742,
    0.205336,0.495789,0.062068,1.000000,0.591547
]

df2 = pd.DataFrame({
    "Country": [iso2_to_name[c] for c in countries],
    "MultilayerScore": valuesbubble,     
    "BubbleSize": vals_2009Q2      
})
df_merge = pd.merge(df, df2, on="Country", how="inner")

plt.rcParams["font.family"] = "Times New Roman"
fig, ax = plt.subplots(figsize=(10, 7))

BUBBLE_COLOR = 'tab:blue'

sc = ax.scatter(
    df_merge["MultilayerScore"], 
    df_merge["FailedCapitalPct"], 
    s=200, 
    c=BUBBLE_COLOR, alpha=0.75, edgecolor="black", linewidth=0.8
)

name_to_iso = {v:k for k,v in iso2_to_name.items()}
for _, row in df_merge.iterrows():
    iso = name_to_iso[row["Country"]]
    ax.annotate(
        iso, xy=(row["MultilayerScore"], row["FailedCapitalPct"]),
        xytext=(0, 10), textcoords="offset points",
        ha="center", fontsize=20
    )

ax.set_xlabel(r"Multilayer Risk Score ($\bar{h}_i$, log scale)", fontsize=30)
ax.set_ylabel(
    "Reproduced IMF Single-Layer\nRisk Score (log scale)",
    fontsize=30
)

ax.tick_params(axis="both", which="major", labelsize=25)

ax.set_xscale("log") 
ax.set_yscale("log")
ax.grid(alpha=0.3)

x_min, x_max = ax.get_xlim()
y_min, y_max = ax.get_ylim()

ax.plot([x_min, x_max], [y_min, y_max], color='gray', linestyle='--', linewidth=2)

plt.tight_layout()
plt.show()