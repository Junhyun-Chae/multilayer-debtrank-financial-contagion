import pandas as pd


file_path = 'UN_debtrank/UNdata_merged_file.csv' 
output_aggregated_path = 'UN_debtrank/one_countries_e_c.csv'  

chunksize = 100000  
filtered_rows = []  


for chunk in pd.read_csv(file_path, chunksize=chunksize):

    filtered_data = chunk[
        (chunk['freqCode'] == 'M') &         
        (chunk['flowDesc'] == 'Export') &    
        (chunk['motDesc'] == 'TOTAL MOT') & 
        (chunk['customsDesc'] == 'TOTAL CPC') &
        (chunk['partnerISO'] != 'W00')   
    ].copy()  

    filtered_data.loc[:, 'primaryValue'] = filtered_data.apply(
        lambda row: row['cifvalue'] if row['cifvalue'] > 0 else (row['fobvalue'] if row['fobvalue'] > 0 else 0),
        axis=1
    )
    filtered_rows.append(filtered_data)

if filtered_rows:
    final_filtered_rows = pd.concat(filtered_rows, ignore_index=True)
else:
    final_filtered_rows = pd.DataFrame()

if not final_filtered_rows.empty:
    aggregated_data = final_filtered_rows.groupby(
        ['period', 'reporterISO', 'partnerISO']
    ).agg({'primaryValue': 'sum'}).reset_index()
else:
    aggregated_data = pd.DataFrame()


if not aggregated_data.empty:
    aggregated_data.to_csv(output_aggregated_path, index=False, encoding='utf-8-sig') 
print(f"집계된 데이터는 '{output_aggregated_path}'에 저장되었습니다.")

