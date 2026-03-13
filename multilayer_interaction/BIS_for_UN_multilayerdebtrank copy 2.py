

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib import animation
from adjustText import adjust_text

plt.rcParams["font.family"] = "DejaVu Sans"  
plt.rcParams["axes.unicode_minus"] = False


from BIS_UN_debtrank_0513copyBISonly import (  
    load_dataset_bis,
    load_dataset_un,
    initialise_risk_vector,
)


ISO2_TO_3 = {
    "AU": "AUS", "AT": "AUT", "BE": "BEL", "BR": "BRA", "CA": "CAN",
    "CH": "CHE", "CL": "CHL", "DE": "DEU", "DK": "DNK", "ES": "ESP",
    "FI": "FIN", "FR": "FRA", "GB": "GBR", "HK": "HKG", "IE": "IRL",
    "IT": "ITA", "JP": "JPN", "NL": "NLD", "SE": "SWE", "US": "USA",
}
ISO3_TO_2 = {v: k for k, v in ISO2_TO_3.items()}

COUNTRY_COORDS = {
    "AUS": (133.7751, -25.2744), "AUT": (14.5501, 47.5162), "BEL": (4.4699, 50.5039),
    "BRA": (-51.9253, -14.2350), "CAN": (-106.3468, 56.1304), "CHE": (8.2275, 46.8182),
    "CHL": (-71.5429, -35.6751), "DEU": (10.4515, 51.1657), "DNK": (9.5018, 56.2639),
    "ESP": (-3.7038, 40.4637),  "FIN": (25.7482, 61.9241), "FRA": (2.2137, 46.6034),
    "GBR": (-3.4360, 55.3781), "HKG": (114.1694, 22.3193), "IRL": (-8.2439, 53.4129),
    "ITA": (12.5674, 41.8719), "JPN": (138.2529, 36.2048), "NLD": (5.2913, 52.1326),
    "SWE": (18.6435, 60.1282), "USA": (-95.7129, 37.0902),
}

def propagate_multilayer(
    W_bis: np.ndarray,
    W_un: np.ndarray,
    h0_bis: np.ndarray,
    h0_un: np.ndarray,
    vertical_alpha: float = 0.05,
    vertical_threshold: float = 0.5,
    max_iter: int = 30,
    eps: float = 1e-3,
):
    h_prev_bis = np.zeros_like(h0_bis)
    h_prev_un  = np.zeros_like(h0_un)
    h_bis = h0_bis.copy();  h_un = h0_un.copy()
    H_bis = h0_bis.copy();  H_un = h0_un.copy()

    history_bis: list[np.ndarray] = []
    history_un:  list[np.ndarray] = []

    for _ in range(max_iter):
        delta_bis = np.maximum(0, h_bis - h_prev_bis)
        new_h_bis = (W_bis @ delta_bis).clip(0, 1)
        H_bis = np.minimum(H_bis + new_h_bis, 1)
        mask_bis = H_bis >= vertical_threshold
        vtrans_bis = vertical_alpha * H_bis * mask_bis.astype(float)
        new_h_un_from_bis = np.minimum(vtrans_bis, 1 - H_un)

        history_bis.append(H_bis.copy())

        delta_un = np.maximum(0, h_un - h_prev_un)
        new_h_un = (W_un @ delta_un).clip(0, 1)
        new_h_un = np.minimum(new_h_un + new_h_un_from_bis, 1)
        H_un = np.minimum(H_un + new_h_un, 1)

        mask_un = H_un >= vertical_threshold
        vtrans_un = vertical_alpha * H_un * mask_un.astype(float)
        new_h_bis_from_un = np.minimum(vtrans_un, 1 - H_bis)
        new_h_bis = np.minimum(new_h_bis + new_h_bis_from_un, 1)
        H_bis = np.minimum(H_bis + new_h_bis_from_un, 1)

        history_un.append(H_un.copy())

        if np.all(new_h_bis < eps) and np.all(new_h_un < eps):
            break

        h_prev_bis, h_bis = h_bis, new_h_bis
        h_prev_un,  h_un  = h_un,  new_h_un

    return history_bis, history_un


def plot_static_map(risk_vec: np.ndarray, iso2_list: list[str],
                    out_path: Path, title: str = "") -> None:
    fig, ax = plt.subplots(figsize=(15, 10))
    m = Basemap(projection="mill", llcrnrlon=-150, llcrnrlat=-60,
                urcrnrlon=160, urcrnrlat=80, resolution="c", ax=ax)
    m.drawcoastlines(linewidth=.4, color="lightgray")
    m.drawcountries(linewidth=.4, color="lightgray")

    texts = []
    vmax = risk_vec.max() if risk_vec.max() > 0 else 1.0
    for iso2, h in zip(iso2_list, risk_vec):
        iso3 = ISO2_TO_3[iso2]
        lon, lat = COUNTRY_COORDS[iso3]
        x, y = m(lon, lat)
        size = 50 + 800 * (h / vmax)
        color = plt.cm.Reds(h / vmax)
        m.scatter(x, y, s=size, color=color, alpha=.85, edgecolor="k", linewidth=.3)
        texts.append(ax.text(x, y, iso3, fontsize=9, ha="center", va="center"))

    adjust_text(texts, arrowprops=dict(arrowstyle="-", color="gray", lw=.4))
    ax.set_title(title, fontsize=16)
    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def make_animation(history: list[np.ndarray], iso2_list: list[str],
                   out_mp4: Path, title: str = "") -> None:
    fig, ax = plt.subplots(figsize=(15, 10))
    m = Basemap(projection="mill", llcrnrlon=-150, llcrnrlat=-60,
                urcrnrlon=160, urcrnrlat=80, resolution="c", ax=ax)
    m.drawcoastlines(linewidth=.4, color="lightgray")
    m.drawcountries(linewidth=.4, color="lightgray")

    scat = m.scatter([], [], s=[], c=[], alpha=.85)
    vmax_global = max(np.max(step) for step in history)

    def init():
        scat.set_offsets(np.empty((0, 2)))
        scat.set_sizes([])        
        scat.set_array(np.array([]))
        ax.set_title(title)
        return scat,

    def update(frame):
        h = history[frame]
        lons, lats = zip(*(COUNTRY_COORDS[ISO2_TO_3[i]] for i in iso2_list))
        xs, ys = m(lons, lats)
        scat.set_offsets(np.c_[xs, ys])
        scat.set_sizes(50 + 800 * (h / vmax_global))
        scat.set_array(h / vmax_global)
        ax.set_title(f"{title} – step {frame}")
        return scat,

    ani = animation.FuncAnimation(fig, update, frames=len(history),
                                  init_func=init, blit=False)
    ani.save(out_mp4, dpi=200, fps=2)
    plt.close(fig)


def run_multilayer(
    base_dir: Path,
    default_file: Path,
    out_dir: Path,
    vertical_alpha: float,
    vertical_threshold: float,
    max_iter: int,
):
    out_dir.mkdir(parents=True, exist_ok=True)

    WM_bis, countries_bis, name_map_bis, coords_bis, periods_bis = load_dataset_bis(base_dir)
    WM_un,  countries_un, name_map_un,  coords_un,  periods_un  = load_dataset_un(base_dir)

    iso2_to_name = name_map_bis                   
    name_to_iso3 = {v: k for k, v in name_map_un.items()} 
    common_iso2 = [iso for iso, name in iso2_to_name.items() if name in name_to_iso3]

    periods_bis_ts = pd.PeriodIndex(periods_bis, freq="Q").to_timestamp()
    common_periods = sorted(set(periods_bis_ts) & set(periods_un))
    print("▶ common ISO2:", common_iso2)
    print("▶ common periods:", common_periods)

    bis_str_to_mat = WM_bis
    WM_bis = {}
    for ts in common_periods:
        bis_key = f"{ts.year}-Q{ts.quarter}"
        WM_bis[ts] = bis_str_to_mat[bis_key]

    WM_un_mat = {}
    for p in common_periods:
        orig = WM_un[p]
        N = len(common_iso2)
        mat = np.zeros((N, N))
        for i, iso2_i in enumerate(common_iso2):
            iso3_i = name_to_iso3[iso2_to_name[iso2_i]]
            idx_i3 = countries_un.index(iso3_i)
            for j, iso2_j in enumerate(common_iso2):
                iso3_j = name_to_iso3[iso2_to_name[iso2_j]]
                idx_j3 = countries_un.index(iso3_j)
                mat[j, i] = orig[idx_j3, idx_i3]
        WM_un_mat[p] = mat

    countries = common_iso2
    WM_un  = WM_un_mat

    default_df = pd.read_excel(default_file)
    default_df["Year_Quarter"] = pd.PeriodIndex(default_df["Year_Quarter"], freq="Q").to_timestamp()

    results_bis: dict[pd.Timestamp, list[np.ndarray]] = {}
    results_un:  dict[pd.Timestamp, list[np.ndarray]] = {}

    for per in common_periods:
        h0_bis = initialise_risk_vector(countries_bis, name_map_bis, default_df, per)
        h0_un  = initialise_risk_vector(countries_un,  name_map_un,  default_df, per)
        hist_bis, hist_un = propagate_multilayer(
            WM_bis[per], WM_un[per], h0_bis, h0_un,
            vertical_alpha, vertical_threshold, max_iter
        )
        results_bis[per] = hist_bis
        results_un[per]  = hist_un

    with pd.ExcelWriter(out_dir / "multilayer_results_BIS.xlsx") as writer:
        for per, hist in results_bis.items():
            pd.DataFrame(hist, columns=countries).to_excel(writer, sheet_name=f"{per.year}-Q{per.quarter}")
    with pd.ExcelWriter(out_dir / "multilayer_results_UN.xlsx") as writer:
        for per, hist in results_un.items():
            pd.DataFrame(hist, columns=countries).to_excel(writer, sheet_name=f"{per.year}-Q{per.quarter}")

    print(f"📓 Multilayer results saved in {out_dir}")

    map_dir = out_dir / "maps"
    map_dir.mkdir(exist_ok=True)

    for per in common_periods:

        last_bis = np.array(results_bis[per][-1])
        last_un  = np.array(results_un[per][-1])
        last_avg = (last_bis + last_un) / 2

        plot_static_map(last_bis,  countries,
                        map_dir / f"map_bis_{per.year}Q{per.quarter}.png",
                        title=f"BIS Risk {per.year}-Q{per.quarter}")
        plot_static_map(last_un,   countries,
                        map_dir / f"map_un_{per.year}Q{per.quarter}.png",
                        title=f"UN  Risk {per.year}-Q{per.quarter}")
        plot_static_map(last_avg,  countries,
                        map_dir / f"map_avg_{per.year}Q{per.quarter}.png",
                        title=f"Multi‑layer Avg Risk {per.year}-Q{per.quarter}")

        make_animation(results_bis[per], countries,
                       map_dir / f"anim_bis_{per.year}Q{per.quarter}.mp4",
                       title=f"BIS Risk Propagation {per.year}-Q{per.quarter}")
        make_animation(results_un[per],  countries,
                       map_dir / f"anim_un_{per.year}Q{per.quarter}.mp4",
                       title=f"UN  Risk Propagation {per.year}-Q{per.quarter}")

    print(f"🗺️  Maps & animations saved in {map_dir}")



def parse_args():
    p = argparse.ArgumentParser(description="Multi‑layer DebtRank (BIS ↔ UN)")
    p.add_argument("--base-dir", default="./", type=Path)
    p.add_argument("--default-file", default="./default/Default_Probabilities_5Years_Bond.xlsx", type=Path)
    p.add_argument("--out-dir", default="./output", type=Path)
    p.add_argument("--vertical-alpha", type=float, default=0.05, help="수직 전이 강도 α")
    p.add_argument("--vertical-threshold", type=float, default=0.5, help="수직 전이 임계값 θ")
    p.add_argument("--max-iter", type=int, default=20, help="최대 전파 스텝 수")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_multilayer(
        base_dir=args.base_dir,
        default_file=args.default_file,
        out_dir=args.out_dir,
        vertical_alpha=args.vertical_alpha,
        vertical_threshold=args.vertical_threshold,
        max_iter=args.max_iter,
    )


##./output/multilayer_results_BIS.xlsx
##./output/multilayer_results_UN.xlsx