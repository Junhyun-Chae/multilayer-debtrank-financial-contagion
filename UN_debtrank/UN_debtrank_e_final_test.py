import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation
plt.rcParams['font.size'] = 21
plt.rcParams['legend.fontsize'] = 21 

all_countries_file = 'UN_debtrank/all_countries_e.xlsx'
one_country_file = 'UN_debtrank/one_countries_e_c.csv'
output_excel_file = 'UN_debtrank/UN_debtrank_e_final.xlsx'
default_probabilities_file = 'default/Default_Probabilities_5Years_Bond.xlsx'

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

def propagate_risk_debtrank(weight_matrix, initial_risk_vector, countries, max_iterations=100, threshold=0.001):

    risk_history = []  
    h = initial_risk_vector.copy()  
    H = h.copy()  
    h_prev = np.zeros(len(countries)) 

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

        print(f"\nStep {iteration + 1}:")
        for idx, risk in sorted(enumerate(H), key=lambda x: x[1], reverse=True)[:5]:  
            print(f"  {countries[idx]}: {risk:.4f}")

        h_prev = h.copy()
        h = new_h.copy()

        if np.all(new_h < threshold):
            print(f"Converged at Step {iteration + 1}")
            break

    return risk_history

def calculate_total_risk(risk_history, countries):

    total_risk = np.sum(risk_history, axis=0)
    sorted_risk = sorted(enumerate(total_risk), key=lambda x: x[1], reverse=True)

    print("\nTotal Risk Rankings (Highest Impact):")
    for idx, risk in sorted_risk:
        print(f"{countries[idx]}: {risk:.4f}")

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

for period, risk_history in all_risk_results.items():
    print(f"\n--- Period: {period} ---")
    calculate_total_risk(risk_history, countries)

animate_risk_propagation_debtrank(weight_matrices, countries, time_periods, default_probabilities_df)


leverage_and_default_file = 'UN_debtrank/UN_leverage_and_defaults.xlsx'
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




































def calculate_quarterly_risk_rankings(all_risk_results, countries):
    quarterly_rankings = {}
    for period, risk_history in all_risk_results.items():
        final_risk = risk_history[-1]
        risk_ranking = sorted(enumerate(final_risk), key=lambda x: x[1], reverse=True)
    
        quarterly_rankings[period] = [(countries[idx], risk) for idx, risk in risk_ranking]
    
    return quarterly_rankings

def print_quarterly_rankings(quarterly_rankings, top_n=5):
    for period, rankings in quarterly_rankings.items():
        print(f"\n--- Period: {period} ---")
        for rank, (country, risk) in enumerate(rankings[:top_n], start=1):
            print(f"Rank {rank}: {country} - Risk: {risk:.4f}")

quarterly_rankings = calculate_quarterly_risk_rankings(all_risk_results, countries)
print_quarterly_rankings(quarterly_rankings, top_n=5)  
def calculate_overall_risk_rankings(all_risk_results, countries):
    total_risks = np.zeros(len(countries))
    for risk_history in all_risk_results.values():
        total_risks += np.sum(risk_history, axis=0)
    
    overall_rankings = sorted(enumerate(total_risks), key=lambda x: x[1], reverse=True)
    return [(countries[idx], risk) for idx, risk in overall_rankings]

def print_overall_rankings(overall_rankings, top_n=10):
    print("\n=== Overall Risk Rankings (2000-2023) ===")
    for rank, (country, risk) in enumerate(overall_rankings[:top_n], start=1):
        print(f"Rank {rank}: {country} - Risk: {risk:.4f}")

overall_rankings = calculate_overall_risk_rankings(all_risk_results, countries)
print_overall_rankings(overall_rankings, top_n=20)  
quarterly_rankings = calculate_quarterly_risk_rankings(all_risk_results, countries)
print_quarterly_rankings(quarterly_rankings, top_n=20)

overall_rankings = calculate_overall_risk_rankings(all_risk_results, countries)
print_overall_rankings(overall_rankings, top_n=20)


def calculate_top_rank_counts(all_risk_results, countries):
    top_rank_counts = {country: 0 for country in countries}

    for period, risk_history in all_risk_results.items():
        final_risk = risk_history[-1]  
        top_country_idx = np.argmax(final_risk)  
        top_country = countries[top_country_idx]
        top_rank_counts[top_country] += 1

    return top_rank_counts

top_rank_counts = calculate_top_rank_counts(all_risk_results, countries)
print("\n1위를 한 횟수:")
for country, count in sorted(top_rank_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{country}: {count} times")


country_total_transactions = merged_df.groupby('reporterISO')['Given C to Counterparty'].sum()




country_risks = {country: sum(np.sum(history, axis=0)[idx] for history in all_risk_results.values()) for idx, country in enumerate(countries)}
correlation = np.corrcoef(
    [country_total_transactions[country] for country in countries if country in country_total_transactions],
    [country_risks[country] for country in countries]
)[0, 1]

print(f"거래 금액과 노드 중요성의 상관관계: {correlation:.4f}")



import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import matplotlib as mpl

mpl.rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

def filter_common_countries(data_dict1, data_dict2, country_list):
    return [country for country in country_list if country in data_dict1 and country in data_dict2]

country_total_transactions = merged_df.groupby('reporterISO')['Given C to Counterparty'].sum().to_dict()
country_risks = {country: sum(np.sum(history, axis=0)[idx] for history in all_risk_results.values()) for idx, country in enumerate(countries)}

common_countries = filter_common_countries(country_total_transactions, country_risks, countries)

x_data = np.array([country_total_transactions[country] for country in common_countries])
y_data = np.array([country_risks[country] for country in common_countries])

correlation_linear, _ = pearsonr(x_data, y_data)
mask = (x_data > 0) & (y_data > 0)
x_log = np.log10(x_data[mask])
y_log = np.log10(y_data[mask])
correlation_log, _ = pearsonr(x_log, y_log)

fig, axs = plt.subplots(1, 2, figsize=(16, 6))

axs[0].scatter(x_data, y_data, color='gray', alpha=0.7, label="Data")
axs[0].set_xlabel("거래 금액")
axs[0].set_ylabel("노드 중요성")
axs[0].set_title(f"로그 변환 전 (상관계수: {correlation_linear:.4f})")
axs[0].grid(True, linestyle="--", linewidth=0.5)
axs[0].legend()

axs[1].scatter(x_log, y_log, color='gray', alpha=0.7, label="Data")
bins = np.linspace(min(x_log), max(x_log), 20)
bin_centers = 0.5 * (bins[:-1] + bins[1:])
bin_means = [np.mean(y_log[(x_log >= bins[i]) & (x_log < bins[i + 1])]) for i in range(len(bins) - 1)]
axs[1].plot(bin_centers, bin_means, 'o-', color='red', label="Trendline")
axs[1].set_xlabel("거래 금액 (log10)")
axs[1].set_ylabel("노드 중요성 (log10)")
axs[1].set_title(f"로그 변환 후 (상관계수: {correlation_log:.4f})")
axs[1].grid(True, linestyle="--", linewidth=0.5)
axs[1].legend()

plt.tight_layout()
plt.show()



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

def calculate_total_leverage(weight_matrices, countries):
    total_leverage = {country: 0 for country in countries}
    for period, weight_matrix in weight_matrices.items():
        for i, country in enumerate(countries):
            total_leverage[country] += np.sum(weight_matrix[i])  
    return total_leverage

def filter_common_countries(data_dict1, data_dict2, country_list):
    return [country for country in country_list if country in data_dict1 and country in data_dict2]

def plot_correlation(x_data, y_data, x_label, y_label, title):

    x_data = np.array(x_data)
    y_data = np.array(y_data)

    mask = (x_data > 0) & (y_data > 0)
    x_log = np.log10(x_data[mask])
    y_log = np.log10(y_data[mask])

    correlation, _ = pearsonr(x_log, y_log)
    print(f"{title} 상관계수 (로그 변환): {correlation:.4f}")

    plt.figure(figsize=(10, 6))
    plt.scatter(x_log, y_log, color='gray', alpha=0.7, label="Data")

    bins = np.linspace(min(x_log), max(x_log), 20)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    bin_means = [np.mean(y_log[(x_log >= bins[i]) & (x_log < bins[i + 1])]) for i in range(len(bins) - 1)]

    plt.plot(bin_centers, bin_means, 'o-', color='red', label="Trendline")
    plt.xlabel(f"{x_label} (log10)")
    plt.ylabel(f"{y_label} (log10)")
    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.show()

total_leverage = calculate_total_leverage(weight_matrices, countries)

country_risks = {country: sum(np.sum(history, axis=0)[idx] for history in all_risk_results.values()) for idx, country in enumerate(countries)}

common_countries = filter_common_countries(total_leverage, country_risks, countries)

if common_countries:
    x_data = [total_leverage[country] for country in common_countries]
    y_data = [country_risks[country] for country in common_countries]
    plot_correlation(x_data, y_data, "레버리지 합계", "DebtRank", "레버리지와 DebtRank 간 상관관계")


import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

def plot_correlation_with_error_stats(x_data, y_data, labels, x_label, y_label, title, log_scale=False):

    if log_scale:
        x_data = np.log10(x_data)
        y_data = np.log10(y_data)
        x_label += " (log10)"
        y_label += " (log10)"

    plt.figure(figsize=(18, 7))
    plt.scatter(x_data, y_data, color='blue',s=280, alpha=0.7, label="Data")

    for i, label in enumerate(labels):
        plt.annotate(label, (x_data[i], y_data[i]), fontsize=24, alpha=0.7, textcoords="offset points", xytext=(5, 5))

    coeffs = np.polyfit(x_data, y_data, 1)
    trendline = np.poly1d(coeffs)
    plt.plot(x_data, trendline(x_data), color='red', label=f"Trendline: y={coeffs[0]:.2f}x + {coeffs[1]:.2f}")

    errors = np.abs(y_data - trendline(x_data))
    max_error = np.max(errors)
    max_error_idx = np.argmax(errors)
    max_error_label = labels[max_error_idx]

    mean_error = np.mean(errors)
    std_error = np.std(errors)

    plt.annotate(f"Max Error\n{max_error_label}\n({max_error:.4f})",
                 (x_data[max_error_idx], y_data[max_error_idx]),
                 fontsize=18, color="blue", textcoords="offset points", xytext=(-50, 20),
                 arrowprops=dict(facecolor='blue', arrowstyle="->", lw=1.5))

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.savefig("UN Correlation between Leverage and DebtRank.png", dpi=300, bbox_inches='tight')
    plt.show()

    print(f"최대 오차: {max_error:.4f} (국가: {max_error_label})")
    print(f"평균 거리: {mean_error:.4f}")
    print(f"표준 편차: {std_error:.4f}")

if common_countries:
    x_data = [total_leverage[country] for country in common_countries]  
    y_data = [country_risks[country] for country in common_countries]  
    labels = common_countries 

    plot_correlation_with_error_stats(x_data, y_data, labels, "leverage matrix", "DebtRank", "UN Correlation between Leverage and DebtRank", log_scale=False)
    plot_correlation_with_error_stats(x_data, y_data, labels, "leverage matrix", "DebtRank", "UN Correlation between Leverage and DebtRank", log_scale=True)













import numpy as np
import matplotlib.pyplot as plt
 
def select_largest_and_smallest_transactions(country_transactions, valid_countries):

    valid_transactions = {
        country: amount
        for country, amount in country_transactions.items()
        if country in valid_countries and amount > 0  
    }
    if not valid_transactions:
        raise ValueError("유효한 거래 금액을 가진 국가가 없습니다.")

    largest_country = max(valid_transactions, key=valid_transactions.get)
    smallest_country = min(valid_transactions, key=valid_transactions.get)

    return largest_country, smallest_country

country_total_transactions = merged_df.groupby('reporterISO')['Given C to Counterparty'].sum().to_dict()

largest_country, smallest_country = select_largest_and_smallest_transactions(
    country_total_transactions, countries
)
print(f"거래 금액이 가장 큰 국가: {largest_country}, 거래 금액: {country_total_transactions[largest_country]}")
print(f"거래 금액이 가장 작은 국가: {smallest_country}, 거래 금액: {country_total_transactions[smallest_country]}")

initial_default_prob = 0.05

def initialize_custom_risk(countries, largest_country, smallest_country, initial_prob):
    risk_vector = np.zeros(len(countries))
    for i, country in enumerate(countries):
        if country == largest_country or country == smallest_country:
            risk_vector[i] = initial_prob
    print(f"Initialized Risk Vector: {risk_vector}")
    return risk_vector


def simulate_risk_propagation(weight_matrix, initial_risk_vector, countries, max_iterations=10):
    risk_history = [initial_risk_vector.copy()] 
    h = initial_risk_vector.copy()
    H = h.copy()

    for step in range(max_iterations):
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
        h = new_h
    return risk_history

def simulate_risk_propagation_all_periods(weight_matrices, countries, largest_country, smallest_country, initial_default_prob, max_iterations=10):
    total_steps = max_iterations + 1  
    cumulative_risks_largest = np.zeros(total_steps)
    cumulative_risks_smallest = np.zeros(total_steps)
    period_count = 0

    for period, weight_matrix in weight_matrices.items():
        initial_risk_vector = initialize_custom_risk(countries, largest_country, smallest_country, initial_default_prob)

        risk_history = simulate_risk_propagation(weight_matrix, initial_risk_vector, countries, max_iterations=max_iterations)

        for step in range(total_steps):
            if step < len(risk_history):
                cumulative_risks_largest[step] += risk_history[step][countries.index(largest_country)]
                cumulative_risks_smallest[step] += risk_history[step][countries.index(smallest_country)]

        period_count += 1
    average_risks_largest = cumulative_risks_largest / period_count
    average_risks_smallest = cumulative_risks_smallest / period_count

    


    print(f"Average Risks (Largest): {average_risks_largest}")  
    print(f"Average Risks (Smallest): {average_risks_smallest}") 

    return average_risks_largest, average_risks_smallest

average_risks_largest, average_risks_smallest = simulate_risk_propagation_all_periods(
    weight_matrices,
    countries,
    largest_country,
    smallest_country,
    initial_default_prob,
    max_iterations=10
)

def plot_average_risk_propagation(average_risks_largest, average_risks_smallest, largest_country, smallest_country):
    steps = len(average_risks_largest)

    plt.figure(figsize=(10, 6))
    plt.plot(range(steps), average_risks_largest, label=f"{largest_country} (Max leverage matrix country)", marker='o')
    plt.plot(range(steps), average_risks_smallest, label=f"{smallest_country} (Min leverage matrix country)", marker='o', linestyle='--')
    plt.xlabel("Propagation Step")
    plt.ylabel("Average Cumulative Risk")
    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.savefig("UN Risk Propagation Simulation: Initial Risk Set to 0.05 for Largest and Smallest Countries, 0 for Others.png", dpi=300, bbox_inches='tight')
    plt.show()

plot_average_risk_propagation(average_risks_largest, average_risks_smallest, largest_country, smallest_country)












from scipy.stats import pearsonr, spearmanr

def calculate_node_degrees(weight_matrices, countries):
    node_degrees = {}

    for period, weight_matrix in weight_matrices.items():
        node_degree = [np.count_nonzero(weight_matrix[:, i]) for i in range(len(countries))]
        node_degrees[period] = node_degree

    return node_degrees

from scipy.stats import pearsonr, spearmanr
import numpy as np

def calculate_correlation(all_risk_results, default_probabilities_df, node_degrees, countries):
    correlation_results = {
        'Node Degree': [],
        'Default Probability': []
    }

    for period, risk_history in all_risk_results.items():
        final_risk_vector = risk_history[-1]
        period_data = default_probabilities_df[default_probabilities_df['Year_Quarter'] == period]
        node_degree_values = node_degrees.get(period, [])
        
        valid_risk_values = []
        valid_node_degrees = []
        valid_default_probabilities = []

        for i, country in enumerate(countries):
            country_name = country_name_mapping.get(country)
            if country_name:
                default_prob = period_data[period_data['Country'] == country_name]['Default_Probability'].values
                if len(default_prob) > 0 and i < len(node_degree_values):
                    risk_value = final_risk_vector[i]
                    node_degree_value = node_degree_values[i]
                
                    if not np.isnan(risk_value) and not np.isnan(node_degree_value):
                        valid_risk_values.append(risk_value)
                        valid_node_degrees.append(node_degree_value)
                        valid_default_probabilities.append(default_prob[0])

        def is_constant(arr):
            return len(set(arr)) == 1

        if valid_node_degrees and valid_risk_values and not is_constant(valid_node_degrees):
            try:
                pearson_node, _ = pearsonr(valid_node_degrees, valid_risk_values)
                spearman_node, _ = spearmanr(valid_node_degrees, valid_risk_values)
                correlation_results['Node Degree'].append((pearson_node, spearman_node))
            except ValueError:
                correlation_results['Node Degree'].append((None, None))
        else:
            correlation_results['Node Degree'].append((None, None))
            print(f"Skipping Node Degree correlation for period {period} due to constant values.")

        if valid_default_probabilities and valid_risk_values and not is_constant(valid_default_probabilities):
            try:
                pearson_default, _ = pearsonr(valid_default_probabilities, valid_risk_values)
                spearman_default, _ = spearmanr(valid_default_probabilities, valid_risk_values)
                correlation_results['Default Probability'].append((pearson_default, spearman_default))
            except ValueError:
                correlation_results['Default Probability'].append((None, None))
        else:
            correlation_results['Default Probability'].append((None, None))
            print(f"Skipping Default Probability correlation for period {period} due to constant values.")

    return correlation_results




def calculate_average_correlation(correlation_results):
    avg_results = {}
    for key, values in correlation_results.items():
        pearson_values = [v[0] for v in values if v[0] is not None]
        spearman_values = [v[1] for v in values if v[1] is not None]
        avg_pearson = np.mean(pearson_values) if pearson_values else None
        avg_spearman = np.mean(spearman_values) if spearman_values else None
        avg_results[key] = {
            'Average Pearson': avg_pearson,
            'Average Spearman': avg_spearman
        }
    return avg_results

node_degrees = calculate_node_degrees(weight_matrices, countries)
correlation_results = calculate_correlation(all_risk_results, default_probabilities_df, node_degrees, countries)
average_correlations = calculate_average_correlation(correlation_results)

print("\n--- Average Correlation Results ---")
for key, averages in average_correlations.items():
    print(f"\n{key}:")
    print(f"  Average Pearson Correlation: {averages['Average Pearson']:.4f}" if averages['Average Pearson'] is not None else "  Average Pearson Correlation: None")
    print(f"  Average Spearman Correlation: {averages['Average Spearman']:.4f}" if averages['Average Spearman'] is not None else "  Average Spearman Correlation: None")
