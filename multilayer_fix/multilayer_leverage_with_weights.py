import pandas as pd

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
