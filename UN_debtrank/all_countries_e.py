import pandas as pd

file_path = 'UN_debtrank/UNdata_merged_file.csv'  
output_file_path = 'UN_debtrank/all_countries_e.xlsx'  

chunksize = 100000  
filtered_rows = []  

for chunk in pd.read_csv(file_path, chunksize=chunksize):
    filtered_data = chunk[
        (chunk['freqCode'] == 'M') &         
        (chunk['partnerISO'] == 'W00') &     
        (chunk['flowDesc'] == 'Export') &       
        (chunk['motDesc'] == 'TOTAL MOT') & 
        (chunk['customsDesc'] == 'TOTAL CPC') 
    ].copy()  

    if not filtered_data.empty:
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
        ['period', 'reporterISO']
    ).agg({'primaryValue': 'sum'}).reset_index()

    aggregated_data = pd.merge(
        final_filtered_rows.drop(columns='primaryValue'),
        aggregated_data,
        on=['period', 'reporterISO'],
        how='right'
    )
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















import pandas as pd
import matplotlib.pyplot as plt

# 파일 경로
output_file_path = 'UN_debtrank/all_countries_e.xlsx'  # 이전에 생성한 엑셀 파일 경로

# 엑셀 파일 불러오기
aggregated_data = pd.read_excel(output_file_path, sheet_name='Aggregated Data')

# 'period'를 날짜 형식으로 변환
aggregated_data['period'] = pd.to_datetime(aggregated_data['period'], format='%Y%m')

# 월 단위 데이터 생성
aggregated_data['month'] = aggregated_data['period'].dt.to_period('M')

# 월별 primaryValue 총합 계산
monthly_data = aggregated_data.groupby('month').agg({'primaryValue': 'sum'}).reset_index()

# datetime 형식으로 변환 (그래프용)
monthly_data['month'] = monthly_data['month'].dt.to_timestamp()




import pandas as pd
import matplotlib.pyplot as plt

# 튀는 값 및 필터링
filtered_data = monthly_data[(monthly_data['month'] != '2006-06') & (monthly_data['month'] <= '2009-12')]

# 분기별 데이터 생성
filtered_data['quarter'] = filtered_data['month'].dt.to_period('Q')  # 분기 단위로 변환
quarterly_data = filtered_data.groupby('quarter').agg({'primaryValue': 'sum'}).reset_index()

# 리먼 금융위기 시작 시점
lehman_quarter = pd.Timestamp('2008-07-01')  # 리먼 금융위기 시작 시점


plt.rc('font', size=14)  # 그래프 전체 기본 글자 크기 설정
plt.rc('legend', fontsize=14)  # 범례 글자 크기 설정
# 그래프 생성
plt.figure(figsize=(12, 8))  # 플롯 생성

# 분기별 데이터 플롯
plt.plot(quarterly_data['quarter'].dt.to_timestamp(), quarterly_data['primaryValue'], linestyle='-', color='b', label='Export Value')

# 리먼 금융위기 시작 시점 점선 추가
plt.axvline(x=lehman_quarter, color='red', linestyle='--', label='Lehman Crisis Start (2008-Q3)')

# x축 설정: 2년 단위로 레이블 표시
xticks = pd.date_range(start='2000-01-01',  # 2000년부터 시작
                       end=quarterly_data['quarter'].dt.to_timestamp().max(),
                       freq='2YS')  # 2년 단위 (1월 1일 기준)
plt.xticks(ticks=xticks, labels=[date.strftime('%Y') for date in xticks], rotation=45)


# 그래프 제목 및 축 레이블 설정
plt.title('Total Export Value by Quarter', fontsize=14)
plt.xlabel('Quarter', fontsize=14)
plt.ylabel('Export Value (Sum)', fontsize=14)

# 격자 설정 (필요 시 제거)
plt.grid(True)

# 범례 추가
plt.legend()

# 레이아웃 조정 및 출력
plt.tight_layout()
plt.show()









import pandas as pd
import matplotlib.pyplot as plt

# 파일 경로
output_file_path = 'UN_debtrank/all_countries_e.xlsx'  # 이전에 생성한 엑셀 파일 경로

# 엑셀 파일 불러오기
aggregated_data = pd.read_excel(output_file_path, sheet_name='Aggregated Data')

# 'period'를 날짜 형식으로 변환
aggregated_data['period'] = pd.to_datetime(aggregated_data['period'], format='%Y%m')

# 분석 대상 국가 리스트
target_countries = ['JPN', 'DEU', 'GBR', 'USA']  # 일본, 독일, 영국, 미국

# 국가별 데이터를 저장할 딕셔너리
country_data = {}

for country in target_countries:
    # 각 국가별 데이터 필터링
    country_df = aggregated_data[aggregated_data['reporterISO'] == country]
    country_df['month'] = country_df['period'].dt.to_period('M')
    monthly_data = country_df.groupby('month').agg({'primaryValue': 'sum'}).reset_index()
    monthly_data['month'] = monthly_data['month'].dt.to_timestamp()  # 그래프용
    country_data[country] = monthly_data

# 그래프 생성
plt.figure(figsize=(14, 8))

for country, data in country_data.items():
    # 데이터 정규화 (0~1 사이 값으로 변환)
    normalized_value = (data['primaryValue'] - data['primaryValue'].min()) / (data['primaryValue'].max() - data['primaryValue'].min())
    plt.plot(data['month'], normalized_value, label=f'{country} (Normalized)')

# 금융위기 및 팬데믹 시점 표시
plt.axvline(x=pd.Timestamp('2008-07-01'), color='red', linestyle='--', label='2008 Lehman Crisis')
plt.axvline(x=pd.Timestamp('2020-03-01'), color='blue', linestyle='--', label='2020 COVID-19 Pandemic')

# 그래프 제목 및 축 레이블 설정
plt.title('Normalized Export Value Comparison Across Countries', fontsize=18)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Normalized Export Value', fontsize=14)

# 범례 추가
plt.legend()

# 레이아웃 조정 및 그래프 출력
plt.tight_layout()
plt.show()
