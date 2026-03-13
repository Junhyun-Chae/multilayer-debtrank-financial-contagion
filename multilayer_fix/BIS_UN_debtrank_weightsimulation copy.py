import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

plt.rcParams['font.size'] = 21
plt.rcParams['legend.fontsize'] = 21 

def convert_un_sheet_name_to_bis(sheet_name):
    if sheet_name.startswith("Leverage_") and '-' in sheet_name:
        year, month = sheet_name.split('_')[1].split('-')
        quarter = (int(month) - 1) // 3 + 1
        return f"Leverage_{year}-Q{quarter}"
    return None

def unify_country_names(df):
    country_mapping = {
        'AUT': 'Austria', 'AUS': 'Australia', 'BEL': 'Belgium', 'BRA': 'Brazil', 
        'CAN': 'Canada', 'CHE': 'Switzerland', 'CHL': 'Chile', 'DEU': 'Germany', 
        'DNK': 'Denmark', 'ESP': 'Spain', 'FIN': 'Finland', 'FRA': 'France', 
        'GBR': 'United Kingdom', 'HKG': 'Hong Kong', 'IRL': 'Ireland', 
        'ITA': 'Italy', 'NLD': 'Netherlands', 'SWE': 'Sweden', 'USA': 'United States', 'JPN': 'Japan',
        'AT': 'Austria', 'AU': 'Australia', 'BE': 'Belgium', 'BR': 'Brazil', 
        'CA': 'Canada', 'CH': 'Switzerland', 'CL': 'Chile', 'DE': 'Germany', 
        'DK': 'Denmark', 'ES': 'Spain', 'FI': 'Finland', 'FR': 'France', 
        'GB': 'United Kingdom', 'HK': 'Hong Kong', 'IE': 'Ireland', 
        'IT': 'Italy', 'NL': 'Netherlands', 'SE': 'Sweden', 'US': 'United States', 'JP': 'Japan'
    }
    
    df.index = df.index.map(lambda x: country_mapping.get(x, x))
    df.columns = df.columns.map(lambda x: country_mapping.get(x, x))
    return df

def add_leverage_matrices_with_weights(unleveraged_file_path, bis_file_path, weight_file_path, output_file_path):
    unleveraged_sheets = pd.ExcelFile(unleveraged_file_path).sheet_names
    bis_sheets = pd.ExcelFile(bis_file_path).sheet_names
    weights_df = pd.read_excel(weight_file_path)
    weights_df['Standard_Date'] = weights_df['Standard_Date'].apply(lambda x: f"Leverage_{x}")
    results = {}

    for sheet_name in unleveraged_sheets:
        if sheet_name.startswith("Defaults_"):
            print(f"{sheet_name}는 Defaults 시트이므로 건너뜁니다.")
            continue
        corresponding_bis_sheet = convert_un_sheet_name_to_bis(sheet_name)

        if not corresponding_bis_sheet or corresponding_bis_sheet not in bis_sheets:
            print(f"시트 {sheet_name}의 대응 시트를 {bis_file_path}에서 찾을 수 없습니다. 건너뜁니다.")
            continue

        unleveraged_data = pd.read_excel(unleveraged_file_path, sheet_name=sheet_name, index_col=0)
        bis_data = pd.read_excel(bis_file_path, sheet_name=corresponding_bis_sheet, index_col=0)
        unleveraged_data = unify_country_names(unleveraged_data)
        bis_data = unify_country_names(bis_data)
        weight_row = weights_df[weights_df['Standard_Date'] == corresponding_bis_sheet]
        if weight_row.empty:
            print(f"{corresponding_bis_sheet}에 대한 가중치를 찾을 수 없습니다. 건너뜁니다.")
            continue
    
        unleveraged_weight = weight_row['UN_Weight'].values[0]
        bis_weight = weight_row['BIS_Weight'].values[0]

        if unleveraged_data.shape != bis_data.shape:
            print(f"크기 불일치: {sheet_name} ({unleveraged_data.shape})와 {corresponding_bis_sheet} ({bis_data.shape})")
            continue
        results[sheet_name] = unleveraged_data * unleveraged_weight + bis_data * bis_weight

    if results:
        with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
            for sheet_name, data in results.items():
                data.to_excel(writer, sheet_name=sheet_name)
        print(f"결과가 {output_file_path}에 저장되었습니다.")
    else:
        print("저장할 데이터가 없습니다. 모든 시트가 건너뛰어졌습니다.")

def convert_sheet_name_to_period(sheet_name):
    if sheet_name.startswith("Leverage_"):
        year, month = sheet_name.split('_')[1].split('-')
        quarter = (int(month) - 1) // 3 + 1
        return f"{year}-Q{quarter}"
    return None

def load_leverage_matrices(leverage_file_path, countries):
    sheet_names = pd.ExcelFile(leverage_file_path).sheet_names
    weight_matrices = {}
    
    for sheet in sheet_names:
        period = convert_sheet_name_to_period(sheet)
        if not period:
            continue  
        df = pd.read_excel(leverage_file_path, sheet_name=sheet, index_col=0)
        df = df.reindex(index=countries, columns=countries, fill_value=0)
        weight_matrix = df.values
        weight_matrices[period] = weight_matrix
    return weight_matrices

def initialize_risk(countries, default_probabilities_file_path, period):
    default_probabilities_df = pd.read_excel(default_probabilities_file_path)
    risk_vector = np.zeros(len(countries))
    
    period_data = default_probabilities_df[default_probabilities_df['Year_Quarter'] == period]
    for i, country in enumerate(countries):
        risk_value = period_data[period_data['Country'] == country]['Default_Probability'].values
        if risk_value.size > 0:
            risk_vector[i] = risk_value[0]
    return risk_vector

def propagate_risk_debtrank(weight_matrix, initial_risk_vector, countries, max_iterations=100, threshold=0.001):
    risk_history = []  
    h = initial_risk_vector.copy()  
    H = h.copy()  
    h_prev = np.zeros(len(countries))  
    countries_with_debt_rank_1 = []  

    for iteration in range(max_iterations):
        new_h = np.zeros(len(countries)) 

        for i, country_from in enumerate(countries):
            if H[i] >= 1.0:  
                continue
            
            for j, country_to in enumerate(countries):
                if weight_matrix[j, i] > 0:
                    delta_risk = max(0, h[i] - h_prev[i])
                    new_h[j] += delta_risk * weight_matrix[j, i]
        
        new_h = np.minimum(new_h, 1.0)
        H = np.minimum(H + new_h, 1.0)  

        risk_history.append(H.copy())

        num_countries_with_rank_1 = np.sum(H >= 1.0)
        countries_with_debt_rank_1.append(num_countries_with_rank_1)

        if np.all(new_h < threshold):
            break

        h_prev = h.copy()
        h = new_h.copy()

    return risk_history, countries_with_debt_rank_1

def calculate_total_risk(risk_history, countries):
    total_risk = np.sum(risk_history, axis=0)
    sorted_risk = sorted(enumerate(total_risk), key=lambda x: x[1], reverse=True)

    print("\nTotal Risk Rankings (Highest Impact):")
    for idx, risk in sorted_risk:
        print(f"{countries[idx]}: {risk:.4f}")

def calculate_risk_for_all_periods(weight_matrices, countries, default_probabilities_file_path, output_file):
    all_results = {}
    countries_with_rank_1_summary = {}

    with pd.ExcelWriter(output_file) as writer:
        for period, weight_matrix in weight_matrices.items():
            print(f"\nCalculating risk for Period: {period}")
            initial_risk = initialize_risk(countries, default_probabilities_file_path, period)

            if np.all(initial_risk == 0):
                continue

            risk_history, countries_with_debt_rank_1 = propagate_risk_debtrank(weight_matrix, initial_risk, countries)
            all_results[period] = risk_history
            countries_with_rank_1_summary[period] = countries_with_debt_rank_1

            initial_risk_df = pd.DataFrame(initial_risk, index=countries, columns=[f"Initial_Risk_{period}"])
            weight_matrix_df = pd.DataFrame(weight_matrix, index=countries, columns=countries)
            risk_history_df = pd.DataFrame(risk_history, columns=countries)
            rank_1_df = pd.DataFrame(countries_with_debt_rank_1, columns=["Countries_With_DebtRank_1"])

            safe_period = period.replace('/', '_').replace('\\', '_').replace(':', '_')
            initial_risk_df.to_excel(writer, sheet_name=f'Initial_Risk_{safe_period}')
            weight_matrix_df.to_excel(writer, sheet_name=f'Weight_Matrix_{safe_period}')
            risk_history_df.index.name = 'Step'
            risk_history_df.to_excel(writer, sheet_name=f'Risk_History_{safe_period}')
            rank_1_df.index.name = 'Step'
            rank_1_df.to_excel(writer, sheet_name=f'Rank_1_Count_{safe_period}')

            calculate_total_risk(risk_history, countries)

    print("\nSummary of Countries with DebtRank = 1 by Period:")
    for period, counts in countries_with_rank_1_summary.items():
        print(f"{period}: {counts}")
    
    return all_results, countries_with_rank_1_summary




summary_results = {}


import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

plt.rcParams['font.size'] = 21
plt.rcParams['legend.fontsize'] = 21

summary_results = {}

for i in range(1, 102):
    weight_file_path = f'multilayersimulate/BIS_UN_weights_set_{i}.xlsx'
    output_file_path = f'multilayersimulate/results_with_weights_set_{i}.xlsx'

    if not os.path.exists(weight_file_path):
        print(f"File not found: {weight_file_path}, skipping...")
        continue

    print(f"Processing weight file: {weight_file_path}")

    try:
        add_leverage_matrices_with_weights(
            'UN_debtrank/UN_leverage_and_defaults.xlsx',
            'BIS_debtrank/BIS_leverage_matrices.xlsx',
            weight_file_path,
            output_file_path
        )

        weight_matrices = load_leverage_matrices(output_file_path, [
            'Austria', 'Australia', 'Belgium', 'Brazil', 'Canada', 'Switzerland', 'Chile', 'Germany',
            'Denmark', 'Spain', 'Finland', 'France', 'United Kingdom', 'Hong Kong', 'Ireland',
            'Italy', 'Netherlands', 'Sweden', 'United States', 'Japan'
        ])

        _, countries_with_rank_1_summary = calculate_risk_for_all_periods(
            weight_matrices,
            [
                'Austria', 'Australia', 'Belgium', 'Brazil', 'Canada', 'Switzerland', 'Chile', 'Germany',
                'Denmark', 'Spain', 'Finland', 'France', 'United Kingdom', 'Hong Kong', 'Ireland',
                'Italy', 'Netherlands', 'Sweden', 'United States', 'Japan'
            ],
            'default/Default_Probabilities_5Years_Bond.xlsx',
            output_file_path
        )

        summary_results[f'weights_set_{i}'] = countries_with_rank_1_summary

    except Exception as e:
        print(f"An error occurred while processing weights set {i}: {e}")

print("\nFinal Summary of Countries with DebtRank = 1 by Period for All Files:")
summary_max_with_files = []

for weights_set, periods in summary_results.items():
    for period, counts in periods.items():
        max_countries = max(counts)
        source_file = weights_set
        summary_max_with_files.append((period, max_countries, source_file))

summary_df = pd.DataFrame(summary_max_with_files, columns=["Period", "Max_Countries", "Source_File"])
grouped_summary = summary_df.groupby("Period").apply(
    lambda x: x.loc[x["Max_Countries"].idxmax()]
).reset_index(drop=True)

summary_output_path = 'multilayersimulate/grouped_summary_max.csv'
grouped_summary.to_csv(summary_output_path, index=False)

print(f"Grouped summary saved to {summary_output_path} as CSV format")
file_risk_summary = summary_df.groupby("Source_File")["Max_Countries"].sum().reset_index()


file_risk_summary = file_risk_summary.sort_values(by="Max_Countries", ascending=False)
file_risk_output_path = 'multilayersimulate/file_risk_summary.csv'
file_risk_summary.to_csv(file_risk_output_path, index=False)

print(f"File risk summary saved to {file_risk_output_path} as CSV format")
most_risky_file = file_risk_summary.iloc[0]
print("\nMost risky file:")
print(f"File: {most_risky_file['Source_File']}, Total Max_Countries: {most_risky_file['Max_Countries']}")





countries = [
    'Austria', 'Australia', 'Belgium', 'Brazil', 'Canada', 'Switzerland', 'Chile', 'Germany',
    'Denmark', 'Spain', 'Finland', 'France', 'United Kingdom', 'Hong Kong', 'Ireland',
    'Italy', 'Netherlands', 'Sweden', 'United States', 'Japan'
]

