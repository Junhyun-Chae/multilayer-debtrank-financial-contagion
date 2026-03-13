import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation

all_countries_file = 'UN_debtrank/all_countries_e.xlsx'
one_country_file = 'UN_debtrank/one_countries_e_c.csv'
output_excel_file = 'UN_debtrank/debtrank_analysis.xlsx'
default_probabilities_file = 'UN_debtrank/Default_Probabilities_5Years_Bond.xlsx'

default_probabilities_df = pd.read_excel(default_probabilities_file)

all_countries_df = pd.read_excel(all_countries_file, sheet_name='Aggregated Data')
all_countries_df.columns = all_countries_df.columns.str.strip()

one_country_df = pd.read_csv(one_country_file)
one_country_df.columns = one_country_df.columns.str.strip()

countries = ['AUT', 'AUS', 'BEL', 'BRA', 'CAN', 'CHE', 'CHL', 'DEU', 'DNK', 'ESP',
             'FIN', 'FRA', 'GBR', 'HKG', 'IRL', 'ITA', 'NLD', 'SWE', 'USA', 'JPN']

country_name_mapping = {
    'AUT': 'Austria', 'AUS': 'Australia', 'BEL': 'Belgium', 'BRA': 'Brazil',
    'CAN': 'Canada', 'CHE': 'Switzerland', 'CHL': 'Chile', 'DEU': 'Germany',
    'DNK': 'Denmark', 'ESP': 'Spain', 'FIN': 'Finland', 'FRA': 'France',
    'GBR': 'United Kingdom', 'HKG': 'Hong Kong', 'IRL': 'Ireland',
    'ITA': 'Italy', 'NLD': 'Netherlands', 'SWE': 'Sweden', 'USA': 'United States', 'JPN': 'Japan'
}

def extract_country_code(country_string):
    return country_string.strip()

all_countries_df['reporterISO'] = all_countries_df['reporterISO'].apply(extract_country_code)
all_countries_df['partnerISO'] = all_countries_df['partnerISO'].apply(extract_country_code)
one_country_df['reporterISO'] = one_country_df['reporterISO'].apply(extract_country_code)
one_country_df['partnerISO'] = one_country_df['partnerISO'].apply(extract_country_code)

all_countries_df['period_quarter'] = all_countries_df['period'].apply(lambda x: pd.to_datetime(str(x), format='%Y%m')).dt.to_period('Q').dt.start_time
one_country_df['period_quarter'] = one_country_df['period'].apply(lambda x: pd.to_datetime(str(x), format='%Y%m')).dt.to_period('Q').dt.start_time

all_c_values = (
    all_countries_df
    .groupby(['reporterISO', 'period_quarter'])['primaryValue']
    .sum()
    .reset_index()
    .rename(columns={'primaryValue': 'Total Given C'})
)

filtered_one_country_df = one_country_df[
    one_country_df['reporterISO'].isin(all_c_values['reporterISO'].unique())
]
one_c_values = (
    filtered_one_country_df
    .groupby(['reporterISO', 'partnerISO', 'period_quarter'])['primaryValue']
    .sum()
    .reset_index()
    .rename(columns={'primaryValue': 'Given C to Counterparty'})
)

merged_df = pd.merge(
    one_c_values,
    all_c_values,
    on=['reporterISO', 'period_quarter'],
    how='left'
)
merged_df['Leverage'] = merged_df.apply(
    lambda row: row['Given C to Counterparty'] / row['Total Given C'] if row['Total Given C'] != 0 else 0,
    axis=1
)

time_periods = sorted(merged_df['period_quarter'].unique())  
weight_matrices = {}

for period in time_periods:
    period_data = merged_df[merged_df['period_quarter'] == period]
    weight_matrix = np.zeros((len(countries), len(countries)))
    for _, row in period_data.iterrows():
        if row['reporterISO'] in countries and row['partnerISO'] in countries:
            i = countries.index(row['reporterISO'])
            j = countries.index(row['partnerISO'])
            weight_matrix[j, i] = row['Leverage']
    weight_matrices[period] = weight_matrix


def calculate_node_metrics(weight_matrix):
    total_transactions = np.sum(weight_matrix, axis=0)  
    connections = np.count_nonzero(weight_matrix, axis=0)  
    return total_transactions, connections


def initialize_risk(countries, default_probabilities_df, period):
    risk_vector = np.zeros(len(countries))
    period_data = default_probabilities_df[default_probabilities_df['Year_Quarter'] == period]
    
    for i, country in enumerate(countries):
        country_name = country_name_mapping.get(country)
        if country_name:
            risk_value = period_data[period_data['Country'] == country_name]['Default_Probability'].values
            if risk_value.size > 0:
                risk_vector[i] = risk_value[0]
    return risk_vector

def propagate_risk_with_metrics(weight_matrix, initial_risk_vector, countries, max_iterations=100, threshold=0.01):
    risk_history = []
    risk_history.append(initial_risk_vector.copy())
    h = initial_risk_vector.copy()
    H = h.copy()

    for iteration in range(max_iterations):
        new_h = np.zeros(len(countries))
        for i, country_from in enumerate(countries):
            if H[i] >= 1.0:
                continue
            for j, country_to in enumerate(countries):
                if weight_matrix[j, i] > 0:
                    new_h[j] += h[i] * weight_matrix[j, i]
        new_h = np.minimum(new_h, 1.0)
        H = np.minimum(H + new_h, 1.0)
        risk_history.append(H.copy())
        if np.all(np.abs(new_h) < threshold):
            break
        h = new_h.copy()

    return risk_history, H

results = []
for period in time_periods:
    print(f"Processing period: {period}")
    weight_matrix = weight_matrices[period]
    initial_risk_vector = initialize_risk(countries, default_probabilities_df, period)
    risk_history, final_risks = propagate_risk_with_metrics(weight_matrix, initial_risk_vector, countries)

    most_important_node = countries[np.argmax(final_risks)]
    total_transactions, connections = calculate_node_metrics(weight_matrix)

    for i, country in enumerate(countries):
        results.append({
            'Period': period,
            'Country': country,
            'Final Risk': final_risks[i],
            'Total Transactions': total_transactions[i],
            'Connections': connections[i],
            'Most Important Node': most_important_node
        })


results_df = pd.DataFrame(results)


results_df.to_excel(output_excel_file, index=False)
print(f"Results saved to {output_excel_file}")
