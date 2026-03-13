import pandas as pd
import os

gdp_file = 'gdp/IMF_GDP_currency.xlsx'

exchange_rate_folder = 'gdp/'

required_countries = [
    'Austria', 'Australia', 'Belgium', 'Brazil', 'Canada', 'Switzerland', 'Chile',
    'Germany', 'Denmark', 'Spain', 'Finland', 'France', 'United Kingdom', 'Hong Kong',
    'Ireland', 'Italy', 'Netherlands', 'Sweden', 'United States', 'Japan'
]

currency_mapping = {
    'Austria': 'USD_EUR Historical Data.csv',
    'Australia': 'USD_AUD Historical Data.csv',
    'Belgium': 'USD_EUR Historical Data.csv',
    'Brazil': 'USD_BRL Historical Data.csv',
    'Canada': 'USD_CAD Historical Data.csv',
    'Switzerland': 'USD_CHF Historical Data.csv',
    'Chile': 'USD_CLP Historical Data.csv',
    'Germany': 'USD_EUR Historical Data.csv',
    'Denmark': 'USD_DKK Historical Data.csv',
    'Spain': 'USD_EUR Historical Data.csv',
    'Finland': 'USD_EUR Historical Data.csv',
    'France': 'USD_EUR Historical Data.csv',
    'United Kingdom': 'USD_GBP Historical Data.csv',
    'Hong Kong': 'USD_HKD Historical Data.csv',
    'Ireland': 'USD_EUR Historical Data.csv',
    'Italy': 'USD_EUR Historical Data.csv',
    'Netherlands': 'USD_EUR Historical Data.csv',
    'Sweden': 'USD_SEK Historical Data.csv',
    'United States': 'USD_USD',  # 고정값 1 처리
    'Japan': 'USD_JPY Historical Data.csv'
}

gdp_data = pd.read_excel(gdp_file, header=6)
gdp_data = gdp_data[gdp_data['Country'].isin(required_countries)]
gdp_cleaned = gdp_data[['Country'] + [col for col in gdp_data.columns if 'Q' in col]]
gdp_data_melted = gdp_cleaned.melt(id_vars=['Country'], var_name='Quarter', value_name='GDP')
gdp_data_melted['Quarter'] = gdp_data_melted['Quarter'].str.extract(r'(\d{4}Q[1-4])')[0]
gdp_data_melted['Quarter'] = pd.PeriodIndex(gdp_data_melted['Quarter'], freq='Q')
gdp_data_melted['GDP'] = pd.to_numeric(gdp_data_melted['GDP'], errors='coerce')


quarterly_exchange_rates = {}

for country, filename in currency_mapping.items():
    if country not in required_countries:
        continue

    if country == 'United States': 
        quarterly_exchange_rates[country] = pd.DataFrame({
            'Quarter': pd.period_range(start='2000Q1', end='2024Q4', freq='Q'),
            'Exchange Rate': 1
        })
        continue

    file_path = os.path.join(exchange_rate_folder, filename)
    try:
        exchange_rate_data = pd.read_csv(file_path)
        exchange_rate_data['Date'] = pd.to_datetime(exchange_rate_data['Date'], format='%m/%d/%Y')
        exchange_rate_data['Price'] = exchange_rate_data['Price'].astype(str).str.replace("'", "").astype(float)
        exchange_rate_data = exchange_rate_data.dropna(subset=['Price'])
        exchange_rate_data['Quarter'] = exchange_rate_data['Date'].dt.to_period('Q')

        quarterly_avg = exchange_rate_data.groupby('Quarter')['Price'].mean().reset_index()
        quarterly_avg.rename(columns={'Price': 'Exchange Rate'}, inplace=True)
        quarterly_avg['Quarter'] = pd.PeriodIndex(quarterly_avg['Quarter'], freq='Q')
        quarterly_exchange_rates[country] = quarterly_avg
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
    except Exception as e:
        print(f"{country} 데이터를 처리하는 중 오류 발생: {e}")

usd_gdp_data = []

for country, group in gdp_data_melted.groupby('Country'):
    exchange_rate_data = quarterly_exchange_rates.get(country, None)

    if exchange_rate_data is not None:
        merged = pd.merge(group, exchange_rate_data, on='Quarter', how='left')
        merged['GDP'] = pd.to_numeric(merged['GDP'], errors='coerce')
        merged['GDP_USD'] = merged['GDP'] / merged['Exchange Rate']
    else: 
        group['GDP_USD'] = group['GDP']
        merged = group
    usd_gdp_data.append(merged)

usd_gdp_data_combined = pd.concat(usd_gdp_data)

print("--- 변환된 GDP 데이터 (USD) ---")
print(usd_gdp_data_combined.head())

usd_gdp_data_combined.to_csv('gdp/gdp_doller_filtered.csv', index=False)
