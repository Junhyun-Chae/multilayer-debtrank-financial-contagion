import pandas as pd

file_path = 'UN_debtrank/UNdata_merged_file.csv'  

df = pd.read_csv(file_path, encoding='ISO-8859-1')  
exclude_columns = ['cifvalue', 'fobvalue', 'primaryValue']
df_filtered = df.drop(columns=exclude_columns, errors='ignore')  
unique_values_per_column = df_filtered.apply(lambda x: pd.unique(x.dropna()))

unique_values_df = pd.DataFrame({
    'Column': unique_values_per_column.index,
    'UniqueValues': unique_values_per_column.apply(lambda x: ', '.join(map(str, x)))  
})

output_file = 'UN_debtrank/unique_values_per_column.csv'
unique_values_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"유니크 값이 {output_file}에 저장되었습니다.")
