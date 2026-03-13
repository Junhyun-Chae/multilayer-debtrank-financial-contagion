
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from BIS_UN_debtrank_0513copyBISonly import (
    load_dataset_bis,
    load_dataset_un,
    initialise_risk_vector,
)

def rankdata_desc(values: np.ndarray) -> np.ndarray:
    """
    Return ranks (1 = highest) with average-tie handling, descending order.
    """
    s = pd.Series(np.asarray(values, dtype=float))
    ranks = s.rank(ascending=False, method="average").to_numpy(dtype=float)
    return ranks

def pearson_corr(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x = x - x.mean()
    y = y - y.mean()
    denom = np.sqrt((x * x).sum()) * np.sqrt((y * y).sum())
    if denom == 0:
        return float("nan")
    return float((x * y).sum() / denom)

def spearman_corr_from_values(values_a: np.ndarray, values_b: np.ndarray) -> float:
    """
    Spearman correlation computed as Pearson correlation of ranks.
    """
    ra = rankdata_desc(values_a)
    rb = rankdata_desc(values_b)
    return pearson_corr(ra, rb)

def mean_abs_rank_change(ranks_a: np.ndarray, ranks_b: np.ndarray) -> float:
    """
    Mean |Δrank| = (1/N) * sum_i |rank_i,a - rank_i,b|
    Here ranks are float (average ties). This matches your Eq.(16) spirit.
    """
    ra = np.asarray(ranks_a, dtype=float)
    rb = np.asarray(ranks_b, dtype=float)
    if ra.shape != rb.shape:
        raise ValueError("Rank vectors must have the same shape.")
    return float(np.mean(np.abs(ra - rb)))

def topk_set(values: np.ndarray, labels: list[str], k: int) -> set[str]:
    values = np.asarray(values, dtype=float)
    idx = np.argsort(values)[::-1][:k]
    return {labels[i] for i in idx}

def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def propagate_multilayer_with_vertical(
    W_bis: np.ndarray,
    W_un: np.ndarray,
    h0_bis: np.ndarray,
    h0_un: np.ndarray,
    vertical_alpha: float,
    vertical_threshold: float,
    max_iter: int = 30,
    eps: float = 1e-3,
):
    h_prev_bis = np.zeros_like(h0_bis)
    h_prev_un  = np.zeros_like(h0_un)

    h_bis = h0_bis.copy()
    h_un  = h0_un.copy()

    H_bis = h0_bis.copy()
    H_un  = h0_un.copy()

    history_bis: list[np.ndarray] = []
    history_un:  list[np.ndarray] = []
    vhist_bis2un: list[np.ndarray] = []
    vhist_un2bis: list[np.ndarray] = []

    for _ in range(max_iter):
        delta_bis = np.maximum(0, h_bis - h_prev_bis)
        new_h_bis = (W_bis @ delta_bis).clip(0, 1)
        H_bis = np.minimum(H_bis + new_h_bis, 1)

        mask_bis = H_bis >= vertical_threshold
        vtrans_bis = vertical_alpha * H_bis * mask_bis.astype(float)
        new_h_un_from_bis = np.minimum(vtrans_bis, 1 - H_un)
        vhist_bis2un.append(new_h_un_from_bis.copy())

        history_bis.append(H_bis.copy())

        delta_un = np.maximum(0, h_un - h_prev_un)
        new_h_un = (W_un @ delta_un).clip(0, 1)
        new_h_un = np.minimum(new_h_un + new_h_un_from_bis, 1)
        H_un = np.minimum(H_un + new_h_un, 1)

        mask_un = H_un >= vertical_threshold
        vtrans_un = vertical_alpha * H_un * mask_un.astype(float)
        new_h_bis_from_un = np.minimum(vtrans_un, 1 - H_bis)
        vhist_un2bis.append(new_h_bis_from_un.copy())

        new_h_bis = np.minimum(new_h_bis + new_h_bis_from_un, 1)
        H_bis = np.minimum(H_bis + new_h_bis_from_un, 1)

        history_un.append(H_un.copy())

        if np.all(new_h_bis < eps) and np.all(new_h_un < eps):
            break

        h_prev_bis, h_bis = h_bis, new_h_bis
        h_prev_un,  h_un  = h_un,  new_h_un

    return history_bis, history_un, vhist_bis2un, vhist_un2bis

def prepare_common_data(base_dir: Path, default_file: Path):

    WM_bis_raw, countries_bis, name_map_bis, coords_bis, periods_bis = load_dataset_bis(base_dir)
    WM_un_raw,  countries_un,  name_map_un,  coords_un,  periods_un  = load_dataset_un(base_dir)

    iso2_to_name = name_map_bis
    name_to_iso3 = {v: k for k, v in name_map_un.items()}
    common_iso2 = [iso for iso, name in iso2_to_name.items() if name in name_to_iso3]

    periods_bis_ts = pd.PeriodIndex(periods_bis, freq="Q").to_timestamp()
    common_periods = sorted(set(periods_bis_ts) & set(periods_un))

    WM_bis = {}
    for ts in common_periods:
        bis_key = f"{ts.year}-Q{ts.quarter}"
        WM_bis[ts] = WM_bis_raw[bis_key]

    WM_un = {}
    for p in common_periods:
        orig = WM_un_raw[p]
        N = len(common_iso2)
        mat = np.zeros((N, N))
        for i, iso2_i in enumerate(common_iso2):
            iso3_i = name_to_iso3[iso2_to_name[iso2_i]]
            idx_i3 = countries_un.index(iso3_i)
            for j, iso2_j in enumerate(common_iso2):
                iso3_j = name_to_iso3[iso2_to_name[iso2_j]]
                idx_j3 = countries_un.index(iso3_j)
                mat[j, i] = orig[idx_j3, idx_i3]
        WM_un[p] = mat

    default_df = pd.read_excel(default_file)
    default_df["Year_Quarter"] = pd.PeriodIndex(default_df["Year_Quarter"], freq="Q").to_timestamp()

    meta = {
        "countries_bis": countries_bis,
        "countries_un": countries_un,
        "name_map_bis": name_map_bis,
        "name_map_un": name_map_un,
        "common_iso2": common_iso2,
        "common_periods": common_periods,
        "default_df": default_df,
    }
    return WM_bis, WM_un, meta

def run_one_kappa(
    kappa: float,
    WM_bis: dict[pd.Timestamp, np.ndarray],
    WM_un: dict[pd.Timestamp, np.ndarray],
    meta: dict,
    vertical_threshold: float,
    max_iter: int,
):
    common_iso2 = meta["common_iso2"]
    common_periods = meta["common_periods"]
    default_df = meta["default_df"]

    countries_bis = meta["countries_bis"]
    countries_un = meta["countries_un"]
    name_map_bis = meta["name_map_bis"]
    name_map_un  = meta["name_map_un"]

    N = len(common_iso2)

    importance = np.zeros(N, dtype=float)

    V_bis2un_total = 0.0
    V_un2bis_total = 0.0
    act_bis2un_sum = 0.0
    act_un2bis_sum = 0.0
    steps_bis2un = 0
    steps_un2bis = 0

    for per in common_periods:
        h0_bis = initialise_risk_vector(countries_bis, name_map_bis, default_df, per)
        h0_un  = initialise_risk_vector(countries_un,  name_map_un,  default_df, per)

        hist_bis, hist_un, vhist_bis2un, vhist_un2bis = propagate_multilayer_with_vertical(
            WM_bis[per], WM_un[per],
            h0_bis, h0_un,
            vertical_alpha=kappa,
            vertical_threshold=vertical_threshold,
            max_iter=max_iter,
        )

        last_bis = np.array(hist_bis[-1]) if len(hist_bis) > 0 else np.array(h0_bis)
        last_un  = np.array(hist_un[-1])  if len(hist_un)  > 0 else np.array(h0_un)
        last_avg = (last_bis + last_un) / 2.0
        importance += last_avg

        for v in vhist_bis2un:
            V_bis2un_total += float(np.sum(v))
            act_bis2un_sum += float(np.count_nonzero(v > 0) / N)
            steps_bis2un += 1

        for v in vhist_un2bis:
            V_un2bis_total += float(np.sum(v))
            act_un2bis_sum += float(np.count_nonzero(v > 0) / N)
            steps_un2bis += 1

    act_rate_bis2un = (act_bis2un_sum / steps_bis2un) if steps_bis2un > 0 else 0.0
    act_rate_un2bis = (act_un2bis_sum / steps_un2bis) if steps_un2bis > 0 else 0.0

    ranks = rankdata_desc(importance)

    return {
        "kappa": float(kappa),
        "importance": importance,
        "ranks": ranks,  # <-- ADDED for Mean|Δrank|
        "V_BIS_to_UN": float(V_bis2un_total),
        "V_UN_to_BIS": float(V_un2bis_total),
        "ActivationRate_BIS_to_UN": float(act_rate_bis2un),
        "ActivationRate_UN_to_BIS": float(act_rate_un2bis),
    }


def kappa_sensitivity(
    base_dir: Path,
    default_file: Path,
    vertical_threshold: float,
    max_iter: int,
    kappa_grid: list[float],
    baseline_kappa: float,
    topk_list: list[int],
    out_csv: Path,
):
    WM_bis, WM_un, meta = prepare_common_data(base_dir, default_file)
    labels = meta["common_iso2"]

    base_res = run_one_kappa(
        baseline_kappa, WM_bis, WM_un, meta,
        vertical_threshold=vertical_threshold,
        max_iter=max_iter,
    )
    base_importance = base_res["importance"]
    base_ranks = base_res["ranks"]

    rows = []
    for kappa in kappa_grid:
        res = run_one_kappa(
            kappa, WM_bis, WM_un, meta,
            vertical_threshold=vertical_threshold,
            max_iter=max_iter,
        )
        imp = res["importance"]
        ranks = res["ranks"]

        spearman = spearman_corr_from_values(imp, base_importance)
        mean_delta_rank = mean_abs_rank_change(ranks, base_ranks) 

        row = {
            "kappa": float(kappa),
            "spearman_vs_baseline": float(spearman),
            "mean_abs_delta_rank_vs_baseline": float(mean_delta_rank), 
            "V_BIS_to_UN": res["V_BIS_to_UN"],
            "V_UN_to_BIS": res["V_UN_to_BIS"],
            "ActivationRate_BIS_to_UN": res["ActivationRate_BIS_to_UN"],
            "ActivationRate_UN_to_BIS": res["ActivationRate_UN_to_BIS"],
        }

        for k in topk_list:
            s_k = topk_set(imp, labels, k)
            s_0 = topk_set(base_importance, labels, k)
            row[f"jaccard_top{k}"] = float(jaccard(s_k, s_0))

        rows.append(row)
        print(f"[done] kappa={kappa:.4f} | spearman={spearman:.4f} | mean|Δrank|={mean_delta_rank:.4f}")

    df = pd.DataFrame(rows).sort_values("kappa").reset_index(drop=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"\nSaved: {out_csv}")
    print("\nPreview:")
    print(df.to_string(index=False))

def parse_args():
    p = argparse.ArgumentParser(description="κ-sensitivity analysis (Ranking + Vertical activation)")
    p.add_argument("--base-dir", default="./", type=Path)
    p.add_argument("--default-file", default="./default/Default_Probabilities_5Years_Bond.xlsx", type=Path)
    p.add_argument("--vertical-threshold", type=float, default=0.5)
    p.add_argument("--max-iter", type=int, default=20)

    p.add_argument("--kappa-grid", nargs="+", type=float, default=None,
                   help="Explicit kappa list, e.g., 0 0.01 0.03 ... 1.0")

    p.add_argument("--kappa-auto", action="store_true",
                   help="Use auto grid from 0 to 1 inclusive")
    p.add_argument("--kappa-step", type=float, default=0.05,
                   help="Step for auto grid (only used when --kappa-auto)")

    p.add_argument("--baseline-kappa", type=float, default=0.07)
    p.add_argument("--topk", nargs="+", type=int, default=[5, 10])
    p.add_argument("--out-csv", type=Path, default=Path("./output/kappa_sensitivity_results.csv"))
    return p.parse_args()

def build_kappa_grid(args) -> list[float]:
    if args.kappa_grid is not None and len(args.kappa_grid) > 0:
        return [float(x) for x in args.kappa_grid]

    if args.kappa_auto:
        step = float(args.kappa_step)
        if step <= 0:
            raise ValueError("--kappa-step must be > 0")
        grid = np.round(np.arange(0.0, 1.0 + 1e-12, step), 10).tolist()
        if grid[-1] != 1.0:
            grid.append(1.0)
        return [float(x) for x in grid]

    return [
        0.00, 0.01, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20,
        0.30, 0.40, 0.50, 0.70, 1.00
    ]

if __name__ == "__main__":
    args = parse_args()
    kappa_grid = build_kappa_grid(args)

    kappa_sensitivity(
        base_dir=args.base_dir,
        default_file=args.default_file,
        vertical_threshold=args.vertical_threshold,
        max_iter=args.max_iter,
        kappa_grid=kappa_grid,
        baseline_kappa=args.baseline_kappa,
        topk_list=args.topk,
        out_csv=args.out_csv,
    )
