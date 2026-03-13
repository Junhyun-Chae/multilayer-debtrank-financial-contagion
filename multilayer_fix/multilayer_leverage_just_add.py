import pandas as pd

def convert_sheet_name(sheet_name):
    """
    Leverage_2010-01 → Leverage_2010-Q1 형식으로 변환
    """
    if sheet_name.startswith("Leverage_") and '-' in sheet_name:
        year, month = sheet_name.split('_')[1].split('-')
        quarter = (int(month) - 1) // 3 + 1
        return f"Leverage_{year}-Q{quarter}"
    return None

def filter_sheets_starting_from_2000(sheets):
    """
    2000년 1분기 이후의 시트만 필터링
    """
    filtered_sheets = []
    for sheet in sheets:
        if sheet.startswith("Leverage_"):
            year, month = sheet.split('_')[1].split('-')
            if int(year) >= 2000:
                filtered_sheets.append(sheet)
    return filtered_sheets

def add_leverage_matrices_from_2000(unleveraged_file_path, bis_file_path, output_file_path):
    unleveraged_sheets = pd.ExcelFile(unleveraged_file_path).sheet_names
    bis_sheets = pd.ExcelFile(bis_file_path).sheet_names

    unleveraged_sheets = filter_sheets_starting_from_2000(unleveraged_sheets)

    results = {}

    for sheet_name in unleveraged_sheets:
        corresponding_sheet = convert_sheet_name(sheet_name)
        
        if corresponding_sheet and corresponding_sheet in bis_sheets:
            unleveraged_data = pd.read_excel(unleveraged_file_path, sheet_name=sheet_name, header=None)
            bis_data = pd.read_excel(bis_file_path, sheet_name=corresponding_sheet, header=None)

            if unleveraged_data.shape != bis_data.shape:
                print(f"크기 불일치: {sheet_name} ({unleveraged_data.shape})와 {corresponding_sheet} ({bis_data.shape})")
                continue
            
            results[sheet_name] = unleveraged_data + bis_data
        else:
            print(f"시트 {sheet_name}의 대응 시트를 {bis_file_path}에서 찾을 수 없습니다. 건너뜁니다.")

    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        for sheet_name, data in results.items():
            data.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

    print(f"결과가 {output_file_path}에 저장되었습니다.")

unleveraged_file_path = 'UN_debtrank/UN_leverage_and_defaults.xlsx'
bis_file_path = 'BIS_debtrank/BIS_leverage_matrices.xlsx'
output_file_path = 'BIS_debtrank/multilayer_leverage_just_add.xlsx'


add_leverage_matrices_from_2000(unleveraged_file_path, bis_file_path, output_file_path)
