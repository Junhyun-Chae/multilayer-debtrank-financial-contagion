import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation
plt.rcParams['font.size'] = 21
plt.rcParams['legend.fontsize'] = 21 


all_countries_file = 'BIS_debtrank/all_countries_fx_c.xlsx'
one_country_file = 'BIS_debtrank/one_countries_fx_c.xlsx'
output_excel_file = 'BIS_debtrank/BIS_debtrank_fx_c_final.xlsx'
default_probabilities_file = 'default/Default_Probabilities_5Years_Bond.xlsx'


default_probabilities_df = pd.read_excel(default_probabilities_file)


all_countries_df = pd.read_excel(all_countries_file, sheet_name='Aggregated Data')
all_countries_df.columns = all_countries_df.columns.str.strip()


one_country_df = pd.read_excel(one_country_file, sheet_name='Aggregated Data')
one_country_df.columns = one_country_df.columns.str.strip()


countries = ['AT', 'AU', 'BE', 'BR', 'CA', 'CH', 'CL', 'DE', 'DK', 'ES', 
             'FI', 'FR', 'GB', 'HK', 'IE', 'IT', 'NL', 'SE', 'US', 'JP']

country_name_mapping = {
    'AT': 'Austria', 'AU': 'Australia', 'BE': 'Belgium', 'BR': 'Brazil', 
    'CA': 'Canada', 'CH': 'Switzerland', 'CL': 'Chile', 'DE': 'Germany', 
    'DK': 'Denmark', 'ES': 'Spain', 'FI': 'Finland', 'FR': 'France', 
    'GB': 'United Kingdom', 'HK': 'Hong Kong', 'IE': 'Ireland', 
    'IT': 'Italy', 'NL': 'Netherlands', 'SE': 'Sweden', 'US': 'United States', 'JP': 'Japan'
}

country_coords = {
    'AT': (14.5501, 47.5162), 'AU': (133.7751, -25.2744), 'BE': (4.4699, 50.5039), 'BR': (-51.9253, -14.2350),
    'CA': (-106.3468, 56.1304), 'CH': (8.2275, 46.8182), 'CL': (-71.5429, -35.6751), 'DE': (10.4515, 51.1657),
    'DK': (9.5018, 56.2639), 'ES': (-3.7038, 40.4637), 'FI': (25.7482, 61.9241), 'FR': (2.2137, 46.6034),
    'GB': (-3.4360, 55.3781), 'HK': (114.1694, 22.3193), 'IE': (-8.2439, 53.4129), 'IT': (12.5674, 41.8719),
    'NL': (5.2913, 52.1326), 'SE': (18.6435, 60.1282), 'US': (-95.7129, 37.0902), 'JP': (138.2529, 36.2048)
}

def extract_country_code(country_string):
    return country_string.split(':')[0].strip()

all_countries_df['L_REP_CTYReporting country'] = all_countries_df['L_REP_CTYReporting country'].apply(extract_country_code)
all_countries_df['L_CP_COUNTRYCounterparty country'] = all_countries_df['L_CP_COUNTRYCounterparty country'].apply(extract_country_code)
one_country_df['L_REP_CTYReporting country'] = one_country_df['L_REP_CTYReporting country'].apply(extract_country_code)
one_country_df['L_CP_COUNTRYCounterparty country'] = one_country_df['L_CP_COUNTRYCounterparty country'].apply(extract_country_code)


all_c_values = (
    all_countries_df
    .groupby(['L_REP_CTYReporting country', 'TIME_PERIODTime period or range'])['OBS_VALUEObservation Value']
    .first()
    .reset_index()
    .rename(columns={'OBS_VALUEObservation Value': 'Total Given C'})
)

filtered_one_country_df = one_country_df[
    one_country_df['L_REP_CTYReporting country'].isin(all_c_values['L_REP_CTYReporting country'].unique())
]
one_c_values = (
    filtered_one_country_df
    .groupby(['L_REP_CTYReporting country', 'L_CP_COUNTRYCounterparty country', 'TIME_PERIODTime period or range'])['OBS_VALUEObservation Value']
    .first()
    .reset_index()
    .rename(columns={'OBS_VALUEObservation Value': 'Given C to Counterparty'})
)

merged_df = pd.merge(
    one_c_values,
    all_c_values,
    on=['L_REP_CTYReporting country', 'TIME_PERIODTime period or range'],
    how='left'
)
merged_df['Leverage'] = merged_df.apply(
    lambda row: row['Given C to Counterparty'] / row['Total Given C'] if row['Total Given C'] != 0 else 0,
    axis=1
)

merged_df = merged_df[
    (merged_df['TIME_PERIODTime period or range'] >= '2000-Q1') &
    (merged_df['TIME_PERIODTime period or range'] <= '2023-Q4')
]


time_periods = merged_df['TIME_PERIODTime period or range'].unique()
time_periods = [period for period in time_periods if '2000' <= period[:4] <= '2023']

weight_matrices = {}

for period in time_periods:
    period_data = merged_df[merged_df['TIME_PERIODTime period or range'] == period]
    weight_matrix = np.zeros((len(countries), len(countries)))
    for _, row in period_data.iterrows():
        if row['L_REP_CTYReporting country'] in countries and row['L_CP_COUNTRYCounterparty country'] in countries:
            i = countries.index(row['L_REP_CTYReporting country'])
            j = countries.index(row['L_CP_COUNTRYCounterparty country'])
            weight_matrix[j, i] = max(0, row['Leverage'])
    weight_matrices[period] = weight_matrix


def initialize_risk(countries, default_probabilities_df, period):
    risk_vector = np.zeros(len(countries))
    period_data = default_probabilities_df[default_probabilities_df['Year_Quarter'] == period]
    
    for i, country in enumerate(countries):
        country_name = country_name_mapping.get(country)
        if country_name:
            risk_value = period_data[period_data['Country'] == country_name]['Default_Probability'].values
            if risk_value.size > 0:
                risk_vector[i] = max(0, risk_value[0])  
    return risk_vector


def propagate_risk_debtrank(weight_matrix, initial_risk_vector, countries, max_iterations=100, threshold=0.001):
    risk_history = []  
    h = initial_risk_vector.copy()  
    H = h.copy()  # 누적 리스크
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

        h_prev = h.copy()
        h = new_h.copy()

        print(f"Step {iteration + 1}:")
        for idx, risk in sorted(enumerate(H), key=lambda x: x[1], reverse=True):
            print(f"  {countries[idx]}: {risk:.4f}")

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
            results_df = pd.DataFrame(history, columns=countries)
            results_df.index.name = 'Step'
            results_df.to_excel(writer, sheet_name=f'Period_{period}')

def animate_risk_propagation_debtrank(weight_matrices, countries, time_periods, default_probabilities_df, output_file):
    fig, ax = plt.subplots(figsize=(15, 10))
    m = Basemap(projection='mill', ax=ax)

    import time
    print("\n==== [초기 리스크 적용에 사용된 파산확률 확인] ====")

    for period in time_periods:
        print(f"\nPeriod: {period}")
        period_data = default_probabilities_df[default_probabilities_df['Year_Quarter'] == period]
        
        if period_data.empty:
            print(" 파산확률 데이터 없음")
            continue

        for country in countries:
            country_name = country_name_mapping.get(country)
            if country_name:
                value = period_data[period_data['Country'] == country_name]['Default_Probability'].values
                if value.size > 0:
                    print(f"  {country} ({country_name}): {value[0]:.6f}")
                else:
                    print(f"  {country} ({country_name}):  데이터 없음")
            else:
                print(f"  {country}:  국가 이름 매핑 없음")

    print("\n⏳ 1분간 대기 중...")
    time.sleep(60)
    print("✅ 대기 완료. 계산을 계속 진행합니다.\n")


    all_risk_histories = calculate_risk_for_all_periods(
        weight_matrices, countries, time_periods, default_probabilities_df
    )

    for period, weight_matrix in weight_matrices.items():
        max_value = np.max(weight_matrix)
        if max_value > 0:
            weight_matrices[period] = weight_matrix / max_value

    def update(frame):
        ax.clear()
        m.drawcoastlines()
        m.drawcountries()
        cumulative_steps = 0
        current_period = None
        for period, risk_history in all_risk_histories.items():
            steps_in_period = len(risk_history)
            if cumulative_steps + steps_in_period > frame:
                step_in_period = frame - cumulative_steps
                risk_vector = risk_history[step_in_period]
                current_period = period
                break
            cumulative_steps += steps_in_period

        if current_period:
            max_risk = max(risk_vector) if max(risk_vector) > 0 else 1
            for i, country in enumerate(countries):
                if country in country_coords:
                    x, y = m(*country_coords[country])
                    ax.plot(
                        x, y, 'o', markersize=10, 
                        color=plt.cm.Reds(risk_vector[i] / max_risk), alpha=0.8
                    )

            weight_matrix = weight_matrices[current_period]
            for i, country_from in enumerate(countries):
                for j, country_to in enumerate(countries):
                    if weight_matrix[j, i] > 0:
                        x1, y1 = m(*country_coords[country_from])
                        x2, y2 = m(*country_coords[country_to])
                        line_width = max(0.5, weight_matrix[j, i] * 5) 
                        alpha_value = max(0.3, weight_matrix[j, i])   
                        ax.annotate(
                            '', xy=(x2, y2), xytext=(x1, y1),
                            arrowprops=dict(
                                arrowstyle='->', color=plt.cm.Blues(weight_matrix[j, i]), 
                                lw=line_width, alpha=alpha_value
                            )
                        )

            ax.set_title(f"Period: {current_period}, Step: {step_in_period + 1}", fontsize=16)

    total_steps = sum(len(history) for history in all_risk_histories.values())
    ani = animation.FuncAnimation(fig, update, frames=total_steps, interval=1000, repeat=False)
    ani.save(output_file, writer=animation.FFMpegWriter(fps=2))
    print(f"Animation saved to {output_file}")
    plt.show()


all_risk_results = calculate_risk_for_all_periods(weight_matrices, countries, time_periods, default_probabilities_df)
save_results_to_excel(all_risk_results, countries, output_excel_file)
print(f"Results saved to {output_excel_file}")

for period, risk_history in all_risk_results.items():
    print(f"\n--- Period: {period} ---")
    calculate_total_risk(risk_history, countries)


animation_output_file = 'risk_propagation_animation.mp4'


animate_risk_propagation_debtrank(
    weight_matrices, 
    countries, 
    time_periods, 
    default_probabilities_df, 
    animation_output_file
)



def save_leverage_matrices_to_excel(weight_matrices, countries, output_file):
    with pd.ExcelWriter(output_file) as writer:
        for period, weight_matrix in weight_matrices.items():
            df = pd.DataFrame(weight_matrix, index=countries, columns=countries)
            df.index.name = 'From' 
            df.columns.name = 'To' 
            formatted_period = str(period)  
            df.to_excel(writer, sheet_name=f'Leverage_{formatted_period}')

    print(f"Leverage matrices saved to {output_file}")

leverage_output_file = 'BIS_debtrank/BIS_leverage_matrices.xlsx'
save_leverage_matrices_to_excel(weight_matrices, countries, leverage_output_file)












































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

country_total_transactions = merged_df.groupby('L_REP_CTYReporting country')['Given C to Counterparty'].sum()







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
country_total_transactions = merged_df.groupby('L_REP_CTYReporting country')['Given C to Counterparty'].sum().to_dict()
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
    """
    DebtRank와 레버리지 간의 상관관계를 시각화 (로그 변환 포함)
    """
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

country_name_mapping_3char = {
    'AT': 'AUT', 'AU': 'AUS', 'BE': 'BEL', 'BR': 'BRA',
    'CA': 'CAN', 'CH': 'CHE', 'CL': 'CHL', 'DE': 'DEU',
    'DK': 'DNK', 'ES': 'ESP', 'FI': 'FIN', 'FR': 'FRA',
    'GB': 'GBR', 'HK': 'HKG', 'IE': 'IRL', 'IT': 'ITA',
    'NL': 'NLD', 'SE': 'SWE', 'US': 'USA', 'JP': 'JPN'
}

from adjustText import adjust_text  

def plot_correlation_with_error_stats(x_data, y_data, labels, x_label, y_label, title, log_scale=False):
    """
    산점도와 추세선을 그리고, 각 점에서 추세선까지의 최대 오차, 평균 거리 및 표준 편차를 계산하여 출력.
    """
    labels = [country_name_mapping_3char.get(label, label) for label in labels]

    if log_scale:
        x_data = np.log10(x_data)
        y_data = np.log10(y_data)
        x_label += " (log10)"
        y_label += " (log10)"

    plt.figure(figsize=(18, 7))
    scatter = plt.scatter(x_data, y_data, c='blue', s=280, alpha=0.7, label='Data Points')

    texts = [plt.text(x_data[i], y_data[i], labels[i], fontsize=13, alpha=0.7) for i in range(len(labels))]

    adjust_text(
        texts,
        force_text=0.8, 
        force_points=0.8,  
        expand_text=(1.5, 2),  
        expand_points=(1.5, 2),  
        arrowprops=dict(arrowstyle="->", color='gray', lw=0.5)  
    )

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
                 fontsize=12, color="blue", textcoords="offset points", xytext=(-50, 20),
                 arrowprops=dict(facecolor='blue', arrowstyle="->", lw=1.5))

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title, fontsize=20, pad=20)
    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.savefig("BIS Correlation between Leverage and DebtRank.png", dpi=300, bbox_inches='tight')
    plt.show()

    print(f"최대 오차: {max_error:.4f} (국가: {max_error_label})")
    print(f"평균 거리: {mean_error:.4f}")
    print(f"표준 편차: {std_error:.4f}")




if common_countries:
    x_data = [total_leverage[country] for country in common_countries] 
    y_data = [country_risks[country] for country in common_countries]  
    labels = common_countries 

    plot_correlation_with_error_stats(x_data, y_data, labels, "leverage matrix", "DebtRank", "BIS Correlation between Leverage and DebtRank", log_scale=False)
    plot_correlation_with_error_stats(x_data, y_data, labels, "leverage matrix", "DebtRank", "BIS Correlation between Leverage and DebtRank", log_scale=True)













import numpy as np
import matplotlib.pyplot as plt


def select_largest_and_smallest_transactions(country_transactions, valid_countries):
    """
    거래 금액이 가장 큰 국가와 가장 작은 국가를 선택
    - country_transactions: 국가별 거래 금액 데이터 딕셔너리
    - valid_countries: 필터링된 국가 리스트
    """
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

country_total_transactions = merged_df.groupby('L_REP_CTYReporting country')['Given C to Counterparty'].sum().to_dict()

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
    risk_history = []
    h = initial_risk_vector.copy()
    H = h.copy()
    print(f"Initial H: {H}") 

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
        print(f"Step {step} - New Risk Vector (h): {new_h}") 
        print(f"Step {step} - Cumulative Risk Vector (H): {H}") 
        risk_history.append(H.copy())
        h = new_h
    return risk_history

def simulate_risk_propagation_all_periods(weight_matrices, countries, largest_country, smallest_country, initial_default_prob, max_iterations=10):
    total_steps = max_iterations
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

    country_name_mapping_3char = {
        'AT': 'AUT', 'AU': 'AUS', 'BE': 'BEL', 'BR': 'BRA',
        'CA': 'CAN', 'CH': 'CHE', 'CL': 'CHL', 'DE': 'DEU',
        'DK': 'DNK', 'ES': 'ESP', 'FI': 'FIN', 'FR': 'FRA',
        'GB': 'GBR', 'HK': 'HKG', 'IE': 'IRL', 'IT': 'ITA',
        'NL': 'NLD', 'SE': 'SWE', 'US': 'USA', 'JP': 'JPN'
    }
    largest_country_iso3 = country_name_mapping_3char.get(largest_country, largest_country)
    smallest_country_iso3 = country_name_mapping_3char.get(smallest_country, smallest_country)
    steps = len(average_risks_largest)
    plt.figure(figsize=(10, 6))
    plt.plot(range(steps), average_risks_largest, label=f"{largest_country_iso3} (Max leverage martix country)", marker='o')
    plt.plot(range(steps), average_risks_smallest, label=f"{smallest_country_iso3} (Min leverage martix country)", marker='o', linestyle='--')
    plt.xlabel("Propagation Step")
    plt.ylabel("Average Cumulative Risk")

    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.savefig("BIS Risk Propagation Simulation: Initial Risk Set to 0.05 for Largest and Smallest Countries, 0 for Others.png", dpi=300, bbox_inches='tight')
    plt.show()

plot_average_risk_propagation(average_risks_largest, average_risks_smallest, largest_country, smallest_country)






from scipy.stats import pearsonr

def calculate_node_connections(weight_matrices, countries):
    node_connections = {country: 0 for country in countries}
    for weight_matrix in weight_matrices.values():
        for i, country in enumerate(countries):
            # outgoing + incoming 연결 수
            node_connections[country] += np.sum(weight_matrix[i] > 0) + np.sum(weight_matrix[:, i] > 0)
    return node_connections

def calculate_correlation_connections_debtrank(weight_matrices, all_risk_results, countries):
    node_connections = calculate_node_connections(weight_matrices, countries)
    country_risks = {country: sum(np.sum(history, axis=0)[idx] for history in all_risk_results.values())
                     for idx, country in enumerate(countries)}
    
    common_countries = filter_common_countries(node_connections, country_risks, countries)

    x_data = np.array([node_connections[country] for country in common_countries])
    y_data = np.array([country_risks[country] for country in common_countries])
    correlation, _ = pearsonr(x_data, y_data)
    print(f"노드 연결 수와 DebtRank의 상관관계: {correlation:.4f}")
    return correlation

def calculate_correlation_default_probability_debtrank(default_probabilities_df, all_risk_results, countries):
    avg_default_probabilities = default_probabilities_df.groupby('Country')['Default_Probability'].mean().to_dict()
    country_risks = {country: sum(np.sum(history, axis=0)[idx] for history in all_risk_results.values())
                     for idx, country in enumerate(countries)}

    common_countries = [country for country in countries if country_name_mapping.get(country) in avg_default_probabilities]

    print(f"공통 국가 리스트: {common_countries}")
    print(f"파산확률 데이터에서 누락된 국가: {[country for country in countries if country_name_mapping.get(country) not in avg_default_probabilities]}")

    if len(common_countries) < 2:
        print("Error: 공통 국가의 수가 2개 미만입니다. 상관관계를 계산할 수 없습니다.")
        return None 

    x_data = np.array([avg_default_probabilities[country_name_mapping[country]] for country in common_countries])
    y_data = np.array([country_risks[country] for country in common_countries])

    correlation, _ = pearsonr(x_data, y_data)
    print(f"국가의 파산확률과 DebtRank의 상관관계: {correlation:.4f}")
    return correlation

correlation_default_probability_debtrank = calculate_correlation_default_probability_debtrank(default_probabilities_df, all_risk_results, countries)
correlation_connections_debtrank = calculate_correlation_connections_debtrank(weight_matrices, all_risk_results, countries)
correlation_default_probability_debtrank = calculate_correlation_default_probability_debtrank(default_probabilities_df, all_risk_results, countries)







from scipy.stats import pearsonr, spearmanr
import numpy as np


def calculate_correlation_debtrank_default_prob(all_risk_results, default_probabilities_df, countries):
    correlation_results = {}

    for period, risk_history in all_risk_results.items():
        final_risk_vector = risk_history[-1]
        period_data = default_probabilities_df[default_probabilities_df['Year_Quarter'] == period]
        
        if period_data.empty:
            correlation_results[period] = {
                'Pearson Correlation': None,
                'Spearman Correlation': None
            }
            continue
        
        risk_values = []
        default_probabilities = []
        
        for i, country in enumerate(countries):
            country_name = country_name_mapping.get(country)
            if not country_name:
                continue
            
            risk_value = final_risk_vector[i]
            default_prob = period_data[period_data['Country'] == country_name]['Default_Probability'].values
            if default_prob.size > 0:
                risk_values.append(risk_value)
                default_probabilities.append(default_prob[0])
        
        if risk_values and default_probabilities:
            try:
                pearson_corr, _ = pearsonr(risk_values, default_probabilities)
                spearman_corr, _ = spearmanr(risk_values, default_probabilities)
            except ValueError:
                pearson_corr, spearman_corr = None, None
        else:
            pearson_corr, spearman_corr = None, None
        
        correlation_results[period] = {
            'Pearson Correlation': pearson_corr,
            'Spearman Correlation': spearman_corr
        }

    print("\n--- Correlation Results ---")
    pearson_values = []
    spearman_values = []

    for period, correlations in correlation_results.items():
        pearson = correlations['Pearson Correlation']
        spearman = correlations['Spearman Correlation']

        if pearson is not None:
            pearson_values.append(pearson)
        if spearman is not None:
            spearman_values.append(spearman)

        print(f"Period: {period}")
        print(f"  Pearson Correlation: {pearson:.4f}" if pearson is not None else "  Pearson Correlation: None")
        print(f"  Spearman Correlation: {spearman:.4f}" if spearman is not None else "  Spearman Correlation: None")
    
    pearson_avg = np.mean(pearson_values) if pearson_values else None
    spearman_avg = np.mean(spearman_values) if spearman_values else None

    print("\n--- Average Correlation Results ---")
    print(f"Average Pearson Correlation: {pearson_avg:.4f}" if pearson_avg is not None else "No Pearson Correlation data")
    print(f"Average Spearman Correlation: {spearman_avg:.4f}" if spearman_avg is not None else "No Spearman Correlation data")
    
    return correlation_results, pearson_avg, spearman_avg

correlation_results, average_pearson, average_spearman = calculate_correlation_debtrank_default_prob(
    all_risk_results, default_probabilities_df, countries
)




from scipy.stats import pearsonr, spearmanr
import networkx as nx

def calculate_node_degrees(weight_matrices, countries):
    node_degrees = {}

    for period, weight_matrix in weight_matrices.items():
        G = nx.DiGraph()
        for i, country_from in enumerate(countries):
            for j, country_to in enumerate(countries):
                if weight_matrix[j, i] > 0:
                    G.add_edge(country_from, country_to, weight=weight_matrix[j, i])
        degree_dict = dict(G.degree())
        node_degrees[period] = degree_dict

    return node_degrees

def calculate_correlation_debtrank_node_degree(all_risk_results, node_degrees, countries):
    correlation_results = {}

    for period, risk_history in all_risk_results.items():
        final_risk_vector = risk_history[-1]
        degree_dict = node_degrees.get(period, {})
        node_degree_values = []
        risk_values = []

        for i, country in enumerate(countries):
            if country in degree_dict:
                node_degree_values.append(degree_dict[country])
                risk_values.append(final_risk_vector[i])

        if node_degree_values and risk_values:
            pearson_corr, _ = pearsonr(node_degree_values, risk_values)
            spearman_corr, _ = spearmanr(node_degree_values, risk_values)

            correlation_results[period] = {
                'Pearson Correlation': pearson_corr,
                'Spearman Correlation': spearman_corr
            }
        else:
            correlation_results[period] = {
                'Pearson Correlation': None,
                'Spearman Correlation': None
            }

    print("\n--- Correlation Results (Node Degree vs DebtRank) ---")
    for period, correlations in correlation_results.items():
        print(f"Period: {period}")
        print(f"  Pearson Correlation: {correlations['Pearson Correlation']}")
        print(f"  Spearman Correlation: {correlations['Spearman Correlation']}")
    
    return correlation_results


node_degrees = calculate_node_degrees(weight_matrices, countries)


correlation_results = calculate_correlation_debtrank_node_degree(all_risk_results, node_degrees, countries)

def calculate_average_correlation(correlation_results):
    pearson_values = []
    spearman_values = []

    for period, correlations in correlation_results.items():
        if correlations['Pearson Correlation'] is not None:
            pearson_values.append(correlations['Pearson Correlation'])
        if correlations['Spearman Correlation'] is not None:
            spearman_values.append(correlations['Spearman Correlation'])

    pearson_avg = np.mean(pearson_values) if pearson_values else None
    spearman_avg = np.mean(spearman_values) if spearman_values else None

    print("\n--- Average Correlation Results ---")
    print(f"Average Pearson Correlation: {pearson_avg:.4f}" if pearson_avg is not None else "No Pearson Correlation data")
    print(f"Average Spearman Correlation: {spearman_avg:.4f}" if spearman_avg is not None else "No Spearman Correlation data")

    return pearson_avg, spearman_avg

average_pearson, average_spearman = calculate_average_correlation(correlation_results)
