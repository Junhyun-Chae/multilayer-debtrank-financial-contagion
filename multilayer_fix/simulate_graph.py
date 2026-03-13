import pandas as pd
import matplotlib.pyplot as plt


file_path = "multilayersimulate/file_risk_summary.csv"  

df = pd.read_csv(file_path)
df = df.sort_values(by="Max_Countries", ascending=False)


top_5 = df.head(5)
bottom_5 = df.tail(5)

plt.figure(figsize=(10, 6))  
plt.barh(top_5["Source_File"], top_5["Max_Countries"], color='green')  
plt.xlabel("Max Countries")
plt.ylabel("Source File")
plt.title("Top 5 Source Files with Max Countries")
plt.gca().invert_yaxis()  
plt.tight_layout()
plt.savefig("top_5_source_file_vs_max_countries.png")
plt.show()


plt.figure(figsize=(10, 6))  
plt.barh(bottom_5["Source_File"], bottom_5["Max_Countries"], color='red')  
plt.xlabel("Max Countries")
plt.ylabel("Source File")
plt.title("Bottom 5 Source Files with Max Countries")
plt.gca().invert_yaxis()  
plt.tight_layout()
plt.savefig("bottom_5_source_file_vs_max_countries.png")
plt.show()









import pandas as pd
import matplotlib.pyplot as plt

file_path = "multilayersimulate/file_risk_summary.csv"

data = pd.read_csv(file_path)
data['Weight'] = data['Source_File'].str.extract(r'weights_set_(\d+)').astype(int)
data['BIS_LBS_Weight'] = data['Weight'] / 100  

plt.figure(figsize=(14, 8))  
plt.scatter(data['BIS_LBS_Weight'], data['Max_Countries'], alpha=0.7, color='blue', label='Countries count')

real_value = 0.36  
plt.axvline(x=real_value, color='red', linestyle='--', linewidth=1, label=f'x = {real_value}')

plt.text(
    real_value + 0.02, 
    max(data['Max_Countries']) * 0.9, 
    f'Real Value: {real_value}', 
    color='red', 
    fontsize=25,  
    fontweight='bold', 
    rotation=0
)


plt.title('Cross-border Debt Weights vs Trade Weights', fontsize=35)  
plt.xlabel('Trade Weights', fontsize=27)  
plt.ylabel('DebtRank score "1" Countries', fontsize=27)  
plt.legend(
    fontsize=18,  
    markerscale=1.2  
)

plt.grid(True, alpha=0.5)
plt.xticks(fontsize=16)  
plt.yticks(fontsize=16)  

plt.show()
