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
    total_risk = np.sum(risk_history, axis=0)  
    sorted_risk = sorted(enumerate(total_risk), key=lambda x: x[1], reverse=True)

    print("\nTotal Risk Rankings (Highest Impact):")
    for idx, risk in sorted_risk:
        print(f"{countries[idx]}: {risk:.4f}")


def calculate_risk_for_all_periods(weight_matrices, countries, default_probabilities_file_path, output_file):
    all_results = {}
    
    with pd.ExcelWriter(output_file) as writer:
        for period, weight_matrix in weight_matrices.items():
            print(f"\nCalculating risk for Period: {period}")
            initial_risk = initialize_risk(countries, default_probabilities_file_path, period)

            if np.all(initial_risk == 0):
                print(f"No initial risk for Period: {period}")
                continue

            risk_history = propagate_risk_debtrank(weight_matrix, initial_risk, countries)
            all_results[period] = risk_history

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
    
    return all_results

weight_matrices = load_leverage_matrices(leverage_file_path, countries)

all_risk_results = calculate_risk_for_all_periods(
    weight_matrices, countries, default_probabilities_file_path, output_excel_file
)

print(f"\nFinal results saved to {output_excel_file}")




























