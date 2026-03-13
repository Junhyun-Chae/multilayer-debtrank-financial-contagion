
import numpy as np
import matplotlib.pyplot as plt

countries = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
             "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]

multi_risk = np.array([100.1802, 86.4905, 56.7234, 46.7408, 45.5560,
                       34.6600, 33.6248, 32.1996, 31.0465, 27.6865,
                       24.7686, 23.2441, 21.5726, 18.8273, 16.1131,
                       12.9130, 10.9705, 7.9908, 5.4174, 2.3264])

multi_rank_counts = np.array([23, 39, 0, 2, 2,
                              1, 2, 0, 6, 6,
                              3, 0, 0, 1, 9,
                              1, 1, 0, 0, 0])

def minmax(x):
    x = np.asarray(x, float)
    return (x - x.min()) / (x.max() - x.min() + 1e-12)

multi_risk_norm = minmax(multi_risk)

def bubble(counts, emphasize_range=(29, 32), base_scaling=4000, min_size=80):
    if counts.max() == 0:
        return np.full_like(counts, min_size, dtype=float)
    s = np.log1p(counts.astype(float))
    mask = (counts >= emphasize_range[0]) & (counts <= emphasize_range[1])
    s[mask] *= 1.8
    b = base_scaling * s / s.max()
    return np.maximum(b, min_size)

bubble_sizes = bubble(multi_rank_counts)


x = np.arange(len(countries))
plt.figure(figsize=(20, 12))
plt.scatter(x, multi_risk_norm, s=bubble_sizes, alpha=0.8, label="Multi-layer")

plt.xticks(x, countries, rotation=45, fontsize=26)
plt.ylabel("Normalized Risk Score (Multi-layer)", fontsize=30)
plt.xlabel("Countries", fontsize=30)
plt.title("Multi-layer DebtRank (Normalized) with Bubble = Count(≥ 1.0)", fontsize=34, pad=18)
plt.grid(alpha=0.3)
plt.legend(fontsize=20, markerscale=0.6, loc='upper right')

plt.tight_layout()
plt.savefig("multilayer_bubble.png", dpi=300, bbox_inches='tight')
plt.show()






import matplotlib.pyplot as plt
import numpy as np

countries = [
    "GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
    "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"
]

bis_norm = [1.000000,0.978544,0.443732,0.498609,0.606977,0.268437,0.278136,
            0.457839,0.467838,0.482939,0.358730,0.406124,0.239039,0.383803,
            0.209242,0.249572,0.276935,0.234017,0.245219,0.000000]

un_norm = [0.879299,1.000000,0.313043,0.409093,0.621210,0.179164,0.190093,
           0.374856,0.467861,0.521439,0.289562,0.285733,0.182328,0.373930,
           0.184159,0.258612,0.161137,0.069440,0.068632,0.000000]

bis_bubble = [4000.000000,3739.481664,2794.221982,2509.894252,3242.857853,
              2161.905235,2509.894252,3242.857853,2794.221982,3034.617652,
              2794.221982,2161.905235,2161.905235,2794.221982,1713.269364,
              2161.905235,2509.894252,2509.894252,2161.905235,80.000000]

un_bubble = [3169.925001,3169.925001,80.000000,3169.925001,4000.000000,
             80.000000,80.000000,80.000000,2000.000000,2000.000000,
             2000.000000,80.000000,80.000000,2000.000000,80.000000,
             80.000000,80.000000,80.000000,80.000000,80.000000]

x = np.arange(len(countries))
plt.figure(figsize=(20, 12))

plt.scatter(x, bis_norm, s=bis_bubble, c='blue', alpha=0.7, label="BIS Data")
plt.scatter(x, un_norm,  s=un_bubble,  c='orange', alpha=0.7, label="UN Data")

plt.xticks(x, countries, rotation=45, fontsize=20)
plt.ylabel("Normalized Risk Score", fontsize=24)
plt.xlabel("Countries", fontsize=24)
plt.title("BIS vs UN (Values from Console)", fontsize=28, pad=20)
plt.grid(alpha=0.3)
plt.legend(fontsize=18, markerscale=0.6, loc="upper right")

plt.tight_layout()
plt.show()









import matplotlib.pyplot as plt
import numpy as np

countries = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
             "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]

multi_bis_norm = [1.000000,0.978544,0.443732,0.498609,0.606977,0.268437,0.278136,
                  0.457839,0.467838,0.482939,0.358730,0.406124,0.239039,0.383803,
                  0.209242,0.249572,0.276935,0.234017,0.245219,0.000000]

multi_bis_bubble = [4000.000000,3739.481664,2794.221982,2509.894252,3242.857853,
                    2161.905235,2509.894252,3242.857853,2794.221982,3034.617652,
                    2794.221982,2161.905235,2161.905235,2794.221982,1713.269364,
                    2161.905235,2509.894252,2509.894252,2161.905235,80.000000]

x = np.arange(len(countries))
plt.figure(figsize=(20, 12))

plt.scatter(x, multi_bis_norm, s=multi_bis_bubble, c='green', alpha=0.7, label="Multilayer BIS")

plt.xticks(x, countries, rotation=45, fontsize=20)
plt.ylabel("Normalized Risk Score", fontsize=24)
plt.xlabel("Countries", fontsize=24)
plt.title("Multilayer BIS – Normalized Risk", fontsize=28, pad=20)
plt.grid(alpha=0.3)
plt.legend(fontsize=18, markerscale=0.6, loc="upper right")

plt.tight_layout()
plt.show()




import matplotlib.pyplot as plt
import numpy as np

countries = ["GBR","USA","DEU","FRA","ESP","ITA","CHE","JPN","NLD","BEL",
             "IRL","FIN","DNK","SWE","AUT","AUS","CAN","HKG","BRA","CHL"]

orig_countries = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
                  "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]

bis_hits = [44,43,15,24,28,14,13,16,20,19,20,21,14,16,11, 8,12,10, 9,2]
un_hits  = [14,20, 8,10,14, 4, 4, 9, 8, 9, 9, 4, 3, 8, 3, 4, 5, 4, 6,1]

bis_bubble = [3000.000000,2982.289324,2185.054806,2536.770071,2653.738680,
              2134.192518,2079.819792,2232.832581,2399.363573,2360.912438,
              2399.363573,2436.025622,2134.192518,2232.832581,1958.334885,
              1731.614964,2021.415897,1889.761921,1814.648737,865.807482]

un_bubble = [2668.448261,3000.000000,2165.092840,2362.828971,2668.448261,
             1585.901840,1585.901840,2268.912587,2165.092840,2268.912587,
             2268.912587,1585.901840,1366.021492,2165.092840,1366.021492,
             1585.901840,1765.557166,1585.901840,1917.453580,683.010746]

data = {c: (b_h, u_h, b_b, u_b) for c, b_h, u_h, b_b, u_b 
        in zip(orig_countries, bis_hits, un_hits, bis_bubble, un_bubble)}

bis_hits_sorted   = [data[c][0] for c in countries]
un_hits_sorted    = [data[c][1] for c in countries]
bis_bubble_sorted = [data[c][2] for c in countries]
un_bubble_sorted  = [data[c][3] for c in countries]

x = np.arange(len(countries))
plt.figure(figsize=(20, 12))

plt.scatter(x, bis_hits_sorted, s=bis_bubble_sorted, c='red', alpha=0.7, marker='^',label="BIS Layer (≥8% Failures)")
plt.scatter(x, un_hits_sorted,  s=un_bubble_sorted,  c='purple', alpha=0.7, marker='^',label="UN Layer (≥8% Failures)")

plt.xticks(x, countries, rotation=45, fontsize=20)
plt.ylabel("Number of Failures (≥8%)", fontsize=24)
plt.xlabel("Countries", fontsize=24)
plt.title("Threshold Model – BIS vs UN (≥8% Failure)", fontsize=28, pad=20)
plt.grid(alpha=0.3)
plt.legend(fontsize=18, markerscale=0.6, loc="upper right")

plt.tight_layout()
plt.show()
































import numpy as np
import matplotlib.pyplot as plt

countries = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
             "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]
x = np.arange(len(countries))

bis_norm = [1.000000,0.978544,0.443732,0.498609,0.606977,0.268437,0.278136,
            0.457839,0.467838,0.482939,0.358730,0.406124,0.239039,0.383803,
            0.209242,0.249572,0.276935,0.234017,0.245219,0.000000]
un_norm = [0.879299,1.000000,0.313043,0.409093,0.621210,0.179164,0.190093,
           0.374856,0.467861,0.521439,0.289562,0.285733,0.182328,0.373930,
           0.184159,0.258612,0.161137,0.069440,0.068632,0.000000]
bis_bubble = [4000.000000,3739.481664,2794.221982,2509.894252,3242.857853,
              2161.905235,2509.894252,3242.857853,2794.221982,3034.617652,
              2794.221982,2161.905235,2161.905235,2794.221982,1713.269364,
              2161.905235,2509.894252,2509.894252,2161.905235,80.000000]
un_bubble = [3169.925001,3169.925001,80.000000,3169.925001,4000.000000,
             80.000000,80.000000,80.000000,2000.000000,2000.000000,
             2000.000000,80.000000,80.000000,2000.000000,80.000000,
             80.000000,80.000000,80.000000,80.000000,80.000000]

multi_bis_norm = [1.000000,0.978544,0.443732,0.498609,0.606977,0.268437,0.278136,
                  0.457839,0.467838,0.482939,0.358730,0.406124,0.239039,0.383803,
                  0.209242,0.249572,0.276935,0.234017,0.245219,0.000000]
multi_bis_bubble = [4000.000000,3739.481664,2794.221982,2509.894252,3242.857853,
                    2161.905235,2509.894252,3242.857853,2794.221982,3034.617652,
                    2794.221982,2161.905235,2161.905235,2794.221982,1713.269364,
                    2161.905235,2509.894252,2509.894252,2161.905235,80.000000]

bis_hits = [44,43,15,24,28,14,13,16,20,19,20,21,14,16,11, 8,12,10, 9,2]
un_hits  = [14,20, 8,10,14, 4, 4, 9, 8, 9, 9, 4, 3, 8, 3, 4, 5, 4, 6,1]
bis_hits_bubble = [3000.000000,2982.289324,2185.054806,2536.770071,2653.738680,
                   2134.192518,2079.819792,2232.832581,2399.363573,2360.912438,
                   2399.363573,2436.025622,2134.192518,2232.832581,1958.334885,
                   1731.614964,2021.415897,1889.761921,1814.648737,865.807482]
un_hits_bubble = [2668.448261,3000.000000,2165.092840,2362.828971,2668.448261,
                  1585.901840,1585.901840,2268.912587,2165.092840,2268.912587,
                  2268.912587,1585.901840,1366.021492,2165.092840,1366.021492,
                  1585.901840,1765.557166,1585.901840,1917.453580,683.010746]

plt.figure(figsize=(22, 14))

plt.scatter(x, multi_bis_norm, s=multi_bis_bubble, c='green', alpha=0.6,marker='s', label="DebtRank)")
plt.scatter(x, bis_norm, s=bis_bubble, c='blue', alpha=0.6, label="BIS (Debtrank + Threshold BIS)")
plt.scatter(x, un_norm,  s=un_bubble,  c='orange', alpha=0.6, label="UN (Debtrank + Threshold UN)")


bis_hits_norm = np.array(bis_hits) / max(bis_hits)
un_hits_norm  = np.array(un_hits)  / max(un_hits)
plt.scatter(x, bis_hits_norm, s=bis_hits_bubble, c='red', alpha=0.7, marker='^', label="Threshold BIS")
plt.scatter(x, un_hits_norm,  s=un_hits_bubble,  c='purple', alpha=0.7, marker='^', label="Threshold UN")

plt.xticks(x, countries, rotation=45, fontsize=20)
plt.ylabel("Normalized Values (Risk Score)", fontsize=24)
plt.xlabel("Countries", fontsize=24)
plt.title("DebtRank vs BIS vs UN vs Threshold Hits (All in One)", fontsize=30, pad=20)
plt.grid(alpha=0.3)
plt.legend(fontsize=16, markerscale=0.6, loc="upper right")

plt.tight_layout()
plt.show()









####

import numpy as np
import matplotlib.pyplot as plt

countries = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
             "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]

multi_bis_norm = [1.000000,0.978544,0.443732,0.498609,0.606977,0.268437,0.278136,
                  0.457839,0.467838,0.482939,0.358730,0.406124,0.239039,0.383803,
                  0.209242,0.249572,0.276935,0.234017,0.245219,0.000000]


order = np.argsort(multi_bis_norm)[::-1]  
countries = [countries[i] for i in order]

multi_bis_norm = [multi_bis_norm[i] for i in order]
multi_bis_bubble = [multi_bis_bubble[i] for i in order]
bis_norm = [bis_norm[i] for i in order]
un_norm = [un_norm[i] for i in order]
bis_bubble = [bis_bubble[i] for i in order]
un_bubble = [un_bubble[i] for i in order]
bis_hits = [bis_hits[i] for i in order]
un_hits = [un_hits[i] for i in order]
bis_hits_bubble = [bis_hits_bubble[i] for i in order]
un_hits_bubble = [un_hits_bubble[i] for i in order]


x = np.arange(len(countries))
fig, axes = plt.subplots(2, 2, figsize=(24, 14), sharex=True)


axes[0,0].scatter(x, bis_norm, s=bis_bubble, c='blue', alpha=0.7)
axes[0,0].set_title("BIS (DebtRank + Threshold)", fontsize=22)
axes[0,0].set_ylabel("Normalized Risk", fontsize=18)
axes[0,0].grid(alpha=0.3)

axes[0,1].scatter(x, un_norm, s=un_bubble, c='orange', alpha=0.7)
axes[0,1].set_title("UN (DebtRank + Threshold)", fontsize=22)
axes[0,1].grid(alpha=0.3)


axes[1,0].scatter(x, multi_bis_norm, s=multi_bis_bubble, c='green', alpha=0.7, marker='s')
axes[1,0].set_title("DebtRank", fontsize=22)
axes[1,0].set_ylabel("Normalized Risk", fontsize=18)
axes[1,0].grid(alpha=0.3)


axes[1,1].scatter(x, bis_hits, s=bis_hits_bubble, c='red', alpha=0.7, marker='^', label="BIS")
axes[1,1].scatter(x, un_hits,  s=un_hits_bubble,  c='purple', alpha=0.7, marker='^', label="UN")
axes[1,1].set_title("Threshold Model (≥8% Failures)", fontsize=22)
axes[1,1].grid(alpha=0.3)
axes[1,1].legend(fontsize=14)


for ax in axes[1,:]:
    ax.set_xticks(x)
    ax.set_xticklabels(countries, rotation=45, fontsize=14)

plt.suptitle("Comparison: BIS vs UN vs Multilayer vs Threshold", fontsize=28, y=0.98)
plt.tight_layout(rect=[0,0,1,0.96])
plt.show()













####

import matplotlib.pyplot as plt
import numpy as np


countries = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
             "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]

bis_norm = [1.000000,0.978544,0.443732,0.498609,0.606977,0.268437,0.278136,
            0.457839,0.467838,0.482939,0.358730,0.406124,0.239039,0.383803,
            0.209242,0.249572,0.276935,0.234017,0.245219,0.000000]
un_norm = [0.879299,1.000000,0.313043,0.409093,0.621210,0.179164,0.190093,
           0.374856,0.467861,0.521439,0.289562,0.285733,0.182328,0.373930,
           0.184159,0.258612,0.161137,0.069440,0.068632,0.000000]

bis_bubble = [4000.000000,3739.481664,2794.221982,2509.894252,3242.857853,
              2161.905235,2509.894252,3242.857853,2794.221982,3034.617652,
              2794.221982,2161.905235,2161.905235,2794.221982,1713.269364,
              2161.905235,2509.894252,2509.894252,2161.905235,80.000000]
un_bubble = [3169.925001,3169.925001,80.000000,3169.925001,4000.000000,
             80.000000,80.000000,80.000000,2000.000000,2000.000000,
             2000.000000,80.000000,80.000000,2000.000000,80.000000,
             80.000000,80.000000,80.000000,80.000000,80.000000]

order = np.argsort(bis_norm)[::-1]
countries = [countries[i] for i in order]
bis_norm = [bis_norm[i] for i in order]
un_norm = [un_norm[i] for i in order]
bis_bubble = [bis_bubble[i] for i in order]
un_bubble = [un_bubble[i] for i in order]


x = np.arange(len(countries))
plt.figure(figsize=(20, 12))

plt.scatter(x, bis_norm, s=bis_bubble, c='blue', alpha=0.7, label="BIS (DebtRank+Threshold)")
plt.scatter(x, un_norm,  s=un_bubble,  c='orange', alpha=0.7, label="UN (DebtRank+Threshold)")

plt.xticks(x, countries, rotation=45, fontsize=16)
plt.ylabel("Normalized Risk Score", fontsize=20)
plt.xlabel("Countries", fontsize=20)
plt.title("BIS vs UN (DebtRank + Threshold)", fontsize=26, pad=18)
plt.grid(alpha=0.3)
plt.legend(fontsize=16, markerscale=0.6, loc="upper right")

plt.tight_layout()
plt.show()
























import numpy as np
import matplotlib.pyplot as plt


countries = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
             "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]
x = np.arange(len(countries))

bis_norm = [1.000000,0.978544,0.443732,0.498609,0.606977,0.268437,0.278136,
            0.457839,0.467838,0.482939,0.358730,0.406124,0.239039,0.383803,
            0.209242,0.249572,0.276935,0.234017,0.245219,0.000000]
un_norm = [0.879299,1.000000,0.313043,0.409093,0.621210,0.179164,0.190093,
           0.374856,0.467861,0.521439,0.289562,0.285733,0.182328,0.373930,
           0.184159,0.258612,0.161137,0.069440,0.068632,0.000000]
bis_bubble = [4000.000000,3739.481664,2794.221982,2509.894252,3242.857853,
              2161.905235,2509.894252,3242.857853,2794.221982,3034.617652,
              2794.221982,2161.905235,2161.905235,2794.221982,1713.269364,
              2161.905235,2509.894252,2509.894252,2161.905235,80.000000]
un_bubble = [3169.925001,3169.925001,80.000000,3169.925001,4000.000000,
             80.000000,80.000000,80.000000,2000.000000,2000.000000,
             2000.000000,80.000000,80.000000,2000.000000,80.000000,
             80.000000,80.000000,80.000000,80.000000,80.000000]


multi_bis_norm = [1.000000,0.978544,0.443732,0.498609,0.606977,0.268437,0.278136,
                  0.457839,0.467838,0.482939,0.358730,0.406124,0.239039,0.383803,
                  0.209242,0.249572,0.276935,0.234017,0.245219,0.000000]
multi_bis_bubble = [4000.000000,3739.481664,2794.221982,2509.894252,3242.857853,
                    2161.905235,2509.894252,3242.857853,2794.221982,3034.617652,
                    2794.221982,2161.905235,2161.905235,2794.221982,1713.269364,
                    2161.905235,2509.894252,2509.894252,2161.905235,80.000000]


bis_hits = [44,43,15,24,28,14,13,16,20,19,20,21,14,16,11, 8,12,10, 9,2]
un_hits  = [14,20, 8,10,14, 4, 4, 9, 8, 9, 9, 4, 3, 8, 3, 4, 5, 4, 6,1]
bis_hits_bubble = [3000.000000,2982.289324,2185.054806,2536.770071,2653.738680,
                   2134.192518,2079.819792,2232.832581,2399.363573,2360.912438,
                   2399.363573,2436.025622,2134.192518,2232.832581,1958.334885,
                   1731.614964,2021.415897,1889.761921,1814.648737,865.807482]
un_hits_bubble = [2668.448261,3000.000000,2165.092840,2362.828971,2668.448261,
                  1585.901840,1585.901840,2268.912587,2165.092840,2268.912587,
                  2268.912587,1585.901840,1366.021492,2165.092840,1366.021492,
                  1585.901840,1765.557166,1585.901840,1917.453580,683.010746]

order = np.argsort(-np.array(multi_bis_norm)) 
countries = [countries[i] for i in order]
multi_bis_norm = [multi_bis_norm[i] for i in order]
multi_bis_bubble = [multi_bis_bubble[i] for i in order]
bis_norm = [bis_norm[i] for i in order]
bis_bubble = [bis_bubble[i] for i in order]
un_norm = [un_norm[i] for i in order]
un_bubble = [un_bubble[i] for i in order]
bis_hits = [bis_hits[i] for i in order]
bis_hits_bubble = [bis_hits_bubble[i] for i in order]
un_hits = [un_hits[i] for i in order]
un_hits_bubble = [un_hits_bubble[i] for i in order]

x = np.arange(len(countries))

plt.figure(figsize=(22, 14))

plt.scatter(x, multi_bis_norm, s=multi_bis_bubble, c='green', alpha=0.6, marker='s', label="DebtRank")
plt.scatter(x, bis_norm, s=bis_bubble, c='blue', alpha=0.6, label="BIS (DebtRank+Threshold)")
plt.scatter(x, un_norm,  s=un_bubble,  c='orange', alpha=0.6, label="UN (DebtRank+Threshold)")

bis_hits_norm = np.array(bis_hits) / max(bis_hits)
un_hits_norm  = np.array(un_hits)  / max(un_hits)
plt.scatter(x, bis_hits_norm, s=bis_hits_bubble, c='red', alpha=0.7, marker='^', label="Threshold BIS")
plt.scatter(x, un_hits_norm,  s=un_hits_bubble,  c='purple', alpha=0.7, marker='^', label="Threshold UN")

plt.xticks(x, countries, rotation=45, fontsize=20)
plt.ylabel("Normalized Values (Risk Score & Threshold Hits)", fontsize=24)
plt.xlabel("Countries (sorted by Multi-layer BIS Risk)", fontsize=24)
plt.title("DebtRank vs BIS vs UN vs Threshold)", fontsize=30, pad=20)
plt.grid(alpha=0.3)
plt.legend(fontsize=16, markerscale=0.6, loc="upper right")

plt.tight_layout()
plt.show()












import numpy as np
import matplotlib.pyplot as plt

countries = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
             "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]

bis_norm = np.array([1.000000,0.978544,0.443732,0.498609,0.606977,0.268437,0.278136,
                     0.457839,0.467838,0.482939,0.358730,0.406124,0.239039,0.383803,
                     0.209242,0.249572,0.276935,0.234017,0.245219,0.000000])
un_norm = np.array([0.879299,1.000000,0.313043,0.409093,0.621210,0.179164,0.190093,
                    0.374856,0.467861,0.521439,0.289562,0.285733,0.182328,0.373930,
                    0.184159,0.258612,0.161137,0.069440,0.068632,0.000000])
multi_bis_norm = np.array([1.000000,0.978544,0.443732,0.498609,0.606977,0.268437,0.278136,
                           0.457839,0.467838,0.482939,0.358730,0.406124,0.239039,0.383803,
                           0.209242,0.249572,0.276935,0.234017,0.245219,0.000000])

bis_hits = np.array([44,43,15,24,28,14,13,16,20,19,20,21,14,16,11, 8,12,10, 9,2])
un_hits  = np.array([14,20, 8,10,14, 4, 4, 9, 8, 9, 9, 4, 3, 8, 3, 4, 5, 4, 6,1])
multi_bis_hits = bis_hits  

T = 96
bis_thresh_avg = bis_hits / T
un_thresh_avg  = un_hits  / T

plt.figure(figsize=(20, 14))
MARKER_SIZE = 90  

plt.scatter(bis_norm,       bis_hits,       s=MARKER_SIZE, c='blue',   alpha=0.85, label="BIS(DebtRank + Threshold)")
plt.scatter(un_norm,        un_hits,        s=MARKER_SIZE, c='orange', alpha=0.85, label="UN(DebtRank + Threshold)")
plt.scatter(multi_bis_norm, multi_bis_hits, s=MARKER_SIZE, c='green',  alpha=0.85, marker='s', label="DebtRank")

plt.scatter(bis_thresh_avg, bis_hits, s=MARKER_SIZE, c='red',    alpha=0.95, marker='^', label="Threshold BIS")
plt.scatter(un_thresh_avg,  un_hits,  s=MARKER_SIZE, c='purple', alpha=0.95, marker='^', label="Threshold UN")

for i, c in enumerate(countries):
    plt.text(bis_norm[i],       bis_hits[i],       c, fontsize=9, ha='right',  va='bottom', color='blue')
    plt.text(un_norm[i],        un_hits[i],        c, fontsize=9, ha='left',   va='bottom', color='orange')
    plt.text(multi_bis_norm[i], multi_bis_hits[i], c, fontsize=9, ha='center', va='top',    color='green')
    plt.text(bis_thresh_avg[i], bis_hits[i],       c, fontsize=9, ha='right',  va='top',    color='red')
    plt.text(un_thresh_avg[i],  un_hits[i],        c, fontsize=9, ha='left',   va='top',    color='purple')

plt.xlabel("Average Risk Score", fontsize=18)
plt.ylabel("Count of DebtRank == 1", fontsize=18)
plt.title("Country Importance Across Different Risk Models", fontsize=22, pad=16)
plt.xlim(-0.05, 1.05)   # 0~1
plt.grid(alpha=0.3)
plt.legend(fontsize=13)
plt.tight_layout()
plt.show()



















import numpy as np
import matplotlib.pyplot as plt

countries = ["GBR","USA","JPN","FRA","DEU","SWE","FIN","CHE","ITA","ESP",
             "IRL","NLD","CAN","BEL","BRA","AUT","DNK","HKG","AUS","CHL"]

bis_norm = np.array([1.000000,0.978544,0.443732,0.498609,0.606977,0.268437,0.278136,
                     0.457839,0.467838,0.482939,0.358730,0.406124,0.239039,0.383803,
                     0.209242,0.249572,0.276935,0.234017,0.245219,0.000000])
un_norm = np.array([0.879299,1.000000,0.313043,0.409093,0.621210,0.179164,0.190093,
                    0.374856,0.467861,0.521439,0.289562,0.285733,0.182328,0.373930,
                    0.184159,0.258612,0.161137,0.069440,0.068632,0.000000])
multi_bis_norm = np.array(bis_norm)

bis_hits = np.array([44,43,15,24,28,14,13,16,20,19,20,21,14,16,11, 8,12,10, 9,2])
un_hits  = np.array([14,20, 8,10,14, 4, 4, 9, 8, 9, 9, 4, 3, 8, 3, 4, 5, 4, 6,1])
multi_bis_hits = np.array(bis_hits)


T = 96
bis_thresh_norm = bis_hits / T
un_thresh_norm  = un_hits  / T

models = ["BIS(DebtRank + Threshold)", "UN(DebtRank + Threshold)", "DebtRank", "Threshold BIS", "Threshold UN"]

hits_matrix = np.vstack([
    bis_hits,
    un_hits,
    multi_bis_hits,
    bis_hits,
    un_hits
])

norm_matrix = np.vstack([
    bis_norm,
    un_norm,
    multi_bis_norm,
    bis_thresh_norm,
    un_thresh_norm
])

fig, axes = plt.subplots(2, 1, figsize=(22, 10), constrained_layout=True)

im1 = axes[0].imshow(hits_matrix, aspect="auto", cmap="Reds")
axes[0].set_yticks(range(len(models)))
axes[0].set_yticklabels(models, fontsize=12)
axes[0].set_xticks(range(len(countries)))
axes[0].set_xticklabels(countries, rotation=45, fontsize=10)
axes[0].set_title("Heatmap of Hits (Count of DebtRank==1)", fontsize=16)
fig.colorbar(im1, ax=axes[0], orientation="vertical", label="Hits")

im2 = axes[1].imshow(norm_matrix, aspect="auto", cmap="Blues", vmin=0, vmax=1)
axes[1].set_yticks(range(len(models)))
axes[1].set_yticklabels(models, fontsize=12)
axes[1].set_xticks(range(len(countries)))
axes[1].set_xticklabels(countries, rotation=45, fontsize=10)
axes[1].set_title("Heatmap of Average Risk Scores", fontsize=16)
fig.colorbar(im2, ax=axes[1], orientation="vertical", label="Average Risk Score")

plt.show()


