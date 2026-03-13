import matplotlib.pyplot as plt

col_labels = [
    "", "Vertical (b)\nBIS", "Vertical (b)\nUN",
    "Aggregate (c)\nBIS", "Aggregate (c)\nUN",
    "Joint (b×c)\nBIS", "Joint (b×c)\nUN"
]

rows = [
    ["Ranking similarity (min–max)",
     "0.9993–0.9994", "0.9847–0.9896",
     "0.9987–0.9991", "0.9952–0.9974",
     "0.996–0.999", "0.981–0.993"],

    ["Average rank change",
     "0.016", "0.202",
     "0.022", "0.031",
     "0.024", "0.086"],

    ["",
     "(0.006)", "(0.008)",
     "(0.018)", "(0.014)",
     "(0.012)", "(0.029)"],

    ["Top-5 countries unchanged (%)",
     "99.3–100.0", "95.0–97.0",
     "99.0–100.0", "98.0–100.0",
     "98.5–100.0", "94.0–99.0"],
]


plt.rcParams["font.family"] = "DejaVu Serif"  
fig, ax = plt.subplots(figsize=(14.5, 4.8))
ax.axis("off")


ax.text(
    0, 1.10,
    "Dependent variable: Systemic risk ranking stability",
    fontsize=14, fontweight="bold",
    transform=ax.transAxes
)


table = ax.table(
    cellText=rows,
    colLabels=col_labels,
    cellLoc="center",
    colLoc="center",
    loc="upper left",
    bbox=[0, 0.15, 1, 0.8]
)

table.auto_set_font_size(False)
table.set_fontsize(11)


for c in range(len(col_labels)):
    cell = table[(0, c)]
    cell.set_text_props(weight="bold")
    cell.set_linewidth(1.2)

nrows = len(rows)
ncols = len(col_labels)

for r in range(1, nrows + 1):
    for c in range(ncols):
        cell = table[(r, c)]
        cell.set_linewidth(0.6)
        if c == 0:
            cell.set_text_props(ha="left")


ax.text(
    0, 0.06,
    "Notes: Values summarize sensitivity of systemic risk rankings to threshold choices. "
    "Numbers in parentheses indicate standard deviations across simulations.",
    fontsize=10,
    transform=ax.transAxes
)

plt.savefig(
    "paper_style_sensitivity_table.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

print("Saved: paper_style_sensitivity_table.png")
