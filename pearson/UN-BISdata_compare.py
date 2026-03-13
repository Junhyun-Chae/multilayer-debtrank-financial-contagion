import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import os

file1_path = 'UN_debtrank/all_countries_e.xlsx'
file2_path = 'BIS_debtrank/all_countries_fx_c.xlsx'

output_dir = 'output_data'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"출력 디렉토리 생성됨: {output_dir}")

file1 = pd.read_excel(file1_path, sheet_name='Aggregated Data')
file2 = pd.read_excel(file2_path, sheet_name='Aggregated Data')

file1_filtered = file1[['period', 'reporterISO', 'primaryValue']]
file2_filtered = file2[['TIME_PERIODTime period or range', 'L_REP_CTYReporting country', 'OBS_VALUEObservation Value']]

file1_filtered.columns = ['period', 'country', 'value1']
file2_filtered.columns = ['period', 'country', 'value2']

def convert_month_to_quarter(period):
    year = str(period)[:4]
    month = int(str(period)[4:6])
    if month in [1, 2, 3]:
        quarter = 'Q1'
    elif month in [4, 5, 6]:
        quarter = 'Q2'
    elif month in [7, 8, 9]:
        quarter = 'Q3'
    else:
        quarter = 'Q4'
    return f"{year}-{quarter}"

file1_filtered['quarter'] = file1_filtered['period'].apply(convert_month_to_quarter)

file1_quarterly = file1_filtered.groupby(['quarter', 'country'], as_index=False).agg({'value1': 'sum'})

file1_quarterly['quarter'] = file1_quarterly['quarter'].str.strip()
file2_filtered['period'] = file2_filtered['period'].str.strip()
file1_quarterly['country'] = file1_quarterly['country'].str.strip()
file2_filtered['country'] = file2_filtered['country'].str.strip()

iso_alpha2_to_alpha3 = {
    'AT': 'AUT', 'BE': 'BEL', 'CA': 'CAN', 'CH': 'CHE', 'DE': 'DEU', 'DK': 'DNK',
    'FR': 'FRA', 'GB': 'GBR', 'IE': 'IRL', 'IT': 'ITA', 'JP': 'JPN', 'LU': 'LUX',
    'NL': 'NLD', 'SE': 'SWE', 'US': 'USA', 'ZA': 'ZAF'
}

def extract_iso_code(country):
    if ':' in country:
        iso_code = country.split(':')[0].strip()
        return iso_alpha2_to_alpha3.get(iso_code, iso_code)
    return country.strip()

file2_filtered.loc[:, 'country'] = file2_filtered['country'].apply(extract_iso_code)


file2_filtered = file2_filtered.drop_duplicates()


merged_data = pd.merge(file1_quarterly, file2_filtered, left_on=['quarter', 'country'], right_on=['period', 'country'], how='inner')


merged_data_output_path = os.path.join(output_dir, 'merged_data_by_quarter_country.xlsx')
merged_data.to_excel(merged_data_output_path, index=False)
print(f"병합된 데이터가 엑셀로 저장되었습니다: {merged_data_output_path}")


def min_max_normalize(series):
    return (series - series.min()) / (series.max() - series.min())


pearson_results = []


countries = merged_data['country'].unique()

for country in countries:
    country_data = merged_data[merged_data['country'] == country]
    country_data_cleaned = country_data.dropna(subset=['value1', 'value2'])
    
    if len(country_data_cleaned) > 1:
        pearson_corr, _ = pearsonr(country_data_cleaned['value1'], country_data_cleaned['value2'])
        pearson_results.append({'country': country, 'pearson_correlation': pearson_corr})
        
        country_data_cleaned['value1_normalized'] = min_max_normalize(country_data_cleaned['value1'])
        country_data_cleaned['value2_normalized'] = min_max_normalize(country_data_cleaned['value2'])
        
        country_output_path = os.path.join(output_dir, f'{country}_data_comparison_normalized.xlsx')
        country_data_cleaned[['quarter', 'value1_normalized', 'value2_normalized']].to_excel(country_output_path, index=False)
        print(f"{country} 데이터가 엑셀로 저장되었습니다: {country_output_path}")

        plt.figure(figsize=(12, 6))
        plt.plot(country_data_cleaned['quarter'], country_data_cleaned['value1_normalized'], marker='o', label='UN Data (Normalized)')
        plt.plot(country_data_cleaned['quarter'], country_data_cleaned['value2_normalized'], marker='x', label='BIS Data (Normalized)')
        plt.title(f'{country} Data Comparison (UN vs BIS, Normalized)', fontsize=14)
        plt.xlabel('Quarter', fontsize=12)
        plt.ylabel('Normalized Value', fontsize=12)
        plt.xticks(rotation=45, fontsize=10)
        plt.legend()
        plt.tight_layout()

        graph_output_path = os.path.join(output_dir, f'{country}_data_comparison_normalized_graph.png')
        plt.savefig(graph_output_path)
        print(f"{country} 데이터 비교 그래프가 저장되었습니다: {graph_output_path}")
        plt.close()
    else:
        print(f"{country} 데이터가 부족하여 피어슨 상관계수를 계산할 수 없습니다.")

merged_cleaned = merged_data.dropna(subset=['value1', 'value2'])
if len(merged_cleaned) > 1:
    overall_corr, _ = pearsonr(merged_cleaned['value1'], merged_cleaned['value2'])
    print(f"전체 데이터의 피어슨 상관계수: {overall_corr}")
    pearson_results.append({'country': 'Overall', 'pearson_correlation': overall_corr})
else:
    print("전체 데이터를 대상으로 피어슨 상관계수를 계산할 수 없습니다.")

pearson_df = pd.DataFrame(pearson_results)

pearson_output_path = os.path.join(output_dir, 'pearson_correlation_results.xlsx')
pearson_df.to_excel(pearson_output_path, index=False)
print(f"피어슨 상관계수 결과가 엑셀로 저장되었습니다: {pearson_output_path}")
