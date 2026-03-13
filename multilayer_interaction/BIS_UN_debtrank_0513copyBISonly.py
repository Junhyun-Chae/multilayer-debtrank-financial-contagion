
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap  
import matplotlib.animation as animation  

plt.rcParams.update({
    "font.size": 18,
    "legend.fontsize": 18,
})


COUNTRY_META_BIS = {
    "codes": [
        "AT", "AU", "BE", "BR", "CA", "CH", "CL", "DE", "DK", "ES",
        "FI", "FR", "GB", "HK", "IE", "IT", "NL", "SE", "US", "JP",
    ],
    "name_map": {
        "AT": "Austria", "AU": "Australia", "BE": "Belgium", "BR": "Brazil",
        "CA": "Canada", "CH": "Switzerland", "CL": "Chile", "DE": "Germany",
        "DK": "Denmark", "ES": "Spain", "FI": "Finland", "FR": "France",
        "GB": "United Kingdom", "HK": "Hong Kong", "IE": "Ireland",
        "IT": "Italy", "NL": "Netherlands", "SE": "Sweden",
        "US": "United States", "JP": "Japan",
    },
}

COUNTRY_META_UN = {
    "codes": [
        "AUT", "AUS", "BEL", "BRA", "CAN", "CHE", "CHL", "DEU", "DNK", "ESP",
        "FIN", "FRA", "GBR", "HKG", "IRL", "ITA", "NLD", "SWE", "USA", "JPN",
    ],
    "name_map": {
        "AUT": "Austria", "AUS": "Australia", "BEL": "Belgium", "BRA": "Brazil",
        "CAN": "Canada", "CHE": "Switzerland", "CHL": "Chile", "DEU": "Germany",
        "DNK": "Denmark", "ESP": "Spain", "FIN": "Finland", "FRA": "France",
        "GBR": "United Kingdom", "HKG": "Hong Kong", "IRL": "Ireland",
        "ITA": "Italy", "NLD": "Netherlands", "SWE": "Sweden",
        "USA": "United States", "JPN": "Japan",
    },
}

COORDS_GENERIC = {
    "Austria": (14.5501, 47.5162),
    "Australia": (133.7751, -25.2744),
    "Belgium": (4.4699, 50.5039),
    "Brazil": (-51.9253, -14.2350),
    "Canada": (-106.3468, 56.1304),
    "Switzerland": (8.2275, 46.8182),
    "Chile": (-71.5429, -35.6751),
    "Germany": (10.4515, 51.1657),
    "Denmark": (9.5018, 56.2639),
    "Spain": (-3.7038, 40.4637),
    "Finland": (25.7482, 61.9241),
    "France": (2.2137, 46.6034),
    "United Kingdom": (-3.4360, 55.3781),
    "Hong Kong": (114.1694, 22.3193),
    "Ireland": (-8.2439, 53.4129),
    "Italy": (12.5674, 41.8719),
    "Netherlands": (5.2913, 52.1326),
    "Sweden": (18.6435, 60.1282),
    "United States": (-95.7129, 37.0902),
    "Japan": (138.2529, 36.2048),
}


def _ensure_outdir(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)


def _normalise_weight_matrix(wm: np.ndarray) -> np.ndarray:
    max_val = wm.max()
    return wm if max_val == 0 else wm / max_val

def load_dataset_bis(base_dir: Path) -> tuple[
    dict[str, np.ndarray], list[str], dict[str, str], dict[str, tuple[float, float]], list[str]
]:
    all_countries_file = base_dir / "BIS_debtrank" / "all_countries_fx_c.xlsx"
    one_country_file = base_dir / "BIS_debtrank" / "one_countries_fx_c.xlsx"

    all_df = pd.read_excel(all_countries_file, sheet_name="Aggregated Data")
    one_df = pd.read_excel(one_country_file, sheet_name="Aggregated Data")

    all_df.columns = all_df.columns.str.strip()
    one_df.columns = one_df.columns.str.strip()

    all_df["L_REP_CTYReporting country"] = all_df["L_REP_CTYReporting country"].str.split(":").str[0].str.strip()
    all_df["L_CP_COUNTRYCounterparty country"] = all_df["L_CP_COUNTRYCounterparty country"].str.split(":").str[0].str.strip()
    one_df["L_REP_CTYReporting country"] = one_df["L_REP_CTYReporting country"].str.split(":").str[0].str.strip()
    one_df["L_CP_COUNTRYCounterparty country"] = one_df["L_CP_COUNTRYCounterparty country"].str.split(":").str[0].str.strip()

    countries = COUNTRY_META_BIS["codes"]

    all_c = (
        all_df.groupby(["L_REP_CTYReporting country", "TIME_PERIODTime period or range"])[
            "OBS_VALUEObservation Value"
        ].first().reset_index().rename(columns={"OBS_VALUEObservation Value": "TotalGiven"})
    )

    one_df = one_df[one_df["L_REP_CTYReporting country"].isin(all_c["L_REP_CTYReporting country"]) ]

    one_c = (
        one_df.groupby([
            "L_REP_CTYReporting country", "L_CP_COUNTRYCounterparty country", "TIME_PERIODTime period or range"
        ])["OBS_VALUEObservation Value"].first().reset_index().rename(columns={"OBS_VALUEObservation Value": "GivenToCp"})
    )

    merged = pd.merge(
        one_c,
        all_c,
        on=["L_REP_CTYReporting country", "TIME_PERIODTime period or range"],
        how="left",
    )
    merged["Leverage"] = merged.apply(
        lambda r: 0 if r.TotalGiven == 0 else r.GivenToCp / r.TotalGiven,
        axis=1,
    )

    merged = merged[(merged["TIME_PERIODTime period or range"] >= "2000-Q1") & (merged["TIME_PERIODTime period or range"] <= "2023-Q4")]

    periods = sorted(merged["TIME_PERIODTime period or range"].unique())

    weight_matrices: dict[str, np.ndarray] = {}
    for p in periods:
        data_p = merged[merged["TIME_PERIODTime period or range"] == p]
        wm = np.zeros((len(countries), len(countries)))
        for _, row in data_p.iterrows():
            if (row["L_REP_CTYReporting country"] in countries and
                    row["L_CP_COUNTRYCounterparty country"] in countries):
                i = countries.index(row["L_REP_CTYReporting country"])
                j = countries.index(row["L_CP_COUNTRYCounterparty country"])
                wm[j, i] = max(0, row.Leverage)
        weight_matrices[p] = wm

    return (
        weight_matrices,
        countries,
        COUNTRY_META_BIS["name_map"],
        {code: COORDS_GENERIC[COUNTRY_META_BIS["name_map"][code]] for code in countries},
        periods,
    )


def load_dataset_un(base_dir: Path) -> tuple[
    dict[str, np.ndarray], list[str], dict[str, str], dict[str, tuple[float, float]], list[pd.Timestamp]
]:
    all_c_file = base_dir / "UN_debtrank" / "all_countries_e.xlsx"
    one_c_file = base_dir / "UN_debtrank" / "one_countries_e_c.csv"


    all_df = pd.read_excel(all_c_file, sheet_name="Aggregated Data")
    one_df = pd.read_csv(one_c_file)

    all_df.columns = all_df.columns.str.strip()
    one_df.columns = one_df.columns.str.strip()

    all_df["reporterISO"] = all_df["reporterISO"].str.strip()
    all_df["partnerISO"] = all_df["partnerISO"].str.strip()
    one_df["reporterISO"] = one_df["reporterISO"].str.strip()
    one_df["partnerISO"] = one_df["partnerISO"].str.strip()

    all_df["period_quarter"] = pd.to_datetime(all_df["period"].astype(str), format="%Y%m").dt.to_period("Q").dt.start_time
    one_df["period_quarter"] = pd.to_datetime(one_df["period"].astype(str), format="%Y%m").dt.to_period("Q").dt.start_time

    countries = COUNTRY_META_UN["codes"]

    all_c = (
        all_df.groupby(["reporterISO", "period_quarter"])["primaryValue"].sum().reset_index().rename(columns={"primaryValue": "TotalGiven"})
    )
    one_df = one_df[one_df["reporterISO"].isin(all_c["reporterISO"].unique())]

    one_c = (
        one_df.groupby(["reporterISO", "partnerISO", "period_quarter"])["primaryValue"].sum().reset_index().rename(columns={"primaryValue": "GivenToCp"})
    )

    merged = pd.merge(one_c, all_c, on=["reporterISO", "period_quarter"], how="left")
    merged["Leverage"] = merged.apply(lambda r: 0 if r.TotalGiven == 0 else r.GivenToCp / r.TotalGiven, axis=1)

    periods = sorted(merged["period_quarter"].unique())

    weight_matrices: dict[pd.Timestamp, np.ndarray] = {}
    for p in periods:
        data_p = merged[merged["period_quarter"] == p]
        wm = np.zeros((len(countries), len(countries)))
        for _, row in data_p.iterrows():
            if row.reporterISO in countries and row.partnerISO in countries:
                i = countries.index(row.reporterISO)
                j = countries.index(row.partnerISO)
                wm[j, i] = row.Leverage
        weight_matrices[p] = wm

    return (
        weight_matrices,
        countries,
        COUNTRY_META_UN["name_map"],
        {code: COORDS_GENERIC[COUNTRY_META_UN["name_map"][code]] for code in countries},
        periods,
    )


def initialise_risk_vector(
    countries: list[str],
    country_name_map: dict[str, str],
    default_prob_df: pd.DataFrame,
    period,
):
    vec = np.zeros(len(countries))
    period_data = default_prob_df[default_prob_df["Year_Quarter"] == period]
    for idx, iso in enumerate(countries):
        cname = country_name_map[iso]
        prob_arr = period_data.loc[period_data["Country"] == cname, "Default_Probability"].values
        if prob_arr.size:
            vec[idx] = max(0.0, prob_arr[0])
    return vec


def propagate_debtrank(
    weight_matrix: np.ndarray,
    h0: np.ndarray,
    max_iter: int = 100,
    threshold: float = 1e-3,
):
    h_prev = np.zeros_like(h0)
    h = h0.copy()
    H = h0.copy()
    history: list[np.ndarray] = []

    for _ in range(max_iter):
        delta = np.maximum(0, h - h_prev)
        new_h = (weight_matrix @ delta).clip(0, 1)
        H = np.minimum(H + new_h, 1)
        history.append(H.copy())
        if np.all(new_h < threshold):
            break
        h_prev = h
        h = new_h
    return history


def run_simulation(
    dataset: str,
    base_dir: Path,
    default_file: Path,
    out_dir: Path,
    make_animation: bool = True,
):
    if dataset.upper() == "BIS":
        wm, countries, name_map, coords, periods = load_dataset_bis(base_dir)
    elif dataset.upper() == "UN":
        wm, countries, name_map, coords, periods = load_dataset_un(base_dir)
    else:
        raise ValueError("dataset must be BIS or UN")

    default_df = pd.read_excel(default_file)

    if dataset.upper() == "UN":
        default_df["Year_Quarter"] = pd.PeriodIndex(default_df["Year_Quarter"], freq="Q").to_timestamp()

    results: dict = {}
    for per in periods:
        h0 = initialise_risk_vector(countries, name_map, default_df, per)
        hist = propagate_debtrank(wm[per], h0)
        results[per] = hist

    excel_out = out_dir / f"{dataset}_debtrank_results.xlsx"
    with pd.ExcelWriter(excel_out) as writer:
        for per, hist in results.items():
            sheet_name = str(per).replace(":", "-")[:31]  
            df = pd.DataFrame(hist, columns=countries)
            df.index.name = "Step"
            df.to_excel(writer, sheet_name=sheet_name)
    print(f"📓 Results saved → {excel_out}")

    lev_out = out_dir / f"{dataset}_leverage_matrices.xlsx"
    with pd.ExcelWriter(lev_out) as writer:
        for per, mat in wm.items():
            df = pd.DataFrame(mat, index=countries, columns=countries)
            df.index.name = "From"; df.columns.name = "To"
            df.to_excel(writer, sheet_name=str(per)[:31])
    print(f"📓 Leverage matrices saved → {lev_out}")

    if make_animation:
        print("🎞  Generating animation … this can take a while on first run")
        _make_animation(results, wm, countries, coords, out_dir / f"{dataset}_propagation.mp4")



def _make_animation(
    all_histories: dict,
    weight_matrices: dict,
    countries: list[str],
    coords: dict[str, tuple[float, float]],
    outfile: Path,
):
    fig, ax = plt.subplots(figsize=(14, 9))
    m = Basemap(projection="mill", ax=ax)

    period_order = list(all_histories.keys())
    cum_lengths = np.cumsum([0] + [len(all_histories[p]) for p in period_order])
    total_frames = cum_lengths[-1]

    def _update(frame):
        ax.clear()
        m.drawcoastlines(); m.drawcountries()
        idx = np.searchsorted(cum_lengths, frame, side="right") - 1
        period = period_order[idx]
        local_step = frame - cum_lengths[idx]
        risks = all_histories[period][local_step]
        wm = weight_matrices[period]

        max_risk = max(risks.max(), 1e-6)
        for iso, risk in zip(countries, risks):
            x, y = m(*coords[iso])
            ax.plot(x, y, "o", markersize=10, color=plt.cm.Reds(risk / max_risk), alpha=0.8)
        for i, iso_from in enumerate(countries):
            for j, iso_to in enumerate(countries):
                if wm[j, i] > 0:
                    x1, y1 = m(*coords[iso_from]); x2, y2 = m(*coords[iso_to])
                    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                                arrowprops=dict(arrowstyle="-", lw=wm[j, i]*2, alpha=0.3, color="blue"))
        ax.set_title(f"{period} – step {local_step+1}")

    ani = animation.FuncAnimation(fig, _update, frames=total_frames, interval=800, repeat=False)
    ani.save(outfile, writer=animation.FFMpegWriter(fps=2))
    plt.close(fig)
    print(f"🎞  Animation saved → {outfile}")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="DebtRank risk‑propagation simulator (BIS / UN)")
    p.add_argument("--dataset", choices=["BIS", "UN"], default="BIS", help="Which dataset to run (default: BIS)")
    p.add_argument("--base-dir", default="./", type=Path, help="Directory containing BIS/ or UN/ sub‑folders")
    p.add_argument("--out-dir", default="./output", type=Path, help="Directory for results")
    p.add_argument("--default-file", default="./default/Default_Probabilities_5Years_Bond.xlsx", type=Path, help="Default probability xlsx path")
    anim_group = p.add_mutually_exclusive_group()
    anim_group.add_argument("--animate", dest="animate", action="store_true", default=True, help="Generate mp4 animation (default)")
    anim_group.add_argument("--no-animation", dest="animate", action="store_false", help="Skip animation")
    return p.parse_args(argv)



def main(argv=None):
    args = parse_args(argv)
    _ensure_outdir(args.out_dir)
    run_simulation(
        dataset=args.dataset,
        base_dir=args.base_dir,
        default_file=args.default_file,
        out_dir=args.out_dir,
        make_animation=args.animate,
    )


if __name__ == "__main__":
    main()
