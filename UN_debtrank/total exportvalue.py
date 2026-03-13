import pandas as pd
import numpy as np

file_path = "UN_debtrank/UNdata_merged_file.csv"
chunksize = 200_000

usecols = [
    "freqCode", "flowDesc",
    "partnerISO", "reporterISO",
    "period", "cifvalue", "fobvalue"
]

acc_country = {}

for chunk in pd.read_csv(file_path, chunksize=chunksize, usecols=usecols):
    chunk["period"] = pd.to_numeric(chunk["period"], errors="coerce")

    mask = (
        (chunk["freqCode"] == "M") &
        (chunk["flowDesc"] == "Export") &
        (chunk["partnerISO"] == "W00") &
        (chunk["period"] >= 200001) &
        (chunk["period"] <= 202312)
    )

    f = chunk.loc[mask].copy()
    if f.empty:
        continue
    cif = pd.to_numeric(f["cifvalue"], errors="coerce").fillna(0)
    fob = pd.to_numeric(f["fobvalue"], errors="coerce").fillna(0)
    f["export_value"] = np.where(cif > 0, cif, np.where(fob > 0, fob, 0.0))
    g = (
        f.groupby(["period", "reporterISO"], as_index=False)["export_value"]
         .sum()
    )

    for row in g.itertuples(index=False):
        key = (int(row.period), row.reporterISO)
        acc_country[key] = acc_country.get(key, 0.0) + float(row.export_value)


country_month = pd.DataFrame(
    [(p, r, v) for (p, r), v in acc_country.items()],
    columns=["period", "reporterISO", "export_value"]
)


global_month = (
    country_month
    .groupby("period", as_index=False)["export_value"]
    .sum()
    .sort_values("period")
)


global_month["date"] = pd.to_datetime(
    global_month["period"].astype(str), format="%Y%m"
)


out_path = "UN_debtrank/global_exports_W00_2000_2023.csv"
global_month.to_csv(out_path, index=False, encoding="utf-8-sig")

print("✅ Global export series (partner=W00) saved")
print(out_path)
