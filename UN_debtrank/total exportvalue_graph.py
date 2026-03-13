import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("UN_debtrank/global_exports_W00_2000_2023.csv")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)
df["pct_change"] = df["export_value"].pct_change()

outlier_threshold = 3.0
outliers = df["pct_change"].abs() > outlier_threshold

print("Detected outliers at:")
print(df.loc[outliers, ["date", "export_value", "pct_change"]])


df["export_value_clean"] = df["export_value"]
df.loc[outliers, "export_value_clean"] = np.nan

df["export_value_clean"] = df["export_value_clean"].interpolate(method="linear")


df["quarter"] = df["date"].dt.to_period("Q")
quarterly = (
    df.groupby("quarter", as_index=False)["export_value_clean"]
      .mean()
)
quarterly["date"] = quarterly["quarter"].dt.to_timestamp()


plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 14

plt.figure(figsize=(12, 7))

plt.plot(
    quarterly["date"],
    quarterly["export_value_clean"],
    color="black",
    linewidth=2,
    label="Global total exports (cleaned)"
)

plt.axvline(pd.Timestamp("2008-09-01"), color="red", linestyle="--", label="Global Financial Crisis")
plt.axvline(pd.Timestamp("2020-03-01"), color="blue", linestyle="--", label="COVID-19 shock")

plt.title("Global Total Exports (World Aggregate, cleaned)")
plt.xlabel("Year")
plt.ylabel("Export value")

plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()
