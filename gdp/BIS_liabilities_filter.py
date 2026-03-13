import pandas as pd

file_path = 'BIS_debtrank/WS_LBS_D_PUB_csv_flat.csv' 
output_aggregated_path = 'gdp/aggregated_data.csv'  
output_filtered_path = 'gdp/filtered_rows.csv'  

chunksize = 100000 
filtered_rows = [] 

for chunk in pd.read_csv(file_path, chunksize=chunksize):
    chunk.columns = chunk.columns.str.replace(':', '').str.strip()
    filtered_data = chunk[
        (chunk['FREQFrequency'] == 'Q: Quarterly') &
        (chunk['L_INSTRType of instruments'] == 'A: All instruments') &
        (chunk['L_DENOMCurrency denomination'] == 'TO1: All currencies') &
        (chunk['L_CURR_TYPECurrency type of reporting country'] == 'A: All currencies (=D+F+U)') &
        (chunk['L_REP_BANK_TYPEType of reporting institutions'] == 'A: All reporting banks/institutions (domestic, foreign, consortium and unclassified)') &
        (chunk['L_POS_TYPEPosition type'] == 'N: Cross-border') &
        (chunk['L_CP_SECTORCounterparty sector'] == 'A: All sectors') &
        (chunk['L_POSITIONBalance sheet position'] == 'L: Total liabilities')
    ]

    if not filtered_data.empty:
        filtered_rows.append(filtered_data)

if filtered_rows:
    final_filtered_rows = pd.concat(filtered_rows, ignore_index=True)
else:
    final_filtered_rows = pd.DataFrame()

if not final_filtered_rows.empty:
    final_filtered_rows['OBS_VALUEObservation Value'] = pd.to_numeric(final_filtered_rows['OBS_VALUEObservation Value'], errors='coerce').fillna(0)
    
    aggregated_data = final_filtered_rows.groupby(
        ['TIME_PERIODTime period or range', 'L_REP_CTYReporting country']
    ).agg({'OBS_VALUEObservation Value': 'sum'}).reset_index()

    aggregated_data = pd.merge(final_filtered_rows.drop(columns='OBS_VALUEObservation Value'), aggregated_data, on=['TIME_PERIODTime period or range', 'L_REP_CTYReporting country'], how='right')
else:
    aggregated_data = pd.DataFrame()

if not aggregated_data.empty:
    aggregated_data.to_csv(output_aggregated_path, index=False)  
if not final_filtered_rows.empty:
    final_filtered_rows.to_csv(output_filtered_path, index=False) 

print(f"집계된 데이터가 '{output_aggregated_path}'에 저장되었습니다.")
print(f"필터링된 데이터가 '{output_filtered_path}'에 저장되었습니다.")







import pandas as pd

input_file = 'gdp/aggregated_data.csv'
output_file = 'gdp/liabilities.csv'  


target_countries = [
    'AT', 'AU', 'BE', 'BR', 'CA', 'CH', 'CL', 'DE', 'DK', 'ES', 
    'FI', 'FR', 'GB', 'HK', 'IE', 'IT', 'NL', 'SE', 'US', 'JP'
]

data = pd.read_csv(input_file)

data.columns = data.columns.str.strip().str.replace(':', '').str.replace(' ', '')

data['L_REP_CTYReportingcountry'] = data['L_REP_CTYReportingcountry'].str.extract(r'([A-Z]{2})')

filtered_data = data[data['L_REP_CTYReportingcountry'].isin(target_countries)]
filtered_data = filtered_data[filtered_data['TIME_PERIODTimeperiodorrange'] >= '2000-Q1']
filtered_data = filtered_data.drop_duplicates(subset=['L_REP_CTYReportingcountry', 'TIME_PERIODTimeperiodorrange', 'OBS_VALUEObservationValue'])
columns_to_keep = ['L_REP_CTYReportingcountry', 'TIME_PERIODTimeperiodorrange', 'OBS_VALUEObservationValue']
filtered_data = filtered_data[columns_to_keep]

filtered_data.rename(
    columns={
        'L_REP_CTYReportingcountry': 'Country',
        'TIME_PERIODTimeperiodorrange': 'Quarter',
        'OBS_VALUEObservationValue': 'Liabilities'
    },
    inplace=True
)

filtered_data.to_csv(output_file, index=False)

print(f"중복을 제거한 데이터가 '{output_file}'에 저장되었습니다.")
