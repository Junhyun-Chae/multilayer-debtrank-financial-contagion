
from __future__ import annotations
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text
import numpy as np
import matplotlib.ticker as ticker

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["axes.unicode_minus"] = False


def plot_graph(file_path: Path):

    if not file_path.exists():
        print(f"오류: {file_path} 파일이 존재하지 않습니다. 먼저 process_data.py를 실행하세요.")
        return

    df = pd.read_csv(file_path)
    countries = df["ISO2"].tolist()
    x = df["Horizontal_total"].values
    y = df["Vertical_total"].values

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(x, y, s=100, alpha=0.75, edgecolor="black", c="tab:blue")

    ax.set_title("Horizontal vs Vertical Contagion by Country", fontsize=35, pad=15)


    x_max = 77
    y_max = 12
    ax.plot([0, x_max], [0, y_max], color="gray", linestyle="--", linewidth=1.2, alpha=0.8)

    texts = []
    for i, iso in enumerate(countries):
        texts.append(ax.text(x[i], y[i], iso, ha="center", va="bottom", fontsize=20))

    adjust_text(
        texts,
        x=x,
        y=y,
        force_points=(1.5, 1.5),
        force_text=(1.5, 1.5),
        expand_points=(1.2, 1.2),
        arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
    )

    def px_to_data(ax, dx_px, dy_px):
        inv = ax.transData.inverted()
        x0, y0 = ax.transData.transform((0, 0))
        x1, y1 = x0 + dx_px, y0 + dy_px
        (dx_data, dy_data) = inv.transform((x1, y1)) - inv.transform((0, 0))
        return dx_data, dy_data

    r_max_px = 25 
    dx_cap, dy_cap = px_to_data(ax, r_max_px, r_max_px)
    r_max_data = np.hypot(dx_cap, dy_cap)

    for i, t in enumerate(texts):
        tx, ty = t.get_position()
        vx, vy = (tx - x[i], ty - y[i])
        dist = np.hypot(vx, vy)

        if dist > 0 and dist > r_max_data:
            scale = r_max_data / dist
            t.set_position((x[i] + vx * scale, y[i] + vy * scale))

    ax.set_xlabel(r"Horizontal propagation ($C_i^{\mathrm{Hor}}$)", fontsize=30)
    ax.set_ylabel(r"Vertical contagion ($C_i^{\mathrm{Ver}}$)", fontsize=30)
    ax.tick_params(axis="both", which="major", labelsize=25)

    ax.set_ylim(0, 12)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2.5))
    ax.yaxis.set_minor_locator(ticker.NullLocator())

    ax.set_xlim(0, 77)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.xaxis.set_minor_locator(ticker.NullLocator())

    ax.grid(True, which="major", alpha=0.3)

    plt.tight_layout()

    out_png = file_path.parent / "scatter_horizontal_vs_vertical_by_country_capped.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.show()
    print(f"📈 캡핑된 라벨 위치가 적용된 그래프가 {out_png}에 저장되었습니다.")


def parse_args():
    p = argparse.ArgumentParser(description="Plot graph from saved data")
    p.add_argument(
        "--data-file",
        default="./output_scatter/horizontal_vs_vertical_by_country.csv",
        type=Path,
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    plot_graph(args.data_file)
