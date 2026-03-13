import pandas as pd
import matplotlib.pyplot as plt
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



unleveraged_file_path = 'UN_debtrank/UN_leverage_and_defaults.xlsx' 
bis_file_path = 'BIS_debtrank/BIS_leverage_matrices.xlsx'  
weight_file_path = 'multilayer/BIS_UN_multi-layer_weight.xlsx'  
output_file_path = 'multilayer/multilayer_leverage_with_weights.xlsx' 

add_leverage_matrices_with_weights(
    unleveraged_file_path,
    bis_file_path,
    weight_file_path,
    output_file_path
)



import numpy as np
import pandas as pd


leverage_file_path = 'multilayer/multilayer_leverage_with_weights.xlsx'
default_probabilities_file_path = 'default/Default_Probabilities_5Years_Bond.xlsx'
output_excel_file = 'multilayer/BIS_UN_debtrank_with_data.xlsx'


countries = [
    'Austria', 'Australia', 'Belgium', 'Brazil', 'Canada', 'Switzerland', 'Chile', 'Germany',
    'Denmark', 'Spain', 'Finland', 'France', 'United Kingdom', 'Hong Kong', 'Ireland',
    'Italy', 'Netherlands', 'Sweden', 'United States', 'Japan'
]

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
    """
    논문 방식으로 리스크를 전파
    """
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
        if np.all(new_h < threshold):
            print(f"Converged at Step {iteration + 1}")
            break

        h_prev = h.copy()
        h = new_h.copy()

    return risk_history

def calculate_total_risk(risk_history, countries):
    """
    누적 리스크 합산 결과를 기반으로 국가별 순위 계산 및 출력
    """
    total_risk = np.sum(risk_history, axis=0)  
    sorted_risk = sorted(enumerate(total_risk), key=lambda x: x[1], reverse=True)

    print("\nTotal Risk Rankings (Highest Impact):")
    for idx, risk in sorted_risk:
        print(f"{countries[idx]}: {risk:.4f}")

def calculate_risk_for_all_periods(weight_matrices, countries, default_probabilities_file_path, output_file=None):
    """
    모든 기간에 대해 리스크 계산 및 저장
    """
    all_results = {}
    
    if output_file is not None:
        writer = pd.ExcelWriter(output_file)

    for period, weight_matrix in weight_matrices.items():
        print(f"\nCalculating risk for Period: {period}")
        initial_risk = initialize_risk(countries, default_probabilities_file_path, period)

        if np.all(initial_risk == 0):
            print(f"No initial risk for Period: {period}")
            continue

        risk_history = propagate_risk_debtrank(weight_matrix, initial_risk, countries)
        all_results[period] = risk_history

        if output_file is not None:
            initial_risk_df = pd.DataFrame(initial_risk, index=countries, columns=[f"Initial_Risk_{period}"])
            weight_matrix_df = pd.DataFrame(weight_matrix, index=countries, columns=countries)
            risk_history_df = pd.DataFrame(risk_history, columns=countries)

            safe_period = period.replace('/', '_').replace('\\', '_').replace(':', '_')
            initial_risk_df.to_excel(writer, sheet_name=f'Initial_Risk_{safe_period}')
            weight_matrix_df.to_excel(writer, sheet_name=f'Weight_Matrix_{safe_period}')
            risk_history_df.index.name = 'Step'
            risk_history_df.to_excel(writer, sheet_name=f'Risk_History_{safe_period}')

        print(f"\n--- Risk Rankings for Period: {period} ---")
        calculate_total_risk(risk_history, countries)
    
    if output_file is not None:
        writer.close()

    return all_results

weight_matrices = load_leverage_matrices(leverage_file_path, countries)
all_risk_results = calculate_risk_for_all_periods(
    weight_matrices, countries, default_probabilities_file_path, output_excel_file
)

print(f"\nFinal results saved to {output_excel_file}")




import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


country_coords = {
    'Austria': (14.5501, 47.5162), 'Australia': (133.7751, -25.2744), 'Belgium': (4.4699, 50.5039),
    'Brazil': (-51.9253, -14.2350), 'Canada': (-106.3468, 56.1304), 'Switzerland': (8.2275, 46.8182),
    'Chile': (-71.5429, -35.6751), 'Germany': (10.4515, 51.1657), 'Denmark': (9.5018, 56.2639),
    'Spain': (-3.7038, 40.4637), 'Finland': (25.7482, 61.9241), 'France': (2.2137, 46.6034),
    'United Kingdom': (-3.4360, 55.3781), 'Hong Kong': (114.1694, 22.3193), 'Ireland': (-8.2439, 53.4129),
    'Italy': (12.5674, 41.8719), 'Netherlands': (5.2913, 52.1326), 'Sweden': (18.6435, 60.1282),
    'United States': (-95.7129, 37.0902), 'Japan': (138.2529, 36.2048)
}

from matplotlib.colors import Normalize
import matplotlib.colorbar as cbar

def animate_risk_propagation(weight_matrices, countries, default_probabilities_file_path, output_file):
    fig, ax = plt.subplots(figsize=(15, 10))
    m = Basemap(projection='mill', ax=ax)

    all_risk_histories = calculate_risk_for_all_periods(
        weight_matrices, countries, default_probabilities_file_path, None
    )

    for period, weight_matrix in weight_matrices.items():
        max_value = np.max(weight_matrix)
        if max_value > 0:
            weight_matrices[period] = weight_matrix / max_value 
    risk_cmap = plt.cm.Reds
    risk_norm = Normalize(vmin=0, vmax=1) 

    weight_cmap = plt.cm.Blues
    weight_norm = Normalize(vmin=0, vmax=1)  

    risk_cbar_ax = fig.add_axes([0.9, 0.1, 0.02, 0.8])  
    risk_cbar = cbar.ColorbarBase(risk_cbar_ax, cmap=risk_cmap, norm=risk_norm)
    risk_cbar.set_label('Risk Level', fontsize=12)

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
            mean_risk = np.mean(risk_vector)
            normalized_risk = (risk_vector / (mean_risk + 1e-6)) 
            normalized_risk = normalized_risk / np.max(normalized_risk)  
            for i, country in enumerate(countries):
                if country in country_coords:
                    x, y = m(*country_coords[country])
                    ax.plot(
                        x, y, 'o', markersize=10,
                        color=risk_cmap(risk_norm(normalized_risk[i])), alpha=0.8
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
                                arrowstyle='->', color=weight_cmap(weight_norm(weight_matrix[j, i])),
                                lw=line_width, alpha=alpha_value
                            )
                        )
            ax.set_title(f"Period: {current_period}, Step: {step_in_period + 1}", fontsize=16)


        legend_elements = [
            Patch(facecolor='darkred', edgecolor='r', label='High Risk'),
            Patch(facecolor='lightcoral', edgecolor='r', label='Low Risk'),
            Line2D([0], [0], color='blue', lw=2, label='Strong Transmission'),
            Line2D([0], [0], color='lightblue', lw=1, label='Weak Transmission')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

    total_steps = sum(len(history) for history in all_risk_histories.values())
    ani = animation.FuncAnimation(fig, update, frames=total_steps, interval=1000, repeat=False)

    ani.save(output_file, writer=animation.FFMpegWriter(fps=2))
    print(f"Animation saved to {output_file}")
    plt.show()

animation_output_file = 'risk_propagation_animation.mp4'

animate_risk_propagation(
    weight_matrices,
    countries,
    default_probabilities_file_path,
    animation_output_file
)



























































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

country_name_mapping_3char = {
    'Austria': 'AUT', 'Australia': 'AUS', 'Belgium': 'BEL', 'Brazil': 'BRA',
    'Canada': 'CAN', 'Switzerland': 'CHE', 'Chile': 'CHL', 'Germany': 'DEU',
    'Denmark': 'DNK', 'Spain': 'ESP', 'Finland': 'FIN', 'France': 'FRA',
    'United Kingdom': 'GBR', 'Hong Kong': 'HKG', 'Ireland': 'IRL',
    'Italy': 'ITA', 'Netherlands': 'NLD', 'Sweden': 'SWE', 'United States': 'USA',
    'Japan': 'JPN', 'AT': 'AUT', 'AU': 'AUS', 'BE': 'BEL', 'BR': 'BRA',
    'CA': 'CAN', 'CH': 'CHE', 'CL': 'CHL', 'DE': 'DEU', 'DK': 'DNK',
    'ES': 'ESP', 'FI': 'FIN', 'FR': 'FRA', 'GB': 'GBR', 'HK': 'HKG',
    'IE': 'IRL', 'IT': 'ITA', 'NL': 'NLD', 'SE': 'SWE', 'US': 'USA', 'JP': 'JPN'
}

def plot_correlation_with_error_stats(x_data, y_data, labels, x_label, y_label, title, log_scale=False):
    labels = [country_name_mapping_3char.get(label, label) for label in labels]

    if log_scale:
        x_data = np.log10(x_data)
        y_data = np.log10(y_data)
        x_label += " (log10)"
        y_label += " (log10)"

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(x_data, y_data, c='blue', s=100, alpha=0.7, label='Data Points')

    for i, label in enumerate(labels):
        plt.annotate(label, (x_data[i], y_data[i]), fontsize=9, alpha=0.7, textcoords="offset points", xytext=(5, 5))

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
                 fontsize=10, color="blue", textcoords="offset points", xytext=(-50, 20),
                 arrowprops=dict(facecolor='blue', arrowstyle="->", lw=1.5))

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(fontsize=21)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()

    print(f"최대 오차: {max_error:.4f} (국가: {max_error_label})")
    print(f"평균 거리: {mean_error:.4f}")
    print(f"표준 편차: {std_error:.4f}")

if common_countries:
    x_data = [total_leverage[country] for country in common_countries]  
    y_data = [country_risks[country] for country in common_countries]  
    labels = common_countries 

    plot_correlation_with_error_stats(x_data, y_data, labels, "leverage matrix", "DebtRank", "Multi-layer Correlation between Leverage and DebtRank", log_scale=False)
    plot_correlation_with_error_stats(x_data, y_data, labels, "leverage matrix", "DebtRank", "Multi-layer Correlation between Leverage and DebtRank", log_scale=True)












import numpy as np
import matplotlib.pyplot as plt


def select_largest_and_smallest_leverage(weight_matrices, countries):
    leverage_sums = np.zeros(len(countries))
    for matrix in weight_matrices.values():
        leverage_sums += matrix.sum(axis=1)  

    leverage_dict = {countries[i]: leverage_sums[i] for i in range(len(countries))}
    largest_country = max(leverage_dict, key=leverage_dict.get)
    smallest_country = min(leverage_dict, key=leverage_dict.get)

    return largest_country, smallest_country

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
    H = initial_risk_vector.copy()  

    print(f"Initial Risk Vector (h): {h}") 

    for step in range(max_iterations):
        new_h = np.zeros(len(countries))
        for i in range(len(countries)):
            if H[i] >= 1.0:  
                continue
            for j in range(len(countries)):
                if weight_matrix[j, i] > 0:
                    new_h[j] += h[i] * weight_matrix[j, i]
        new_h = np.minimum(new_h, 1.0)
        H = np.minimum(H + new_h, 1.0)

        print(f"Step {step}: Risk Vector (new_h): {new_h}")
        print(f"Step {step}: Cumulative Risk Vector (H): {H}")

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
        print(f"Period {period}: Initial Risk Vector: {initial_risk_vector}")  

        risk_history = simulate_risk_propagation(weight_matrix, initial_risk_vector, countries, max_iterations=max_iterations)

        cumulative_risks_largest[0] += initial_risk_vector[countries.index(largest_country)]
        cumulative_risks_smallest[0] += initial_risk_vector[countries.index(smallest_country)]

        for step in range(1, total_steps):  
            if step < len(risk_history):
                cumulative_risks_largest[step] += risk_history[step][countries.index(largest_country)]
                cumulative_risks_smallest[step] += risk_history[step][countries.index(smallest_country)]

        period_count += 1

    average_risks_largest = cumulative_risks_largest / period_count
    average_risks_smallest = cumulative_risks_smallest / period_count

    print(f"Average Risks (Largest): {average_risks_largest}") 
    print(f"Average Risks (Smallest): {average_risks_smallest}")

    return average_risks_largest, average_risks_smallest








import pandas as pd
import matplotlib.pyplot as plt

def plot_average_risk_propagation(average_risks_largest, average_risks_smallest, largest_country, smallest_country):
    steps = len(average_risks_largest)

    country_name_mapping_3char = {
        'Austria': 'AUT', 'Australia': 'AUS', 'Belgium': 'BEL', 'Brazil': 'BRA',
        'Canada': 'CAN', 'Switzerland': 'CHE', 'Chile': 'CHL', 'Germany': 'DEU',
        'Denmark': 'DNK', 'Spain': 'ESP', 'Finland': 'FIN', 'France': 'FRA',
        'United Kingdom': 'GBR', 'Hong Kong': 'HKG', 'Ireland': 'IRL',
        'Italy': 'ITA', 'Netherlands': 'NLD', 'Sweden': 'SWE', 'United States': 'USA',
        'Japan': 'JPN', 'AT': 'AUT', 'AU': 'AUS', 'BE': 'BEL', 'BR': 'BRA',
        'CA': 'CAN', 'CH': 'CHE', 'CL': 'CHL', 'DE': 'DEU', 'DK': 'DNK',
        'ES': 'ESP', 'FI': 'FIN', 'FR': 'FRA', 'GB': 'GBR', 'HK': 'HKG',
        'IE': 'IRL', 'IT': 'ITA', 'NL': 'NLD', 'SE': 'SWE', 'US': 'USA', 'JP': 'JPN'
    }

    largest_country_iso3 = country_name_mapping_3char.get(largest_country, largest_country)
    smallest_country_iso3 = country_name_mapping_3char.get(smallest_country, smallest_country)

    plt.figure(figsize=(10, 6))
    plt.plot(range(steps), average_risks_largest, label=f"{largest_country_iso3} (Max leverage matrix country)", marker='o')
    plt.plot(range(steps), average_risks_smallest, label=f"{smallest_country_iso3} (Min leverage matrix country)", marker='o', linestyle='--')
    plt.xlabel("Propagation Step")
    plt.ylabel("Average Cumulative Risk")
    plt.legend(fontsize=21)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.savefig("Multi-layer Risk Propagation Simulation: Initial Risk Set to 0.05 for Largest and Smallest Countries, 0 for Others.png", dpi=300, bbox_inches='tight')
    plt.show()

largest_country, smallest_country = select_largest_and_smallest_leverage(weight_matrices, countries)
print(f"레버리지 합이 가장 큰 국가: {largest_country}")
print(f"레버리지 합이 가장 작은 국가: {smallest_country}")

average_risks_largest, average_risks_smallest = simulate_risk_propagation_all_periods(
    weight_matrices,
    countries,
    largest_country,
    smallest_country,
    initial_default_prob=0.05,
    max_iterations=10
)

plot_average_risk_propagation(average_risks_largest, average_risks_smallest, largest_country, smallest_country)






















from scipy.stats import pearsonr, spearmanr
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

def calculate_correlation(all_risk_results, default_probabilities_file_path, node_degrees, countries):
    default_probabilities_df = pd.read_excel(default_probabilities_file_path)
    correlation_results = {
        'Node Degree': [],
        'Default Probability': []
    }

    for period, risk_history in all_risk_results.items():
        final_risk_vector = risk_history[-1]
        
        period_data = default_probabilities_df[default_probabilities_df['Year_Quarter'] == period]
        if period_data.empty:
            continue

        node_degree_values = node_degrees.get(period, [])
        default_probabilities = []
        risk_values = []

        for i, country in enumerate(countries):
            country_name = country  
            risk_values.append(final_risk_vector[i])
            prob = period_data[period_data['Country'] == country]['Default_Probability'].values
            if prob.size > 0:
                default_probabilities.append(prob[0])

        valid_node_degrees = [node_degree_values[i] for i in range(len(node_degree_values)) if risk_values[i] != 0]
        valid_risk_values = [risk_values[i] for i in range(len(risk_values)) if risk_values[i] != 0]

        if valid_node_degrees and len(set(valid_node_degrees)) > 1:  
            try:
                pearson_node, _ = pearsonr(valid_node_degrees, valid_risk_values)
                spearman_node, _ = spearmanr(valid_node_degrees, valid_risk_values)
                correlation_results['Node Degree'].append((pearson_node, spearman_node))
            except ValueError:
                correlation_results['Node Degree'].append((None, None))
        else:
            correlation_results['Node Degree'].append((None, None))

        if default_probabilities and len(set(default_probabilities)) > 1:  
            try:
                pearson_default, _ = pearsonr(default_probabilities, risk_values)
                spearman_default, _ = spearmanr(default_probabilities, risk_values)
                correlation_results['Default Probability'].append((pearson_default, spearman_default))
            except ValueError:
                correlation_results['Default Probability'].append((None, None))
        else:
            correlation_results['Default Probability'].append((None, None))

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


def calculate_node_degrees(weight_matrices, countries):
    node_degrees = {}
    for period, weight_matrix in weight_matrices.items():
        degree_counts = [np.count_nonzero(weight_matrix[:, i]) for i in range(len(countries))]
        node_degrees[period] = degree_counts
    return node_degrees

node_degrees = calculate_node_degrees(weight_matrices, countries)
correlation_results = calculate_correlation(all_risk_results, default_probabilities_file_path, node_degrees, countries)
average_correlations = calculate_average_correlation(correlation_results)

print("\n--- Average Correlation Results ---")
for key, averages in average_correlations.items():
    print(f"\n{key}:")
    print(f"  Average Pearson Correlation: {averages['Average Pearson']:.4f}" if averages['Average Pearson'] is not None else "  Average Pearson Correlation: None")
    print(f"  Average Spearman Correlation: {averages['Average Spearman']:.4f}" if averages['Average Spearman'] is not None else "  Average Spearman Correlation: None")
correlation_results = calculate_correlation(all_risk_results, default_probabilities_file_path, node_degrees, countries)
average_correlations = calculate_average_correlation(correlation_results)


print("\n--- Average Correlation Results ---")
for key, averages in average_correlations.items():
    print(f"\n{key}:")
    print(f"  Average Pearson Correlation: {averages['Average Pearson']:.4f}" if averages['Average Pearson'] is not None else "  Average Pearson Correlation: None")
    print(f"  Average Spearman Correlation: {averages['Average Spearman']:.4f}" if averages['Average Spearman'] is not None else "  Average Spearman Correlation: None")
