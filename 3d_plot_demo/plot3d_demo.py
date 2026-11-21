"""Two paper-grade matplotlib 3D figures (orthographic, no default styling).

Output: fig_surface.png / fig_buildings.png (300 dpi) and .pdf (vector).
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# ---------------------------------------------------------------- global style
mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 10,
    "axes.linewidth": 0.8,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
})


def style_3d(ax, elev=26, azim=-58):
    """Clean engineering-drawing look: ortho projection, white panes, faint grid."""
    ax.set_proj_type("ortho")          # perspective is what makes renders look "3D-movie"-ish
    ax.view_init(elev=elev, azim=azim)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((1, 1, 1, 1))
        axis.pane.set_edgecolor((0.55, 0.55, 0.55, 1))
        axis._axinfo["grid"].update(color="0.82", linewidth=0.4, linestyle=":")
    ax.tick_params(direction="out", length=3, width=0.7, pad=0)
    ax.set_box_aspect((1.35, 1.0, 0.62))
    ax.zaxis.set_rotate_label(False)


# ------------------------------------------------------- fig 1: surface + contour
x = np.linspace(0, 100, 161)
y = np.linspace(0, 100, 161)
X, Y = np.meshgrid(x, y)

# fake "observable score": smooth bump + two Gaussian valleys (replace with your model output)
Z = (1.5 * np.exp(-((X - 78) ** 2 + (Y - 72) ** 2) / 900)
     + 0.9 * np.exp(-((X - 30) ** 2 + (Y - 40) ** 2) / 1400)
     - 0.55 * np.exp(-((X - 55) ** 2 + (Y - 25) ** 2) / 500))
Z = np.clip(Z, 0, None)

fig = plt.figure(figsize=(5.4, 4.2))
ax = fig.add_subplot(111, projection="3d")
style_3d(ax, elev=27, azim=-123)

surf = ax.plot_surface(
    X, Y, Z, cmap="viridis", rstride=2, cstride=2,
    linewidth=0, antialiased=True, alpha=0.96, shade=True,
)
# contour lines drawn on the surface itself (much better than a dense wireframe)
ax.contour(X, Y, Z, levels=8, cmap="viridis", linewidths=0.6, alpha=0.9)
# same contour lines projected on the floor plane z = 0
ax.contour(X, Y, Z, zdir="z", offset=0, levels=8,
           colors="0.45", linewidths=0.45, alpha=0.8)

ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_zlim(0, 1.9)
ax.set_xlabel(r"$x$ (m)", labelpad=8, fontsize=9)
ax.set_ylabel(r"$y$ (m)", labelpad=8, fontsize=9)
ax.set_zlabel(r"score $\phi$", labelpad=10, fontsize=9)
ax.set_xticks(np.arange(0, 101, 20))
ax.set_yticks(np.arange(0, 101, 20))
ax.set_zticks(np.arange(0, 2.0, 0.5))

cb = fig.colorbar(surf, ax=ax, shrink=0.62, pad=0.09, aspect=18)
cb.outline.set_linewidth(0.6)
cb.ax.tick_params(length=2.5, width=0.6, labelsize=8)

fig.savefig("/workspace/3d_plot_demo/fig_surface.png")
fig.savefig("/workspace/3d_plot_demo/fig_surface.pdf")
plt.close(fig)


# ------------------------------------- fig 2: extruded buildings + feasible grid
buildings = [("B1", 22, 20, 8, 6, 20), ("B3", 14, 68, 10, 6, 12),
             ("B5", 38, 40, 10, 6, 32), ("B2", 62, 60, 16, 10, 28),
             ("B4", 72, 22, 12, 10, 24)]
cmap = plt.get_cmap("Greys")

fig = plt.figure(figsize=(5.6, 4.4))
ax = fig.add_subplot(111, projection="3d")
style_3d(ax, elev=22, azim=-114)

# feasible centres at z = 0, coloured by distance to nearest building (dense but subtle)
rng = np.random.default_rng(7)
gx, gy = np.meshgrid(np.arange(0.5, 100, 1.2), np.arange(0.5, 100, 1.2))
gx, gy = gx.ravel(), gy.ravel()
keep = (gx - 88) ** 2 + (gy - 76) ** 2 < 26 ** 2
gx, gy = gx[keep], gy[keep]
ax.scatter(gx, gy, np.zeros_like(gx), s=2.2, c="tab:blue", alpha=0.18,
           edgecolors="none", depthshade=False)

for name, x0, y0, w, d, h in buildings:
    # solid box with flat facade shading (no glossy lighting -> no "render" look)
    ax.bar3d(x0, y0, 0, w, d, h, color="0.78", edgecolor="0.28",
             linewidth=0.6, shade=True, alpha=1.0, zsort="max")
    ax.text(x0 + w / 2, y0 + d / 2, h + 1.5, f"{name}", ha="center",
            va="bottom", fontsize=8, color="0.12")

# recommended station
ax.scatter([88.8], [76.3], [0], marker="*", s=110, c="tab:red",
           edgecolors="k", linewidths=0.4, depthshade=False, zorder=5)
ax.text(88.8, 76.3, 6, r"$P^*$", color="tab:red", fontsize=10, ha="left")

ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_zlim(0, 40)
ax.set_xticks(np.arange(0, 101, 20)); ax.set_yticks(np.arange(0, 101, 20))
ax.set_zticks(np.arange(0, 41, 10))
ax.set_xlabel(r"$x$ (m)", labelpad=8, fontsize=9)
ax.set_ylabel(r"$y$ (m)", labelpad=8, fontsize=9)
ax.set_zlabel(r"$z$ (m)", labelpad=10, fontsize=9)

fig.savefig("/workspace/3d_plot_demo/fig_buildings.png")
fig.savefig("/workspace/3d_plot_demo/fig_buildings.pdf")
plt.close(fig)
print("done")
