import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

FAILED_CAPITAL = {
    "Australia": 2.57, "Austria": 0.90, "Belgium": 1.62, "Canada": 3.49,
    "Finland": 1.24, "France": 6.59, "Germany": 3.65, "Greece": 0.73,
    "Ireland": 2.29, "Italy": 24.57, "Japan": 15.02, "Netherlands": 5.64,
    "Portugal": 0.49, "Spain": 4.19, "Sweden": 0.77, "Switzerland": 1.78,
    "United Kingdom": 45.03, "United States": 96.23,
}

ISO2_TO_NAME = {
    "AT": "Austria", "AU": "Australia", "BE": "Belgium", "BR": "Brazil",
    "CA": "Canada", "CH": "Switzerland", "CL": "Chile", "DE": "Germany",
    "DK": "Denmark", "ES": "Spain", "FI": "Finland", "FR": "France",
    "GB": "United Kingdom", "HK": "Hong Kong", "IE": "Ireland",
    "IT": "Italy", "NL": "Netherlands", "SE": "Sweden",
    "US": "United States", "JP": "Japan",
}

RISK_FINAL = {
    "AT":0.041324,"AU":0.052019,"BE":0.030118,"BR":0.027851,"CA":0.070547,
    "CH":0.279063,"CL":0.000467,"DE":0.125476,"DK":0.090995,"ES":0.361115,
    "FI":0.027988,"FR":0.165386,"GB":1.000000,"HK":0.057331,"IE":0.029742,
    "IT":0.205336,"NL":0.495789,"SE":0.062068,"US":1.000000,"JP":0.591547
}

RISK_2009Q2 = [
    0.794038, 0.352396, 0.078577, 0.472990, 0.035432,
    0.858892, 0.481226, 0.988440, 0.030631, 0.867883,
    0.040789, 0.375728, 0.953423, 0.006477, 0.943267,
    0.892239, 0.720245, 0.015508, 0.849759, 0.927505
]
ISO2_ORDER_20 = ["AT","AU","BE","BR","CA","CH","CL","DE","DK","ES",
                 "FI","FR","GB","HK","IE","IT","NL","SE","US","JP"]

df_failed = pd.DataFrame(
    [(k, v) for k, v in FAILED_CAPITAL.items()],
    columns=["Country", "FailedCapitalPct"]
)

df_risk_final = pd.DataFrame(
    [(ISO2_TO_NAME[k], v) for k, v in RISK_FINAL.items()],
    columns=["Country", "RiskValue"]
)

df_merge = pd.merge(df_failed, df_risk_final, on="Country", how="inner")

plt.figure(figsize=(12, 6))
df_failed_sorted = df_failed.sort_values("FailedCapitalPct", ascending=False)
plt.scatter(df_failed_sorted["Country"], df_failed_sorted["FailedCapitalPct"], s=100)
plt.xticks(rotation=60, ha="right")
plt.ylabel("Failed Capital (% of Total)")
plt.title("Failed Capital by Country — Simulation 1 (Credit Channel)")
for i, val in enumerate(df_failed_sorted["FailedCapitalPct"]):
    plt.text(i, val * 1.01, f"{val:.2f}", ha="center", fontsize=8)
plt.tight_layout()
plt.show()

plt.figure(figsize=(14, 7))
plt.scatter(list(RISK_FINAL.keys()), list(RISK_FINAL.values()), s=120, alpha=0.7)
plt.xticks(rotation=45)
plt.ylabel("Final Risk Value (Last Row)")
plt.title("Scatter Plot of Final Risk Values")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 7))
plt.scatter(df_merge["RiskValue"], df_merge["FailedCapitalPct"], s=140, alpha=0.8)
for _, row in df_merge.iterrows():
    iso = [k for k, v in ISO2_TO_NAME.items() if v == row["Country"]][0]
    plt.annotate(iso, (row["RiskValue"], row["FailedCapitalPct"]),
                 xytext=(0, 10), textcoords="offset points", ha="center", fontsize=12)
plt.xlabel("Multilayer Risk Value")
plt.ylabel("Failed Capital (% of Total)")
plt.title("Failed Capital vs Multilayer Risk Value")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

df_2009 = pd.DataFrame({
    "ISO2": ISO2_ORDER_20,
    "Risk2009Q2": RISK_2009Q2
})
df_2009["Country"] = df_2009["ISO2"].map(ISO2_TO_NAME)
df_2009m = pd.merge(df_2009, df_failed, on="Country", how="inner")

plt.figure(figsize=(10, 7))
plt.scatter(df_2009m["Risk2009Q2"], df_2009m["FailedCapitalPct"], s=120, alpha=0.8)
for _, r in df_2009m.iterrows():
    plt.annotate(r["ISO2"], (r["Risk2009Q2"], r["FailedCapitalPct"]),
                 xytext=(0, 10), textcoords="offset points", ha="center", fontsize=12)
plt.xlabel("Final Risk Value (2009-Q2)")
plt.ylabel("Failed Capital (% of Total)")
plt.title("Failed Capital vs 2009-Q2 Risk Value")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
