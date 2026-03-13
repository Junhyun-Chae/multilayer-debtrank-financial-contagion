import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

output_directory = 'multilayer/risk_results'
os.makedirs(output_directory, exist_ok=True)

countries = [
    'Austria', 'Australia', 'Belgium', 'Brazil', 'Canada', 'Switzerland', 'Chile', 'Germany',
    'Denmark', 'Spain', 'Finland', 'France', 'United Kingdom', 'Hong Kong', 'Ireland',
    'Italy', 'Netherlands', 'Sweden', 'United States', 'Japan'
]
def convert_sheet_name_to_period(sheet_name):
    if sheet_name.startswith("Weight_Matrix_"):
        try:
            # 'Weight_Matrix_' 이후의 문자열 추출
            date_part = sheet_name[len("Weight_Matrix_"):]
            year, quarter = date_part.split('-Q')
            return f"{year}-Q{quarter}"
        except ValueError:
            print(f"Unexpected sheet name format: {sheet_name}")
            return None
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

    for _ in range(max_iterations):
        new_h = np.zeros(len(countries))
        for i in range(len(countries)):
            if H[i] >= 1.0:
                continue
            for j in range(len(countries)):
                if weight_matrix[j, i] > 0:
                    delta_risk = max(0, h[i] - h_prev[i])
                    new_h[j] += delta_risk * weight_matrix[j, i]
        new_h = np.minimum(new_h, 1.0)
        H = np.minimum(H + new_h, 1.0)
        risk_history.append(H.copy())
        if np.all(new_h < threshold):
            break
        h_prev = h.copy()
        h = new_h.copy()
    return risk_history

def calculate_risk_for_all_periods(weight_matrices, countries, default_probabilities_file_path):
    all_results = {}
    for period, weight_matrix in weight_matrices.items():
        initial_risk = initialize_risk(countries, default_probabilities_file_path, period)
        if np.all(initial_risk == 0):
            continue
        risk_history = propagate_risk_debtrank(weight_matrix, initial_risk, countries)
        all_results[period] = risk_history
    return all_results


def calculate_total_leverage(weight_matrices, countries):
    total_leverage = {country: 0 for country in countries}
    for weight_matrix in weight_matrices.values():
        for i, country in enumerate(countries):
            total_leverage[country] += np.sum(weight_matrix[i])
    return total_leverage


def plot_correlation_with_error_stats(x_data, y_data, labels, x_label, y_label, title, log_scale=False):
    if log_scale:
        x_data = np.log10(x_data)
        y_data = np.log10(y_data)
        x_label += " (log10)"
        y_label += " (log10)"

    plt.figure(figsize=(10, 6))
    plt.scatter(x_data, y_data, c='blue', s=100, alpha=0.7, label='Data Points')

    for i, label in enumerate(labels):
        plt.annotate(label, (x_data[i], y_data[i]), fontsize=9, alpha=0.7, textcoords="offset points", xytext=(5, 5))

    coeffs = np.polyfit(x_data, y_data, 1)
    trendline = np.poly1d(coeffs)
    plt.plot(x_data, trendline(x_data), color='red', label=f"Trendline: y={coeffs[0]:.2f}x + {coeffs[1]:.2f}")

    errors = np.abs(y_data - trendline(x_data))
    max_error = np.max(errors)
    mean_error = np.mean(errors)
    std_error = np.std(errors)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()

    print(f"최대 오차: {max_error:.4f}, 평균 거리: {mean_error:.4f}, 표준 편차: {std_error:.4f}")

def filter_common_countries(data_dict1, data_dict2, country_list):
    return [country for country in country_list if country in data_dict1 and country in data_dict2]


def calculate_and_plot_correlation_for_all_files(leverage_file_paths, countries, default_probabilities_file_path):
    for leverage_file_path in leverage_file_paths:
        print(f"\nProcessing file: {leverage_file_path}")
        weight_matrices = load_leverage_matrices(leverage_file_path, countries)
        all_risk_results = calculate_risk_for_all_periods(weight_matrices, countries, default_probabilities_file_path)
        total_leverage = calculate_total_leverage(weight_matrices, countries)
        country_risks = {
            country: sum(np.sum(history, axis=0)[idx] for history in all_risk_results.values())
            for idx, country in enumerate(countries)
        }
        common_countries = filter_common_countries(total_leverage, country_risks, countries)

        if common_countries:
            x_data = [total_leverage[country] for country in common_countries]
            y_data = [country_risks[country] for country in common_countries]
            labels = common_countries

            plot_correlation_with_error_stats(
                x_data, y_data, labels,
                "Leverage Matrix (Total)", "DebtRank",
                f"Correlation for {os.path.basename(leverage_file_path)}",
                log_scale=False
            )

            plot_correlation_with_error_stats(
                x_data, y_data, labels,
                "Leverage Matrix (Total)", "DebtRank",
                f"Log-transformed Correlation for {os.path.basename(leverage_file_path)}",
                log_scale=True
            )

leverage_file_paths = [f'multilayersimulate/results_with_weights_set_{i}.xlsx' for i in range(1, 102)]
default_probabilities_file_path = 'default/Default_Probabilities_5Years_Bond.xlsx'
calculate_and_plot_correlation_for_all_files(leverage_file_paths, countries, default_probabilities_file_path)
excel_file = pd.ExcelFile(leverage_file_paths[0])
print(excel_file.sheet_names)


