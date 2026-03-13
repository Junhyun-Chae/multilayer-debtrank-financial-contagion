import pandas as pd

layer_files = {
    'BIS': 'BIS_debtrank/one_countries_fx_c.xlsx',  
    'UN': 'UN_debtrank//one_countries_e_c.csv'    
}

def format_date_bis_to_quarter(date_str):
    return date_str.strip()

def format_date_un_to_quarter(date_str):
    year = date_str[:4]
    month = int(date_str[4:6])
    quarter = (month - 1) // 3 + 1
    return f"{year}-Q{quarter}"

def calculate_layer_weights_by_date(layer_files):
    layer_dataframes = {}

    for layer_name, file_path in layer_files.items():
        if layer_name == 'BIS':
            data = pd.read_excel(file_path, sheet_name='Aggregated Data')
            transaction_column = 'OBS_VALUEObservation Value'

            data[transaction_column] = (
                pd.to_numeric(data[transaction_column], errors='coerce')
                .fillna(0).abs() * 10**5
            )
            data['Standard_Date'] = data['TIME_PERIODTime period or range'].apply(format_date_bis_to_quarter)

            grouped_data = (
                data.groupby('Standard_Date')[transaction_column]
                .sum()
                .reset_index()
                .rename(columns={transaction_column: f'{layer_name}_Total'})
            )
        elif layer_name == 'UN':

            data = pd.read_csv(file_path)
            transaction_column = 'primaryValue'

            data[transaction_column] = pd.to_numeric(data[transaction_column], errors='coerce').fillna(0).abs()

            data['Standard_Date'] = data['period'].astype(str).apply(format_date_un_to_quarter)
            grouped_data = (
                data.groupby('Standard_Date')[transaction_column]
                .sum()
                .reset_index()
                .rename(columns={transaction_column: f'{layer_name}_Total'})
            )
        else:
            raise ValueError(f"Unsupported layer: {layer_name}")

        layer_dataframes[layer_name] = grouped_data

    merged_data = None
    for layer_name, df in layer_dataframes.items():
        if merged_data is None:
            merged_data = df
        else:
            merged_data = pd.merge(merged_data, df, how='outer', on='Standard_Date')

    merged_data.fillna(0, inplace=True)
    merged_data['Total_All_Layers'] = merged_data[
        [f'{layer_name}_Total' for layer_name in layer_files]
    ].sum(axis=1)

    for layer_name in layer_files:
        merged_data[f'{layer_name}_Weight'] = (
            merged_data[f'{layer_name}_Total'] / merged_data['Total_All_Layers']
        )

    return merged_data

layer_weights = calculate_layer_weights_by_date(layer_files)

print(layer_weights)


layer_weights.to_excel('multilayer/BIS_UN_multi-layer_weight.xlsx', index=False)
print("Layer weights by quarter saved to 'BIS_UN_multi-layer_weight.xlsx'")
