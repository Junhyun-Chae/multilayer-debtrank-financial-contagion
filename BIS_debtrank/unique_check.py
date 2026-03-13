import pandas as pd
from pathlib import Path

file_path = Path("/Users/junhyunchae/Desktop/credit_/BIS_debtrank/WS_LBS_D_PUB_csv_flat.csv")
out_path = Path("/Users/junhyunchae/Desktop/credit_/usd_eur_filtered.xlsx")
chunksize = 500_000

results = []

for chunk in pd.read_csv(file_path, chunksize=chunksize):
    chunk.columns = chunk.columns.str.replace(':', '').str.strip()

    filtered_data = chunk[
        (chunk['FREQFrequency'] == 'Q: Quarterly') &
        (chunk['L_INSTRType of instruments'] == 'A: All instruments') &
        (chunk['L_DENOMCurrency denomination'].isin(['USD: US dollar', 'EUR: Euro'])) &

        (chunk['L_CURR_TYPECurrency type of reporting country'] == 'A: All currencies (=D+F+U)') &
        (chunk['L_REP_BANK_TYPEType of reporting institutions'] == 'A: All reporting banks/institutions (domestic, foreign, consortium and unclassified)') &
        (chunk['L_POS_TYPEPosition type'] == 'N: Cross-border') &
        (chunk['L_MEASUREMeasure'] == 'B: Break in stocks') &
        (chunk['L_CP_SECTORCounterparty sector'] == 'A: All sectors') &
        (chunk['L_POSITIONBalance sheet position'] == 'C: Total claims')
    ]

    if not filtered_data.empty:
        results.append(filtered_data)

if results:
    df_final = pd.concat(results, ignore_index=True)
    df_final.to_excel(out_path, index=False)
    print(f"완료: {out_path}")
else:
    print("조건에 맞는 데이터가 없습니다.")





import pandas as pd
from pathlib import Path

file_path = Path("/Users/junhyunchae/Desktop/credit_/BIS_debtrank/WS_LBS_D_PUB_csv_flat.csv")

columns = pd.read_csv(file_path, nrows=0).columns.tolist()

print("CSV 헤더(열 이름) 목록:")
for col in columns:
    print(" •", col)



import pandas as pd
from pathlib import Path

csv_path = Path("~/Desktop/credit_/BIS_debtrank/WS_LBS_D_PUB_csv_flat.csv").expanduser()

raw_cols = pd.read_csv(csv_path, nrows=0).columns
print("원본 헤더 예시:", list(raw_cols)[:10])  
clean_cols = raw_cols.str.replace(':', '').str.strip()
col_map = dict(zip(raw_cols, clean_cols))     

df = pd.read_csv(csv_path)
df.rename(columns=col_map, inplace=True)
col = "L_DENOMCurrency denomination"
if col not in df.columns:
    raise KeyError(f"{col} 열이 여전히 없습니다. 실제 헤더를 확인해 보세요 ↖︎")

vals = df[col].dropna().unique()
print("\nunique values:")
for v in vals:
    print(" •", v)

print("\nFrequency:")
print(df[col].value_counts())
