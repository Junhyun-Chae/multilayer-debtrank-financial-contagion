import pandas as pd

file_path = 'WS_LBS_D_PUB_csv_flat.csv'  
output_file_path = 'BIS_debtrank/all_countries_fx_c.xlsx'  

chunksize = 100000  
aggregated_results = [] 
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
        (chunk['L_MEASUREMeasure'] == 'F: FX and break adjusted change (BIS calculated)') &
        (chunk['L_CP_SECTORCounterparty sector']=='A: All sectors') &
        (chunk['L_POSITIONBalance sheet position'] == 'C: Total claims')
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

with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
    if not aggregated_data.empty:
        aggregated_data.to_excel(writer, sheet_name='Aggregated Data', index=False)
    if not final_filtered_rows.empty:
        final_filtered_rows.to_excel(writer, sheet_name='Filtered Rows', index=False)

    workbook = writer.book
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
    
    if not aggregated_data.empty:
        worksheet_aggregated = writer.sheets['Aggregated Data']
        for col_num, value in enumerate(aggregated_data.columns.values):
            worksheet_aggregated.write(0, col_num, value, header_format)
    
    if not final_filtered_rows.empty:
        worksheet_filtered = writer.sheets['Filtered Rows']
        for col_num, value in enumerate(final_filtered_rows.columns.values):
            worksheet_filtered.write(0, col_num, value, header_format)

print(f"집계된 데이터와 필터링된 행이 '{output_file_path}' 파일에 저장되었습니다.")