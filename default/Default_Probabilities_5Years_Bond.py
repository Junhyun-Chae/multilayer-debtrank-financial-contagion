import pandas as pd

file_path = "default/IMF_Interest_Rates.xlsx"
df_from_row_6 = pd.read_excel(file_path, skiprows=6)

target_countries = [
    "Australia", "Brazil", "Canada", "Switzerland", "Chile",
    "Denmark", "United Kingdom", "Hong Kong", "Sweden", "United States", "Japan"
]

filtered_data = df_from_row_6[df_from_row_6["Country"].isin(target_countries)]
print(filtered_data)
filtered_data.to_excel("default/IMF_Filtered_Interest_Rates.xlsx", index=False)




import pandas as pd
country_code_map = {
    "Austria": "AT", "Australia": "AU", "Belgium": "BE", "Brazil": "BR",
    "Canada": "CA", "Switzerland": "CH", "Chile": "CL", "Germany": "DE",
    "Denmark": "DK", "Spain": "ES", "Finland": "FI", "France": "FR",
    "United Kingdom": "GB", "Hong Kong": "HK", "Ireland": "IE", 
    "Italy": "IT", "Netherlands": "NL", "Sweden": "SE", 
    "United States": "US", "Japan": "JP"
}

ecb_file_path = "default/ECB_Interest_Rates.xlsx"
filtered_file_path = "default/IMF_Filtered_Interest_Rates_real.xlsx"

try:
    ecb_data = pd.read_excel(ecb_file_path)
    ecb_data.columns = ["Quarter", "Interest Rate (%)"]
    ecb_countries_code_map = {
        "Austria": "AT", "Belgium": "BE", "Germany": "DE", "Spain": "ES",
        "Finland": "FI", "France": "FR", "Ireland": "IE", "Italy": "IT", "Netherlands": "NL"
    }
    ecb_data_expanded = pd.DataFrame()
    for country, code in ecb_countries_code_map.items():
        country_data = ecb_data.copy()
        country_data["Country"] = code
        ecb_data_expanded = pd.concat([ecb_data_expanded, country_data], ignore_index=True)
    
    print("ECB 데이터 정리 완료!")
except Exception as e:
    print(f"ECB 데이터 처리 중 오류 발생: {e}")


try:
    filtered_data = pd.read_excel(filtered_file_path)
    quarter_columns = [col for col in filtered_data.columns if "Q" in col]
    filtered_data = filtered_data[["Country"] + quarter_columns]
    filtered_data = filtered_data.melt(
        id_vars=["Country"],
        var_name="Quarter",
        value_name="Interest Rate (%)"
    )
    filtered_data["Interest Rate (%)"] = pd.to_numeric(filtered_data["Interest Rate (%)"], errors="coerce")
    filtered_data["Country"] = filtered_data["Country"].map(country_code_map)
    
    print("나머지 국가 데이터 정리 완료!")
except Exception as e:
    print(f"나머지 국가 데이터 처리 중 오류 발생: {e}")

try:
    ecb_data_expanded = ecb_data_expanded[["Country", "Quarter", "Interest Rate (%)"]]
    filtered_data = filtered_data[["Country", "Quarter", "Interest Rate (%)"]]
    combined_data = pd.concat([ecb_data_expanded, filtered_data], ignore_index=True)
    combined_data = combined_data.sort_values(by=["Country", "Quarter"]).reset_index(drop=True)
    print(combined_data.head(10))
    
    combined_data.to_csv("default/IMF_EURO_add.csv", index=False)
    print("결과 저장 완료: default/IMF_EURO_add.csv")
except Exception as e:
    print(f"데이터 결합 중 오류 발생: {e}")






import pandas as pd
import os

countries = ['AT: Austria', 'AU: Australia', 'BE: Belgium', 'BR: Brazil', 
             'CA: Canada', 'CH: Switzerland', 'CL: Chile', 'DE: Germany', 
             'DK: Denmark', 'ES: Spain', 'FI: Finland', 'FR: France', 
             'GB: United Kingdom', 'HK: Hong Kong', 'IE: Ireland', 
             'IT: Italy', 'NL: Netherlands', 'SE: Sweden', 'US: United States', 'JP: Japan']

bond_data_all = []

for country in countries:
    file_path = f"5years_bond/{country.split(': ')[1]} 5-Year Bond Yield Historical Data.csv"
    if os.path.exists(file_path):
        print(f"Processing file for: {country.split(': ')[1]}")
        bond_data = pd.read_csv(file_path)
        bond_data['Date'] = pd.to_datetime(bond_data['Date'], format='%m/%d/%Y')
        bond_data['Year_Quarter'] = bond_data['Date'].dt.year.astype(str) + '-Q' + bond_data['Date'].dt.quarter.astype(str)
        bond_quarterly = bond_data.groupby('Year_Quarter')['Price'].mean().reset_index()
        bond_quarterly.rename(columns={'Price': f"{country.split(': ')[1]} 5-Year Bond Yield"}, inplace=True)
        bond_data_all.append(bond_quarterly)


if bond_data_all:
    combined_bond_data = bond_data_all[0]
else:
    raise ValueError('No bond data available for any country.')

for i in range(1, len(bond_data_all)):
    combined_bond_data = pd.merge(combined_bond_data, bond_data_all[i], on='Year_Quarter', how='outer')

print("Combined Bond Data (All Countries):")
print(combined_bond_data.head()) 

combined_bond_data['Year'] = combined_bond_data['Year_Quarter'].str[:4].astype(int) 
filtered_bond_data = combined_bond_data[combined_bond_data['Year'] >= 2000].drop(columns=['Year'])

print("Filtered Bond Data (2000 and later):")
print(filtered_bond_data.head())


filtered_bond_data.to_csv("default/Filtered_5years_Bond_Data_2000_Onwards.csv", index=False)
print("Filtered data saved as: default/Filtered_5years_Bond_Data_2000_Onwards.csv")
















#CDS
import pandas as pd

country_code_map = {
    "Austria": "AT", "Australia": "AU", "Belgium": "BE", "Brazil": "BR",
    "Canada": "CA", "Switzerland": "CH", "Chile": "CL", "Germany": "DE",
    "Denmark": "DK", "Spain": "ES", "Finland": "FI", "France": "FR",
    "United Kingdom": "GB", "Hong Kong": "HK", "Ireland": "IE",
    "Italy": "IT", "Netherlands": "NL", "Sweden": "SE",
    "United States": "US", "Japan": "JP"
}

interest_rates_path = "default/IMF_EURO_add.csv"
bond_yields_path = "default/Filtered_5years_Bond_Data_2000_Onwards.csv"
interest_rates = pd.read_csv(interest_rates_path)
bond_yields = pd.read_csv(bond_yields_path)
bond_yields = bond_yields.rename(
    columns={f"{country} 5-Year Bond Yield": country_code_map[country] for country in country_code_map}
)
bond_yields['Quarter'] = bond_yields['Year_Quarter'].str.replace("-", "")
bond_yields_melted = bond_yields.melt(
    id_vars=['Quarter'],
    value_vars=[code for code in country_code_map.values()],
    var_name='Country',
    value_name='Bond Yield'
)
bond_yields_melted['Bond Yield'] = pd.to_numeric(
    bond_yields_melted['Bond Yield'].astype(str).str.replace("'", ""),
    errors='coerce'
)

merged_data = pd.merge(
    interest_rates,
    bond_yields_melted,
    on=["Country", "Quarter"],
    how="inner"
)

merged_data["Difference"] = merged_data["Bond Yield"] - merged_data["Interest Rate (%)"]

print("Merged Data with Differences:")
print(merged_data.head())
merged_data.to_csv("default/Interest_Rate_vs_Bond_Yield_Differences.csv", index=False)
print("Results saved to: default/Interest_Rate_vs_Bond_Yield_Differences.csv")


















import numpy as np
import pandas as pd
country_code_map = {
    "Austria": "AT", "Australia": "AU", "Belgium": "BE", "Brazil": "BR",
    "Canada": "CA", "Switzerland": "CH", "Chile": "CL", "Germany": "DE",
    "Denmark": "DK", "Spain": "ES", "Finland": "FI", "France": "FR",
    "United Kingdom": "GB", "Hong Kong": "HK", "Ireland": "IE",
    "Italy": "IT", "Netherlands": "NL", "Sweden": "SE",
    "United States": "US", "Japan": "JP"
}
iso_to_country_map = {v: k for k, v in country_code_map.items()}

def calculate_default_probability(cds_spread, recovery_rate=0.4):
    """
    CDS 스프레드로부터 부도확률을 계산하는 함수
    :param cds_spread: CDS 스프레드 (단위: bp, 예: 30bp)
    :param recovery_rate: 회수율 (기본값 40%)
    :return: 부도 확률 (소수점 값, 예: 0.02)
    """
    cds_spread = cds_spread / 10000 
    default_probability = (cds_spread * (1 - recovery_rate)) / (recovery_rate + cds_spread)
    return default_probability

interest_rates_path = "default/IMF_EURO_add.csv"
bond_yields_path = "default/Filtered_5years_Bond_Data_2000_Onwards.csv"

interest_rates = pd.read_csv(interest_rates_path)
bond_yields = pd.read_csv(bond_yields_path)

bond_yields = bond_yields.rename(
    columns={f"{country} 5-Year Bond Yield": country_code_map[country] for country in country_code_map}
)
bond_yields['Quarter'] = bond_yields['Year_Quarter'].str.replace("-", "")

bond_yields_melted = bond_yields.melt(
    id_vars=['Quarter'],
    value_vars=[code for code in country_code_map.values()],
    var_name='Country',
    value_name='Bond Yield'
)

bond_yields_melted['Bond Yield'] = pd.to_numeric(
    bond_yields_melted['Bond Yield'].astype(str).str.replace("'", ""),
    errors='coerce'
)

merged_data = pd.merge(
    interest_rates,
    bond_yields_melted,
    on=["Country", "Quarter"],
    how="inner"
)

if 'Bond Yield' in merged_data.columns and 'Interest Rate (%)' in merged_data.columns:
    merged_data['Difference'] = merged_data['Bond Yield'] - merged_data['Interest Rate (%)']
    merged_data['Difference'] = merged_data['Difference'].fillna(0)
else:
    raise KeyError("Missing columns: 'Bond Yield' or 'Interest Rate (%)'")

merged_data['CDS Spread'] = merged_data['Difference'] * 100 

merged_data['Default Probability'] = merged_data['CDS Spread'].apply(
    lambda x: calculate_default_probability(x, recovery_rate=0.4)
)

merged_data['Country'] = merged_data['Country'].map(iso_to_country_map)


output_path = "default/Default_Probabilities_5Years_Bond.xlsx"

final_output = merged_data[["Quarter", "Country", "Default Probability"]].rename(
    columns={
        "Quarter": "Year_Quarter",
        "Default Probability": "Default_Probability"
    }
)

final_output['Year_Quarter'] = final_output['Year_Quarter'].apply(
    lambda x: f"{x[:4]}-{x[4:]}" if 'Q' in x else x
)

final_output.to_excel(output_path, index=False, float_format="%.9f")
print(f"Results saved to: {output_path}")
