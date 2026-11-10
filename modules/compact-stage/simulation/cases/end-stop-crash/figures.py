"""Figures for the end-stop crash case (matplotlib, PNG)."""

import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6"]
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"
SURFACE = "#fcfcfb"
CRITICAL = "#d03b3b"
BLUES = LinearSegmentedColormap.from_list("blues", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11, "axes.titlecolor": INK,
    "lines.linewidth": 2.0, "legend.frameon": False,
})


def time_histories(named, out_dir):
    keys = ["no payload", "1 kg at 50 mm", "cross stage, upper carriage +0 mm"]
    fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    for i, k in enumerate(keys):
        r = named[k]
        rec = r["_rec"]
        t = rec["t"] * 1e3
        total = rec["fb"].sum(axis=1) + rec["fm"]
        axes[0].plot(t, total / 1e3, color=SERIES[i], label=k)
        import crash_model as cm
        a = np.linalg.norm(cm.point_accel(rec, r["_model"].r_head), axis=1)
        axes[1].plot(t, a, color=SERIES[i], label=k)
    axes[0].set_ylabel("Force on the base end wall (kN)")
    axes[0].set_title("Force on the end wall during the crash (2 m/s, motor pushing)", loc="left")
    axes[1].axhline(1000, color=CRITICAL, linewidth=1.2, linestyle="--")
    axes[1].text(0.2, 1000, " read head limit 1000 m/s² (6 ms)", color=INK2, va="bottom", fontsize=9)
    axes[1].set_ylabel("Read head acceleration (m/s²)")
    axes[1].set_xlabel("Time from the first bumper touch (ms)")
    axes[1].set_title("Acceleration of the read head", loc="left")
    axes[0].legend(loc="upper right")
    for ax in axes:
        ax.set_xlim(left=0)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "time-histories.png"), dpi=150)
    plt.close(fig)


def heatmap(ax, table, key, title, fmt, limit=None, invert=False):
    P = sorted({r["payload_kg"] for r in table})
    H = sorted({r["com_height_mm"] for r in table})
    Z = np.zeros((len(H), len(P)))
    for r in table:
        Z[H.index(r["com_height_mm"]), P.index(r["payload_kg"])] = r[key]
    cmap = BLUES.reversed() if invert else BLUES
    im = ax.imshow(Z, origin="lower", cmap=cmap, aspect="auto")
    ax.set_xticks(range(len(P)), ["%g" % p for p in P])
    ax.set_yticks(range(len(H)), ["%g" % h for h in H])
    ax.set_xlabel("Payload (kg)")
    ax.set_ylabel("Centre of mass above the carriage top (mm)")
    ax.set_title(title, loc="left")
    ax.grid(False)
    norm = im.norm
    for i in range(len(H)):
        for j in range(len(P)):
            v = Z[i, j]
            dark = norm(v) > 0.55 if not invert else norm(v) < 0.45
            bad = limit is not None and ((v < limit) if invert else (v > limit))
            ax.text(j, i, fmt % v + (" !" if bad else ""), ha="center", va="center", fontsize=8,
                    color="#ffffff" if dark else INK)


def table_maps(table, out_dir):
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    heatmap(axes[0, 0], table, "block_fsl", "Guide blocks: static safety C0/P (HIWIN asks 3 to 5; ! = below 1)",
            "%.2f", limit=1.0, invert=True)
    heatmap(axes[0, 1], table, "read_head_m_s2", "Read head peak acceleration, m/s² (! = above 1000)",
            "%.0f", limit=1000.0)
    heatmap(axes[1, 0], table, "payload_slip_use", "Payload on 6 x M5: slip use, friction 0.10 (! = slides)",
            "%.2f", limit=1.0)
    heatmap(axes[1, 1], table, "base_lasting_dent_mm", "Base end wall: lasting dent (mm)", "%.3f")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "payload-table.png"), dpi=150)
    plt.close(fig)


def fem_curves(fem, cfg, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for i, (key, lab) in enumerate((("pocket", "Pocket back walls (both bumpers)"),
                                    ("band", "End wall face (carriage end hits)"))):
        cv = fem[key]["curve"]
        F = np.array([c["force"] for c in cv]) / 1e3
        axes[0].plot(F, [c["von_mises_max"] for c in cv], color=SERIES[i], label=lab)
        axes[1].plot(F, [100 * c["peeq_max"] for c in cv], color=SERIES[i], label=lab)
    mat = cfg["material_base"]
    axes[0].axhline(mat["rp02"], color=INK2, linewidth=1, linestyle="--")
    axes[0].text(1, mat["rp02"], " yield Rp0.2 %g MPa" % mat["rp02"], va="bottom", color=INK2, fontsize=9)
    axes[1].axhline(100 * mat["elongation"], color=CRITICAL, linewidth=1, linestyle="--")
    axes[1].text(1, 100 * mat["elongation"], " elongation at break A50 (minimum)", va="bottom", color=INK2, fontsize=9)
    axes[0].set_title("Peak stress in the base (7075-T651)", loc="left")
    axes[1].set_title("Peak plastic strain in the base", loc="left")
    axes[0].set_ylabel("Von Mises stress (MPa)")
    axes[1].set_ylabel("Plastic strain (%)")
    for ax in axes:
        ax.set_xlabel("Force (kN)")
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
    axes[0].legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "base-stress.png"), dpi=150)
    plt.close(fig)


def make_all(cfg, fem, named, table, out_dir):
    time_histories(named, out_dir)
    table_maps(table, out_dir)
    fem_curves(fem, cfg, out_dir)
