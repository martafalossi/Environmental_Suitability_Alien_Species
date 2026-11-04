# -*- coding: utf-8 -*-
"""Figures for the manuscript:
"Machine Learning Projections of Future Environmental Suitability to Marine Alien Species
in the Mediterranean Sea"

This script contains plotting routines used to generate the manuscript figures.
It includes maps of alien-species observation records, environmental suitability,
suitability categories, and baseline/future environmental conditions.

The script is intended to be run after loading the input datasets described in the
repository documentation. See the README for the required data files, dependencies,
and execution instructions.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime as dt
import geopandas as gpd
import matplotlib.colors as mcolors
from matplotlib.colors import LogNorm
import matplotlib.patches as patches
import cmocean
from matplotlib.colors import BoundaryNorm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib.patches import FancyBboxPatch
from matplotlib.patches import Wedge
from matplotlib.lines import Line2D

"""Figure 1. Alien-species observation records by Mediterranean country.

The map displays the number of records grouped into four time periods:
1999–2004, 2005–2010, 2011–2016, and 2017–2021.
The size of each quarter-circle represents the number of observations in that period.
"""

# Load the geographical boundaries and observation data.
path= ''' shapefile with geographical boundaries, I used the one at 10m resolution from
          https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/ '''
world = gpd.read_file(path)

# Mediterranean countries from unified alien species dataset
# Alien_data available in 'data' section of the repository
Alien_data=Alien_data[Alien_data['Year']>1999]
med_countries = Alien_data.Country.unique()
med_map = world[world['NAME'].isin(med_countries)]

# DEFINE AGGREGATION PERIODS
# --------------------------------------------------
bins = [1999, 2004, 2010, 2016, 2021]
labels = ["1999–2004", "2005–2010", "2011–2016", "2017–2021"]

Alien_data["period"] = pd.cut(
    Alien_data["Year"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

# --------------------------------------------------
# AGGREGATE OBSERVATIONS
# --------------------------------------------------
period_counts = (
    Alien_data
    .groupby(["Country", "period"])
    .size()
    .reset_index(name="n_obs")
)

# Merge with map
med_obs = med_map.merge(
    period_counts,
    how='left',
    left_on='NAME',
    right_on='Country'
).fillna({"n_obs": 0})

# --------------------------------------------------
# COMPUTE CENTROIDS
# --------------------------------------------------
# Project original country geometries
med_map_proj = med_map.to_crs(epsg=3035)
# Representative points (guaranteed inside geometry)
rep_points_proj = med_map_proj.geometry.representative_point()
rep_points_lonlat = rep_points_proj.to_crs(epsg=4326)

med_map["x"] = rep_points_lonlat.x.values
med_map["y"] = rep_points_lonlat.y.values
#-----------
# COLORS & SCALE
# --------------------------------------------------
# Using 4 distinct steps from the viridis colormap
cmap = plt.get_cmap('viridis')
period_colors = {
    "1999–2004": cmap(0.1),  # Deep Purple
    "2005–2010": cmap(0.4),  # Blue/Teal
    "2011–2016": cmap(0.7),  # Green/Yellow
    "2017–2021": cmap(0.95) # Bright Yellow
}

size_scale = 0.06  # controls pie radius

# --------------------------------------------------
# PIE DRAWING FUNCTION
# --------------------------------------------------
def draw_pie(ax, x, y, values, colors, scale):
    total = sum(values)
    if total == 0:

        return

    start_angle = 0
    radius = np.sqrt(total) * scale

    for v, c in zip(values, colors):
        if v == 0:
            continue
        angle = 360 * v / total
        wedge = Wedge(
            (x, y),
            radius,
            start_angle,
            start_angle + angle,
            facecolor=c,
            edgecolor="black",
            linewidth=0.3,
            zorder=6
        )
        ax.add_patch(wedge)
        start_angle += angle


def draw_quartered_circle(ax, x, y, values, colors, scale):
    """
    Draws 4 fixed 90° quarters.
    Radius of each quarter ∝ sqrt(value)
    """
    angles = [(0, 90), (90, 180), (180, 270), (270, 360)]

    for (v, c, (a0, a1)) in zip(values, colors, angles):
        if v == 0:
            continue

        radius = np.sqrt(v) * scale
        wedge = Wedge(
            (x, y),
            radius,
            a0,
            a1,
            facecolor=c,
            edgecolor="black",
            linewidth=0.3,
            zorder=6
        )
        ax.add_patch(wedge)

# --------------------------------------------------
#PLOT SETTINGS
# --------------------------------------------------
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 7
})

fig, ax = plt.subplots(
    figsize=(8, 6),
    dpi=600,
    subplot_kw={"projection": ccrs.PlateCarree()}
)

pad = 5
# Mediterranean Sea geographic extent bounds
xmin = -6.0- pad
xmax = 36.5+ pad
ymin = 30.0- pad
ymax = 46.0

ax.set_extent([xmin, xmax, ymin, ymax])
ax.add_feature(cfeature.LAND, facecolor="0.85", zorder=0)
ax.add_feature(cfeature.COASTLINE, linewidth=0.3)
ax.add_feature(cfeature.BORDERS, linewidth=0.2)

# Plot countries
med_map.plot(ax=ax, color='lightgray', edgecolor='black', linewidth=0.3,zorder=1)

# --------------------------------------------------
#  DRAW PIE CIRCLES
# --------------------------------------------------
for country in med_map["NAME"]:

    x = med_map.loc[med_map["NAME"] == country, "x"].values[0]
    y = med_map.loc[med_map["NAME"] == country, "y"].values[0]

    g = med_obs[med_obs["NAME"] == country]

    values = [g[g["period"] == p]["n_obs"].sum() for p in labels]
    colors = [period_colors[p] for p in labels]

    draw_quartered_circle(ax, x, y, values, colors, size_scale)
# --------------------------------------------------
#LEGEND
# --------------------------------------------------
legend_elements = [
    Line2D([0], [0], marker='o', color='w',
           label=p, markerfacecolor=period_colors[p],
           markersize=6)
    for p in labels
]

ax.legend(
    handles=legend_elements,
    title="Observation period",
    loc="upper left",
    fontsize=7,
    title_fontsize=7,
    frameon=True
)

from matplotlib.patches import Circle

# --------------------------------------------------
# SIZE LEGEND (uses same radius formula)
# --------------------------------------------------
rounded_max = round(max_value, -3)
#  Position (bottom-left corner of map)
# Adjust these offsets based on your padding/extent
legend_x = xmin + 5
legend_y = ymin + 2

#Draw a single Quarter-Circle (matching your map style)
ref_radius = np.sqrt(rounded_max) * size_scale

legend_wedge = Wedge(
    (legend_x, legend_y),
    ref_radius,
    0, 90,             # Just one quarter (0 to 90 degrees)
    facecolor="gray",  # Neutral color for reference
    edgecolor="black",
    linewidth=0.5,
    alpha=0.7,
    zorder=10
)
ax.add_patch(legend_wedge)

#  Add the Label
ax.text(
    legend_x + ref_radius - 3,
    #legend_y + (ref_radius / 2),
    legend_y-0.8,
    f"{rounded_max:,} obs.",
    va="bottom",
    fontsize=4,
    fontweight="bold"
)

# --------------------------------------------------
# 10. GRIDLINES
# --------------------------------------------------
gl = ax.gridlines(
    draw_labels=True,
    linewidth=0.3,
    color="gray",
    alpha=0.3,
    linestyle="--"
)
gl.top_labels = False
gl.right_labels = False
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {"size": 7}
gl.ylabel_style = {"size": 7}

# --------------------------------------------------
# 11. EXPORT
# --------------------------------------------------
ax.patch.set_facecolor("white")
fig.patch.set_facecolor("white")
plt.title(
        f"Distribution of Observations 1999-2021",
        fontsize=10,
        #fontweight="bold",
        pad=3
    )

# fig.savefig(
#     your_savepath,
#     dpi=600,
#     bbox_inches="tight"
# )

"""Figure 3. Mediterranean environmental suitability and observation records.

The function below plots the suitability index for a selected year and can optionally
overlay the corresponding species observation records.
The suitability index ranges from 0 to 1.
"""

def Past_Med_Suitability_Observations(
    ds_past,
    year,
    log=False, # use only if want to plot in log scale
    obs_df=None,
    save_path=None
):
    """
    Plot the environmental suitability index for a selected year.

    Parameters
    ----------
    ds_past : xarray.Dataset
        Dataset containing the historical suitability index.
    year : int
        Year to display.
    log : bool, optional
        If True, use a logarithmic colour scale.
    obs_df : pandas.DataFrame, optional
        Observation table. Expected columns are 'longitude', 'latitude', and 'Year'.
    save_path : str or None, optional
        Output path. If None, the figure is not saved.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure.
    """

    # --- Font & style ---
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 7
    })

    da_year = ds_past.suitability.sel(time=year)

    fig, ax = plt.subplots(
        figsize=(8, 6),
        dpi=600,
        subplot_kw={'projection': ccrs.PlateCarree()}
    )

    # --- Map extent ---
    lon_min = float(ds_past.longitude.min())
    lon_max = float(ds_past.longitude.max())
    lat_min = float(ds_past.latitude.min())
    lat_max = float(ds_past.latitude.max())

    ax.set_extent([lon_min, lon_max, lat_min, lat_max])

    # --- Base map ---
    ax.add_feature(cfeature.LAND, facecolor="0.8", zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
    ax.add_feature(cfeature.BORDERS, linewidth=0.2)


    # --- Suitability plot ---
    norm = LogNorm(vmin=1e-3, vmax=1) if log else None

    im = da_year.plot(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap="OrRd",
        norm=norm,
        add_colorbar=False
    )

    # --- Colorbar INSIDE the map ---
        # Create the inset
    # 1. Create the inset
    cax = inset_axes(ax, width="3%", height="40%", loc="upper left",
                     borderpad=2,
                     bbox_to_anchor=(0.84, 0.04, 1, 1),
                     bbox_transform=ax.transAxes)

    # 2. Add a background rectangle (patch)
    rect = patches.Rectangle(
        #(0.01, 0.53), 0.15, 0.45, # (x, y), width, height
        (0.86, 0.53), 0.13, 0.45,
        transform=ax.transAxes,
        facecolor='white',
        edgecolor='black',
        linewidth=0.5,
        zorder=3
    )
    ax.add_patch(rect)


    # 2. Plot the colorbar
    cb = plt.colorbar(im, cax=cax)

    cb.ax.set_zorder(5) # Ensure it sits on top of the white box
    cb.set_label("Suitability Index", fontsize=6)
    cb.ax.tick_params(labelsize=8)

    # --- Gridlines with degree labels ---
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.3,
        color="gray",
        alpha=0.2,
        linestyle="--"
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {"size": 7}
    gl.ylabel_style = {"size": 7}

    # --- Scale bar (approximate, km) ---
    scale_km = 500
    lon_scale = lon_min + 0.05 * (lon_max - lon_min)
    lat_scale = lat_min + 0.05 * (lat_max - lat_min)

    ax.plot(
        [lon_scale, lon_scale + scale_km / 111],
        [lat_scale, lat_scale],
        transform=ccrs.PlateCarree(),
        color="k",
        linewidth=2
    )
    ax.text(
        lon_scale + scale_km / 222,
        lat_scale + 0.3,
        f"{scale_km} km",
        transform=ccrs.PlateCarree(),
        ha="center",
        va="bottom",
        fontsize=8
    )

    # --- Overlay observation points ---
    if obs_df is not None:
        obs_year = obs_df[obs_df["Year"] == year]

        ax.scatter(
            obs_year["longitude"],
            obs_year["latitude"],
            s=10,
            color="navy",
            edgecolor="white",
            linewidth=0.2,
            alpha=0.6,
            transform=ccrs.PlateCarree(),
            zorder=5,
            label="Observations"
        )

    # --- Year annotation (white box, top-right) ---
    ax.text(
        0.02, 0.95,
        str(year),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=12,
        fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="black",linewidth=0.4)#, boxstyle="round,pad=0.3")
    )

    # --- title---
    ax.set_title("Suitability Index", fontsize=12)

    if obs_df is not None:

        leg = ax.legend(loc='upper center', fontsize=8, edgecolor='k', frameon=True)
        # Set the linewidth on the frame object directly
        leg.get_frame().set_linewidth(0.4)


    if save_path is not None:
        fig.savefig(
            save_path,
            dpi=600,
            bbox_inches="tight"
        )

    plt.close(fig)
    return fig

"""Figure 4. Projected environmental suitability under future climate scenarios.

The function plots the suitability index for a selected year or averages it over
a specified period. The manuscript compares SSP2-4.5 and SSP5-8.5 across the
near-future (2025–2035), mid-century (2050–2060), and end-of-century (2085–2095)
periods. Individual panels are generated by calling the function with the relevant
dataset and time selection.
"""

# Single images produced with

def plot_Med_Suitability(
    ds,
    title,
    years,
    savepath=None
):

    """

    INPUT:
        ds : xarray Dataset provided in data section (either past-reanalysis or future projections)
        title : str, title of plot
        years   : temporal selection range(start_year,end_year)
        save_path : str or None
    """

    # --- Font & style  ---
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10
    })
    # ---- Temporal selection ----
    if np.isscalar(years):
        data = ds.suitability.sel(time=years)
        year_label = str(years)
    else:
        data = ds.suitability.sel(
            time=slice(years[0], years[-1])
        ).mean(dim="time", skipna=True)
        year_label = f"{years[0]}–{years[-1]} (mean)"


    # ---- Figure ----
    fig = plt.figure(figsize=(9, 6), dpi=600)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())


    # --- Map extent ---
    lon_min = float(ds.longitude.min())
    lon_max = float(ds.longitude.max())
    lat_min = float(ds.latitude.min())
    lat_max = float(ds.latitude.max())

    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    # --- Base map ---
    ax.add_feature(cfeature.LAND, facecolor="0.8", zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
    ax.add_feature(cfeature.BORDERS, linewidth=0.2)
    norm = plt.Normalize(vmin=0, vmax=1)
    # ---- Plot categories  ----
    im = data.plot(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap='OrRd',
        norm=norm,
        add_colorbar=False,
        add_labels=False
    )

    #  SMALL BOXED COLORBAR — UPPER LEFT

    cax = inset_axes(
        ax,
        width="2%",
        height="32%",
        loc="upper left",
        borderpad=1.2
    )

    cax.set_facecolor("none")
    cax.set_zorder(5)
    # White background box BEHIND the colorbar
    bg = FancyBboxPatch(
        (-0.35, -0.08),   # move slightly down/left
        5.5,              # wider box
        1.15,             # taller box
        transform=cax.transAxes,
        boxstyle="round,pad=0.04",
        facecolor="white",
        edgecolor="black",
        linewidth=0.5,
        clip_on=False,
        zorder=1
    )

    cax.add_patch(bg)
    cb = plt.colorbar(im, cax=cax, orientation="vertical")
    cb.set_ticks([0, 0.5, 1])
    cb.set_label("Suitability Index", fontsize=7)
    cb.ax.tick_params(labelsize=6)

    for spine in cax.spines.values():
        spine.set_visible(False)


    # --- Gridlines with degree labels ---
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.3,
        color="gray",
        alpha=0.5,
        linestyle="--"
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {"size": 8}
    gl.ylabel_style = {"size": 8}

    # --- Scale bar (approximate, km) ---
    scale_km = 500
    lon_scale = lon_min + 0.05 * (lon_max - lon_min)
    lat_scale = lat_min + 0.05 * (lat_max - lat_min)

    ax.plot(
        [lon_scale, lon_scale + scale_km / 111],
        [lat_scale, lat_scale],
        transform=ccrs.PlateCarree(),
        color="k",
        linewidth=2
    )
    ax.text(
        lon_scale + scale_km / 222,
        lat_scale + 0.3,
        f"{scale_km} km",
        transform=ccrs.PlateCarree(),
        ha="center",
        va="bottom",
        fontsize=8
    )

    # --- Year annotation (white box, top-right) ---

    ax.text(
        0.98, 0.98,
        str(year_label),
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=12,
        fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="black",linewidth=0.4)#, boxstyle="round,pad=0.3")
    )

    if savepath is not None:
        fig.savefig(savepath, dpi=600, bbox_inches="tight")

    plt.close(fig)
    return fig

"""Supplementary figure. Spatial distribution of suitability categories.

Suitability values are classified into four categories:
0: Low (0–0.25)
1: Medium (0.25–0.50)
2: Moderate (0.50–0.75)
3: High (0.75–1.00)

The function also calculates the percentage of the valid study area in each category,
using cosine-of-latitude weights as an approximation of grid-cell area.
"""

## SUPPORTING CODE FOR CATHEGORIZATION

def compute_area_percentages(cat, lat):
    """
    Calculate the area-weighted percentage occupied by each suitability category.

    Parameters
    ----------
    cat : xarray.DataArray
        Categorical suitability data (values 0–3); NaN values are excluded.
    lat : xarray.DataArray
        Latitude coordinate used to calculate cosine-of-latitude weights.

    Returns
    -------
    dict
        Dictionary mapping category labels to percentages of the valid study area.
    """

    # peso areale corretto
    weights = np.cos(np.deg2rad(lat))
    valid = cat.notnull()
    weights_2d = weights.broadcast_like(cat)

    total_area = weights_2d.where(valid).sum(
        dim=("latitude", "longitude")
    )
    #print(total_area)
    labels = {
        0: "Low (0–0.25)",
        1: "Medium (0.25–0.5)",
        2: "Moderate (0.5–0.75)",
        3: "High (>0.75)"
    }

    percentages = {}

    for k, label in labels.items():
        area_k = weights_2d.where(valid & (cat == k)).sum(
            dim=("latitude", "longitude")
        )
        percentages[label] = float(area_k / total_area * 100)
        #print(area_k)

    return percentages

def plot_Med_Suitability_Area_Cat(
    ds,
    title,
    years,
    savepath=None
):
    """
    Plot the spatial distribution of suitability categories.

    Parameters
    ----------
    ds : xarray.Dataset
        Dataset containing the suitability variable.
    title : str
        Scenario or dataset label used in the figure title.
    years : int or sequence of int
        A single year or a two-element period defining the temporal selection.
    savepath : str or None, optional
        Output path. If None, the figure is not saved.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure.
    """
    # --- Font & style ---
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10
    })
    # ---- Temporal selection ----
    if np.isscalar(years):
        data = ds.suitability.sel(time=years)
        year_label = str(years)
    else:
        data = ds.suitability.sel(
            time=slice(years[0], years[-1])
        ).mean(dim="time", skipna=True)
        year_label = f"{years[0]}–{years[-1]} (mean)"

    # ---- Clean invalid values ----
    data = data.where((data >= 0) & (data <= 1))

    # ---- Classification ----
    cat = xr.full_like(data, np.nan)
    cat = xr.where((data >= 0.0) & (data < 0.25), 0, cat)
    cat = xr.where((data >= 0.25) & (data < 0.5), 1, cat)
    cat = xr.where((data >= 0.5) & (data < 0.75), 2, cat)
    cat = xr.where(data >= 0.75, 3, cat)

    percentages = compute_area_percentages(cat, cat.latitude)

    # ---- Discrete colormap ----
    colors = ["green", "yellow", "orange", "red"]
    cmap = mcolors.ListedColormap(colors)
    bounds = [0, 1, 2, 3, 4]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    # ---- Figure ----
    fig = plt.figure(figsize=(9, 6), dpi=600)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())


    # --- Map extent ---
    lon_min = float(ds.longitude.min())
    lon_max = float(ds.longitude.max())
    lat_min = float(ds.latitude.min())
    lat_max = float(ds.latitude.max())

    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    # --- Base map ---
    ax.add_feature(cfeature.LAND, facecolor="0.8", zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
    ax.add_feature(cfeature.BORDERS, linewidth=0.2)

    # ---- Plot categories  ----
    im = cat.plot(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        norm=norm,
        add_colorbar=False,
        add_labels=False
    )

    #  SMALL BOXED COLORBAR — UPPER LEFT

    cax = inset_axes(
        ax,
        width="2%",
        height="32%",
        loc="upper left",
        borderpad=1.2
    )
    cax.set_facecolor("none")
    cax.set_zorder(5)

    for spine in cax.spines.values():
        spine.set_visible(False)

    # White background box BEHIND the colorbar
    bg = FancyBboxPatch(
        (-0.35, -0.08),   # move slightly down/left
        5.5,              # wider box
        1.15,             # taller box
        transform=cax.transAxes,
        boxstyle="round,pad=0.04",
        facecolor="white",
        edgecolor="black",
        linewidth=0.5,
        clip_on=False,
        zorder=1
    )

    cax.add_patch(bg)

    cb = plt.colorbar(
        im,
        cax=cax,
        ticks=[0.5, 1.5, 2.5, 3.5]
    )

    cb.ax.set_zorder(6)
    cb.ax.tick_params(labelsize=7)

    cb.ax.set_yticklabels([
        "Low",
        "Medium",
        "Moderate",
        "High"
    ])


    # --- Gridlines with degree labels ---
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.3,
        color="gray",
        alpha=0.5,
        linestyle="--"
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {"size": 8}
    gl.ylabel_style = {"size": 8}


    # --- Scale bar km ---
    scale_km = 500
    lon_scale = lon_min + 0.05 * (lon_max - lon_min)
    lat_scale = lat_min + 0.05 * (lat_max - lat_min)

    ax.plot(
        [lon_scale, lon_scale + scale_km / 111],
        [lat_scale, lat_scale],
        transform=ccrs.PlateCarree(),
        color="k",
        linewidth=2
    )
    ax.text(
        lon_scale + scale_km / 222,
        lat_scale + 0.3,
        f"{scale_km} km",
        transform=ccrs.PlateCarree(),
        ha="center",
        va="bottom",
        fontsize=8
    )

    # --- Year annotation---

    ax.text(
        0.98, 0.98,
        str(year_label),
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=12,
        fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="black",linewidth=0.4)#, boxstyle="round,pad=0.3")
    )
    # ---- Title ----
    ax.set_title(
        f"{title} suitability categories",
        fontsize=14,
        fontweight="bold",
        pad=12
    )

    #plt.tight_layout()
    if savepath is not None:
        fig.savefig(savepath, dpi=600, bbox_inches="tight")

    plt.close(fig)
    return fig

"""Figure 8. Baseline environmental conditions and projected changes.

The figure combines maps of the suitability index, surface potential temperature,
salinity, and dissolved molecular oxygen. The baseline period is 2010–2020.
Projected changes under SSP5-8.5 are calculated relative to this baseline for
the near-future (2025–2035), mid-century (2050–2060), and end-of-century
(2085–2095) periods.

Baseline environmental fields are based on Copernicus Marine Service reanalysis
data. Future environmental projections are based on the dataset by Kristiansen
and Butenschön (2024), available from Zenodo. The datasets are described in
the repository README and cited in the manuscript.

The plotting functions below generate the individual baseline and difference
maps; the multi-panel figure is assembled separately.
"""

def plot_Baseline_Climate(
    BASELINE,      # xarray Dataset (baseline)
    var,
    label,
    min_value,
    max_value,
    text,
    cmap_set=cmocean.cm.dense,

    title=None,
    save_path=None
    ):
    """
    Plot the baseline spatial distribution of an environmental variable.

    Parameters
    ----------
    BASELINE : xarray.Dataset
        Baseline environmental dataset, including the selected variable and time
        coordinate.
    var : str
        Variable name (e.g. 'thetao', 'so', or 'o2').
    label : str
        Colour-bar label, including the variable units.
    min_value, max_value : float
        Lower and upper limits of the colour scale.
    text : str
        Annotation displayed on the map.
    cmap_set : matplotlib colormap, optional
        Colormap used for the map.
    title : str or None, optional
        Figure title.
    save_path : str or None, optional
        Output path. If None, the figure is not saved.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure.
    """
    # --- Font & style ---
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10
    })


    # Baseline mean (fixed reference period)
    base = (
        BASELINE[var]
        .sel(time=slice(2010, 2020))
        .mean(dim="time", skipna=True)
    )

    # ---- Figure ----
    fig = plt.figure(figsize=(9, 6), dpi=600)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # --- Map extent ---
    lon_min = float(BASELINE.longitude.min())
    lon_max = float(BASELINE.longitude.max())
    lat_min = float(BASELINE.latitude.min())
    lat_max = float(BASELINE.latitude.max())

    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    # --- Base map ---
    ax.add_feature(cfeature.LAND, facecolor="0.8", zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
    ax.add_feature(cfeature.BORDERS, linewidth=0.2)

    # ---- Plot data ----
    im = base.plot(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap=cmap_set,
        vmin=min_value,
        vmax=max_value,
        add_colorbar=False,
        add_labels=False
    )

    #  SMALL BOXED COLORBAR — UPPER LEFT (same style as before)
    cax = inset_axes(
        ax,
        width="2%",
        height="32%",
        loc="upper left",
        borderpad=1.2
    )

    cax.set_facecolor("none")
    cax.set_zorder(5)
    # White background box BEHIND the colorbar
    bg = FancyBboxPatch(
        (-0.35, -0.08),   # move slightly down/left
        5.5,              # wider box
        1.15,             # taller box
        transform=cax.transAxes,
        boxstyle="round,pad=0.04",
        facecolor="white",
        edgecolor="black",
        linewidth=0.5,
        clip_on=False,
        zorder=1
    )

    cax.add_patch(bg)
    cb = plt.colorbar(im, cax=cax, orientation="vertical")
    #cb.set_ticks([0, 0.5, 1])
    cb.set_label(label, fontsize=7)
    cb.ax.tick_params(labelsize=6)

    for spine in cax.spines.values():
        spine.set_visible(False)


    # --- Gridlines with degree labels ---
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.3,
        color="gray",
        alpha=0.5,
        linestyle="--"
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {"size": 8}
    gl.ylabel_style = {"size": 8}


    # --- Scale bar (approximate, km) ---
    scale_km = 500
    lon_scale = lon_min + 0.05 * (lon_max - lon_min)
    lat_scale = lat_min + 0.05 * (lat_max - lat_min)

    ax.plot(
        [lon_scale, lon_scale + scale_km / 111],
        [lat_scale, lat_scale],
        transform=ccrs.PlateCarree(),
        color="k",
        linewidth=2
    )
    ax.text(
        lon_scale + scale_km / 222,
        lat_scale + 0.3,
        f"{scale_km} km",
        transform=ccrs.PlateCarree(),
        ha="center",
        va="bottom",
        fontsize=8
    )
    # --- Year annotation (white box, top-right) ---
    ax.text(
        0.98, 0.98,
        text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=12,
        fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="black",linewidth=0.4)#, boxstyle="round,pad=0.3")
    )
    # ---- Title ----
    if title is not None :
        ax.set_title(
            title,
            fontsize=14,
            fontweight="bold",
            pad=12
        )

    #plt.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=600, bbox_inches="tight")

    plt.close(fig)
    return fig

def plot_Difference_Baseline_Climate(
    BASELINE,      # xarray Dataset (baseline)
    ds,        # xarray Dataset (future)
    var,
    min_value,
    max_value,
    years,
    label,
    cmap_set=cmocean.cm.delta,
    title=None,
    scenario=True,
    save_path=None
    ):
    """
    Plot the difference between future and baseline environmental conditions.

    Parameters
    ----------
    BASELINE : xarray.Dataset
        Baseline environmental dataset.
    ds : xarray.Dataset
        Future projection dataset.
    var : str
        Variable name (e.g. 'thetao', 'so', or 'o2').
    min_value, max_value : float
        Lower and upper limits of the colour scale.
    years : int or sequence of int
        A single year or a two-element period defining the future time selection.
    label : str
        Colour-bar label, including the difference units.
    cmap_set : matplotlib colormap, optional
        Colormap used for the difference map.
    title : str or None, optional
        Figure title.
    scenario : bool, optional
        If True, annotate the selected period as an SSP5-8.5 projection;
        otherwise, annotate the map as a baseline bias.
    save_path : str or None, optional
        Output path. If None, the figure is not saved.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure.
    """
    # --- Font & style (journal-friendly) ---
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10
    })
    absolute_min = np.nanmin([BASELINE[var].min(), ds[var].min()])
    absolute_max = np.nanmax([BASELINE[var].max(), ds[var].max()])
    print(absolute_min)
    print(absolute_max)
    # ---- Selezione temporale ----
    if np.isscalar(years):
        data_fut = ds[var].sel(time=years)
        year_label = str(years)
    else:
        data_fut = ds[var].sel(time=slice(years[0], years[1])).mean(dim="time", skipna=True)
        year_label = f"{years[0]}–{years[-1]} (mean)"

    # Baseline mean (fixed reference period)
    base = (
        BASELINE[var]
        .sel(time=slice(2010, 2020))
        .mean(dim="time", skipna=True)
    )

    # Interpolate to baseline
    data_fut = data_fut.interp(
        latitude=base.latitude,
        longitude=base.longitude,
        method="nearest"
    )

    diff = data_fut - base

    # Safety check
    if diff.count() == 0:
        raise ValueError("No valid data to plot. Check time coverage and NaNs.")

    # ---- Figure ----
    fig = plt.figure(figsize=(9, 6), dpi=600)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())


    # --- Map extent ---
    lon_min = float(ds.longitude.min())
    lon_max = float(ds.longitude.max())
    lat_min = float(ds.latitude.min())
    lat_max = float(ds.latitude.max())

    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    # --- Base map ---
    ax.add_feature(cfeature.LAND, facecolor="0.8", zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
    ax.add_feature(cfeature.BORDERS, linewidth=0.2)


    # ---- Plot categories (NO colorbar here) ----
    im = diff.plot(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap=cmap_set,
        norm=plt.Normalize(vmin=min_value, vmax=max_value),
        add_colorbar=False,
        add_labels=False
    )

    #  SMALL BOXED COLORBAR — UPPER LEFT
    cax = inset_axes(
        ax,
        width="2%",
        height="32%",
        loc="upper left",
        borderpad=1.2
    )

    cax.set_facecolor("none")
    cax.set_zorder(5)
    # White background box BEHIND the colorbar
    bg = FancyBboxPatch(
        (-0.35, -0.08),   # move slightly down/left
        5.5,              # wider box
        1.15,             # taller box
        transform=cax.transAxes,
        boxstyle="round,pad=0.04",
        facecolor="white",
        edgecolor="black",
        linewidth=0.5,
        clip_on=False,
        zorder=1
    )

    cax.add_patch(bg)
    cb = plt.colorbar(im, cax=cax, orientation="vertical")
    #cb.set_ticks([0, 0.5, 1])
    cb.set_label(label, fontsize=7)
    cb.ax.tick_params(labelsize=6)

    for spine in cax.spines.values():
        spine.set_visible(False)


    # --- Gridlines with degree labels ---
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.3,
        color="gray",
        alpha=0.5,
        linestyle="--"
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {"size": 8}
    gl.ylabel_style = {"size": 8}


    # --- Scale bar (approximate, km) ---
    scale_km = 500
    lon_scale = lon_min + 0.05 * (lon_max - lon_min)
    lat_scale = lat_min + 0.05 * (lat_max - lat_min)

    ax.plot(
        [lon_scale, lon_scale + scale_km / 111],
        [lat_scale, lat_scale],
        transform=ccrs.PlateCarree(),
        color="k",
        linewidth=2
    )
    ax.text(
        lon_scale + scale_km / 222,
        lat_scale + 0.3,
        f"{scale_km} km",
        transform=ccrs.PlateCarree(),
        ha="center",
        va="bottom",
        fontsize=8
    )

    # --- Year annotation (white box, top-right) ---
    if scenario==True:

        ax.text(
            0.98, 0.98,
            'SSP5-8.5'+' '+str(year_label),
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=12,
            fontweight="bold",
            bbox=dict(facecolor="white", edgecolor="black",linewidth=0.4)#, boxstyle="round,pad=0.3")
        )
    else:
                ax.text(
            0.98, 0.98,
            'Bias GCMs-CMEMS',
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=12,
            fontweight="bold",
            bbox=dict(facecolor="white", edgecolor="black",linewidth=0.4)#, boxstyle="round,pad=0.3")
        )
    # ---- Title ----
    if title is not None :
        ax.set_title(
            title,
            fontsize=14,
            fontweight="bold",
            pad=12
        )

    #plt.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=600, bbox_inches="tight")

    plt.close(fig)
    return fig