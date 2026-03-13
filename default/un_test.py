import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation

all_countries_file = 'UN_debtrank/all_countries_e.xlsx'
one_country_file = 'UN_debtrank/one_countries_e_c.csv'
output_excel_file = 'UN_debtrank_e_final.xlsx'
default_probabilities_file = 'Default_Probabilities_5Years_Bond.xlsx'
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

country_coords = {
    'AUT': (14.5501, 47.5162), 'AUS': (133.7751, -25.2744), 'BEL': (4.4699, 50.5039), 'BRA': (-51.9253, -14.2350),
    'CAN': (-106.3468, 56.1304), 'CHE': (8.2275, 46.8182), 'CHL': (-71.5429, -35.6751), 'DEU': (10.4515, 51.1657),
    'DNK': (9.5018, 56.2639), 'ESP': (-3.7038, 40.4637), 'FIN': (25.7482, 61.9241), 'FRA': (2.2137, 46.6034),
    'GBR': (-3.4360, 55.3781), 'HKG': (114.1694, 22.3193), 'IRL': (-8.2439, 53.4129), 'ITA': (12.5674, 41.8719),
    'NLD': (5.2913, 52.1326), 'SWE': (18.6435, 60.1282), 'USA': (-95.7129, 37.0902), 'JPN': (138.2529, 36.2048)
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

default_probabilities_df['Year_Quarter'] = pd.PeriodIndex(default_probabilities_df['Year_Quarter'], freq='Q').to_timestamp()

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

def propagate_risk_debtrank(weight_matrix, initial_risk_vector, countries, max_iterations=100, threshold=0.01):
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
            print(f"Converged at Step {iteration + 1}")
            break
        h = new_h.copy()

    return risk_history

def calculate_risk_for_all_periods(weight_matrices, countries, time_periods, default_probabilities_df):
    all_results = {}
    for period in time_periods:
        print(f"Calculating risk for Period: {period}")
        weight_matrix = weight_matrices[period]
        initial_risk = initialize_risk(countries, default_probabilities_df, period)
        risk_history = propagate_risk_debtrank(weight_matrix, initial_risk, countries)
        all_results[period] = risk_history
    return all_results

def save_results_to_excel(all_risk_results, countries, output_file):
    with pd.ExcelWriter(output_file) as writer:
        for period, history in all_risk_results.items():
            formatted_period = pd.Timestamp(period).strftime('%Y-%m') 
            results_df = pd.DataFrame(history, columns=countries)
            results_df.index.name = 'Step'
            results_df.to_excel(writer, sheet_name=f'Period_{formatted_period}')

def animate_risk_propagation_debtrank(weight_matrices, countries, time_periods, default_probabilities_df):
    fig, ax = plt.subplots(figsize=(15, 10))
    m = Basemap(projection='mill', ax=ax)

    all_risk_histories = calculate_risk_for_all_periods(
        weight_matrices, countries, time_periods, default_probabilities_df
    )
    def update(frame):
        ax.clear()
        m.drawcoastlines()
        m.drawcountries()

        cumulative_steps = 0
        for period, risk_history in all_risk_histories.items():
            steps_in_period = len(risk_history)
            if cumulative_steps + steps_in_period > frame:
                step_in_period = frame - cumulative_steps
                risk_vector = risk_history[step_in_period]
                current_period = period
                break
            cumulative_steps += steps_in_period

        weight_matrix = weight_matrices[current_period]
        max_risk = max(risk_vector) if max(risk_vector) > 0 else 1
        for i, country in enumerate(countries):
            if country in country_coords:
                x, y = m(*country_coords[country])
                ax.plot(x, y, 'o', markersize=10, color=plt.cm.Reds(risk_vector[i] / max_risk), alpha=0.8)

        for i, country_from in enumerate(countries):
            for j, country_to in enumerate(countries):
                if weight_matrix[j, i] > 0: 
                    x1, y1 = m(*country_coords[country_from])
                    x2, y2 = m(*country_coords[country_to])
                    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                                arrowprops=dict(arrowstyle='->', color='blue', 
                                                lw=weight_matrix[j, i] * 2, alpha=0.6))

        ax.set_title(f"Period: {current_period}, Step: {step_in_period + 1}", fontsize=16)

    total_steps = sum(len(history) for history in all_risk_histories.values())
    ani = animation.FuncAnimation(fig, update, frames=total_steps, interval=1000, repeat=False)
    plt.show()

output_excel_file = 'UN_debtrank/UN_debtrank_e_final.xlsx'
all_risk_results = calculate_risk_for_all_periods(weight_matrices, countries, time_periods, default_probabilities_df)
save_results_to_excel(all_risk_results, countries, output_excel_file)
print(f"Results saved to {output_excel_file}")

animate_risk_propagation_debtrank(weight_matrices, countries, time_periods, default_probabilities_df)


leverage_and_default_file = 'UN_leverage_and_defaults.xlsx'
with pd.ExcelWriter(leverage_and_default_file) as writer:
    for period in time_periods:
        weight_matrix = weight_matrices[period]
        formatted_period = pd.Timestamp(period).strftime('%Y-%m')
        df = pd.DataFrame(weight_matrix, index=countries, columns=countries)
        df.index.name = 'From'
        df.columns.name = 'To'
        df.to_excel(writer, sheet_name=f'Leverage_{formatted_period}')
        
        default_data = default_probabilities_df[default_probabilities_df['Year_Quarter'] == period]
        actual_defaults = []
        for country in countries:
            country_name = country_name_mapping.get(country, None)
            if country_name:
                risk_value = default_data[default_data['Country'] == country_name]['Default_Probability'].values
                actual_defaults.append(risk_value[0] if len(risk_value) > 0 else 0)
        
        df_defaults = pd.DataFrame({'Country': countries, 'Default_Probability': actual_defaults})
        df_defaults.to_excel(writer, sheet_name=f'Defaults_{formatted_period}', index=False)

print(f"Leverage matrices and Default Probability values saved to {leverage_and_default_file}")
