#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 14:50:34 2026

@author: f055
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



# ==========================================================
# USER SETTINGS
# ==========================================================

filename = "data/soi_3dp.dat"

rm_window = 3               # running mean length (months)

threshold = 1.0             # e.g. 1 or 2
threshold_type = "sd"       # "sd" or "absolute"

#line_colour = "#0055A4"
#monthly_colour = "0.80"

monthly_colour = "0.75"
line_colour = "#004B87"

figsize = (12, 10)

# ==========================================================
# READ CRU SOI FILE
# ==========================================================

dates = []
values = []

with open(filename) as f:

    for line in f:

        parts = line.split()

        year = int(parts[0])

        monthly = np.array(parts[1:13], dtype=float)

        for month in range(12):

            val = monthly[month]

            if val <= -99:
                continue

            dates.append(pd.Timestamp(year=year,
                                      month=month + 1,
                                      day=1))

            values.append(val)

df = pd.DataFrame(
    {
        "date": dates,
        "soi": values
    }
)

# ----------------------------------------------------------
# reverse sign
# El Niño now positive
# ----------------------------------------------------------

#df["enso"] = -df["soi"]
# Actually now I just keep the original sign and reverse the y-axis


# ==========================================================
# RUNNING MEAN
# ==========================================================

df["smooth"] = (
    df["soi"]
    .rolling(
        rm_window,
        center=True,
        min_periods=rm_window    # IMPORTANT: this truncates near the ends (=1 would not)
    )
    .mean()
)

# ==========================================================
# THRESHOLD
# ==========================================================

if threshold_type.lower() == "sd":
    thr = threshold * df["smooth"].std()
else:
    thr = threshold

print(f"Threshold = {thr:.3f}")

# ==========================================================
# SPLIT INTO THREE PANELS
# ==========================================================

n = len(df)

#segments = [
#    ("1920-1979", "1920-01-01", "1979-12-31"),
#    ("1860-1919", "1860-01-01", "1919-12-31"),
#    ("1980-present", "1980-01-01", df["date"].max())
#]

segments = [
    ("1865-1920", "1865-01-01", "1920-01-01"),
    ("1920-1975", "1920-01-01", "1975-01-01"),
    ("1975-present", "1975-01-01", "2030-01-01")
]

# ==========================================================
# Label some events
# ==========================================================

# Specify event label and period within which to search for peak

#events = {
#    "1982-83": ("1982-01-01", "1984-01-01"),
#    "1877-78": ("1877-01-01", "1879-01-01"),
#    "1997-98": ("1997-01-01", "1999-01-01"),
#    "2015-16": ("2015-01-01", "2017-01-01"),
#    "2026":    ("2025-01-01", "2027-12-31"),
#}

events = {
    "1877-78": ("1877-01-01", "1879-01-01"),
    "1896-97": ("1896-01-01", "1898-01-01"),
    "1905-06": ("1905-01-01", "1907-01-01"),
    "1940-42": ("1940-01-01", "1943-01-01"),
    "1982-83": ("1982-01-01", "1984-01-01"),
    "1997-98": ("1997-01-01", "1999-01-01"),
    "2026":    ("2025-01-01", "2027-12-31"),
}



# ==========================================================
# PLOT
# ==========================================================

fig, axes = plt.subplots(
    3,
    1,
    figsize=figsize,
    sharey=True
)

for ax, (label, start, end) in zip(axes, segments):

    seg = df[
        (df["date"] >= start) &
        (df["date"] <= end)
    ]

    panel_start = pd.Timestamp(start)
    panel_end = pd.Timestamp(end)

    # Monthly values
    ax.plot(
        seg["date"],
        seg["soi"],
        color=monthly_colour,
        lw=0.8,
        zorder=1
    )

    # Ensure all panels use the same y-axis ranges
    ax.set_ylim(-4.5, 4.5)
 
    # Reverse axis so El Nino are upwards
    ax.invert_yaxis()

    # Use this option to start/end at specified start/end years even if data doesn't cover whole period
    ax.set_xlim(panel_start,panel_end)
    
    # Use this option to shorten x-axis ranges to match period spanned by data
    # even though it may make the segments cover different lengths
    #ax.set_xlim(
    #    seg["date"].iloc[0],
    #    seg["date"].iloc[-1]
    #)
    
    # Choose nice tick intervals
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # Running mean
    ax.plot(
        seg["date"],
        seg["smooth"],
        color=line_colour,
        lw=2.2,
        zorder=3
    )

    # Threshold lines
    ax.axhline(
        thr,
        color="blue",
        ls="--",
        lw=1
    )

    ax.axhline(
        -thr,
        color="red",
        ls="--",
        lw=1
    )

    # Positive exceedance shading
    ax.fill_between(
        seg["date"],
        thr,
        seg["smooth"],
        where=(seg["smooth"] >= thr),
        color="blue",
        alpha=0.25,
        interpolate=True,
        zorder=2
    )

    # Negative exceedance shading
    ax.fill_between(
        seg["date"],
        -thr,
        seg["smooth"],
        where=(seg["smooth"] <= -thr),
        color="red",
        alpha=0.25,
        interpolate=True,
        zorder=2
    )

    ax.axhline(
        0,
        color="black",
        lw=0.6
    )

    ax.grid(
        axis="y",
        alpha=0.25
    )
    
    # Label panel with time period it covers
    ax.text(
        0.01, 0.88,
        label,
        transform=ax.transAxes,
        fontsize=12,
        fontweight="bold",
        color="0.25",
        ha="left",
        va="top"
        )

    # Now label some ENSO events

    for event_label, (event_start, event_end) in events.items():

        event_start = pd.Timestamp(event_start)
        event_end   = pd.Timestamp(event_end)

        # skip if event not in this panel
        if event_end < panel_start or event_start > panel_end:
            continue

        event = df[
            (df["date"] >= event_start) &
            (df["date"] <= event_end)
        ]

        if len(event) == 0:
            continue

        idx = event["smooth"].idxmin()

        x = df.loc[idx, "date"]
        y = df.loc[idx, "smooth"]

        ax.text(
            x,
#            y + 0.35,   # label just above peak
            -3.9,        # label just below upper axis
            event_label,
            ha="center",
            va="bottom",
            fontsize=9,
            color="darkred",
            fontweight="bold"
        )





axes[1].set_ylabel(
    f"Reversed SOI ({rm_window}-month mean)"
)

axes[0].set_title(
    "CRU/Jones Southern Oscillation Index\n"
    "(inverted y-axis: El Niño upwards)"
)

fig.text(
    0.98, 0.985,
    "Graphic: CRU, UEA",
    ha="right",
    va="top",
    color="0.4",
    fontsize=12
)

# Keep text editable in PDF output
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": True,
    "axes.spines.right": True
})

plt.tight_layout()

plt.show()


#%% Now make a new plot with a composite of El Nino events, aligned by peak

# Define event labels and time periods to search for peak
# This list couild be different to the previous list

events = {
    "1877-78": ("1877-01-01", "1879-01-01"),
    "1896-97": ("1896-01-01", "1898-01-01"),
    "1905-06": ("1905-01-01", "1907-01-01"),
    "1940-42": ("1940-01-01", "1943-01-01"),
    "1982-83": ("1982-01-01", "1984-01-01"),
    "1997-98": ("1997-01-01", "1999-01-01"),
    "2026":    ("2025-01-01", "2027-12-31"),
}

# For each event, find the peak of the smoothed SOI series

event_series = {}

for label, (start, end) in events.items():

    event = df[
        (df["date"] >= start) &
        (df["date"] <= end)
    ]

    peak_idx = event["smooth"].idxmin()

    peak_date = df.loc[peak_idx, "date"]
    
    # 24 months either side
    window_start = peak_date - pd.DateOffset(months=24)
    window_end   = peak_date + pd.DateOffset(months=24)

    comp = df[
        (df["date"] >= window_start) &
        (df["date"] <= window_end)
    ].copy()

    # months relative to peak
    comp["month_rel"] = (
        (comp["date"].dt.year - peak_date.year) * 12 +
        (comp["date"].dt.month - peak_date.month)
    )

    event_series[label] = comp

# Now plot a composite of these events, aligned to the peak value

fig, ax = plt.subplots(figsize=(10, 6))

colours = [
    "#8c510a",
    "#bf812d",
    "#dfc27d",
    "#35978f",
    "#01665e",
    "#003c30",
    "#7f0000",
]

for colour, (label, comp) in zip(colours, event_series.items()):

    lw = 4.0 if label == "2026" else 2.0
    zorder = 10 if label == "2026" else 1
    alpha=1.0 if label == "2026" else 0.7

    ax.plot(
        comp["month_rel"],
        comp["smooth"],
        lw=lw,
        color=colour,
        zorder=zorder,
        alpha=alpha,
        label=label
    )

ax.axvline(
    0,
    color="0.4",
    lw=1.2,
    ls="--"
)

ax.axhline(
    0,
    color="black",
    lw=0.8
)

ax.set_xlim(-24, 24)
ax.set_xlabel("Months relative to peak SOI")

# Reverse axis so El Nino are upwards
ax.invert_yaxis()
ax.set_ylabel(f"{rm_window}-month mean SOI (inverted y-axis)")

ax.legend(
    frameon=False,
    ncol=2
)

ax.grid(
    axis="y",
    alpha=0.25
)

fig.text(
    0.98,
    0.02,
    "Graphic: CRU, UEA",
    ha="right",
    va="bottom",
    color="0.55",
    fontsize=9
)

plt.tight_layout()
plt.show()

#%% Now make a new plot with a composite of El Nino events, aligned by January nearest peak

# Define event labels and time periods to search for peak
# This list couild be different to the previous list

events = {
    "1877-78": ("1877-01-01", "1879-01-01"),
    "1896-97": ("1896-01-01", "1898-01-01"),
    "1905-06": ("1905-01-01", "1907-01-01"),
    "1940-42": ("1940-01-01", "1943-01-01"),
    "1982-83": ("1982-01-01", "1984-01-01"),
    "1997-98": ("1997-01-01", "1999-01-01"),
    "2026":    ("2025-01-01", "2027-12-31"),
}

# For each event, find the peak of the smoothed SOI series

event_series = {}

for label, (start, end) in events.items():

    event = df[
        (df["date"] >= start) &
        (df["date"] <= end)
    ]

    peak_idx = event["smooth"].idxmin()

    peak_date = df.loc[peak_idx, "date"]
    
    if peak_date.month >= 7:
        centre_date = pd.Timestamp(
            peak_date.year + 1, 1, 1
        )
    else:
        centre_date = pd.Timestamp(
            peak_date.year, 1, 1
        )
    peak_date=centre_date

    # 24 months either side
    window_start = peak_date - pd.DateOffset(months=24)
    window_end   = peak_date + pd.DateOffset(months=24)

    comp = df[
        (df["date"] >= window_start) &
        (df["date"] <= window_end)
    ].copy()

    # months relative to peak
    comp["month_rel"] = (
        (comp["date"].dt.year - peak_date.year) * 12 +
        (comp["date"].dt.month - peak_date.month)
    )

    event_series[label] = comp

# Now plot a composite of these events, aligned to the peak value

fig, ax = plt.subplots(figsize=(10, 6))

# Option: use hard-coded colours
#colours = [
#    "#8c510a",
#    "#bf812d",
#    "#dfc27d",
#    "#35978f",
#    "#01665e",
#    "#003c30",
#    "#7f0000",
#]

# Option: use pre-defined qualitative colour map
#cmap = plt.get_cmap("tab20c")
#colours = [cmap(i) for i in range(len(events))]

#for colour, (label, comp) in zip(colours, event_series.items()):
#
#    ax.plot(
#        comp["month_rel"],
#        comp["smooth"],
#        lw=2.5,
#        alpha=0.8,
#        color=colour,
#        label=label
#    )


# Option: use shades of one colour for all previous events and
# then emphasize current event
cmap = plt.get_cmap("Greys")

n_hist = len(events) - 1

hist_colours = cmap(
    np.linspace(0.35, 0.85, n_hist)
)

hist_labels = [e for e in events if e != "2026"]

for colour, label in zip(hist_colours, hist_labels):

    ax.plot(
        event_series[label]["month_rel"],
        event_series[label]["smooth"],
        color=colour,
        lw=1.8,
        alpha=0.9,
        zorder=1,
        label=label
    )

ax.plot(
    event_series["2026"]["month_rel"],
    event_series["2026"]["smooth"],
    color="crimson",
    lw=3.5,
    zorder=10,
    label="2026"
)


#ax.axvline(
#    0,
#    color="0.4",
#    lw=1.2,
#    ls="--"
#)

# Add vertical markers for calendar year boundaries

for x in [-24, -12, 0, 12, 24]:

    ax.axvline(
        x,
        color="0.5",
        lw=0.8,
        zorder=0
    )

ax.axhline(
    0,
    color="0.5",
    lw=0.8
)

# Make nice x-axis

month_labels = [
    "J","F","M","A","M","J","J","A","S","O","N","D"
]

xticks = np.arange(-24, 25)

xticklabels = [
    month_labels[(m % 12)]
    for m in xticks
]

ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)

ax.set_xlim(-24, 24)

ax.set_xlabel("Months relative to January closest to peak SOI")

# Reverse axis so El Nino are upwards
ax.invert_yaxis()
ax.set_ylabel(f"{rm_window}-month mean SOI (inverted y-axis)")

ax.legend(
    frameon=False,
    ncol=2
)

ax.grid(
    axis="y",
    alpha=0.25
)

fig.text(
    0.98,
    0.02,
    "Graphic: CRU, UEA",
    ha="right",
    va="bottom",
    color="0.55",
    fontsize=9
)

plt.tight_layout()
plt.show()


#%% Now make a new plot just of the July 3-month running mean values
# (i.e. ending Jun-Aug mean of current year).

july = df[df["date"].dt.month == 7].copy()



fig, ax = plt.subplots(figsize=(12, 4))

ax.vlines(
    july["date"],
    0,
    july["smooth"],
    color="#004B87",
    lw=1
)

ax.scatter(
    july["date"],
    july["smooth"],
    color="#004B87",
    s=20,
    zorder=3
)


# Reverse axis so El Nino are upwards
ax.invert_yaxis()
ax.set_ylabel(f"{rm_window}-month mean SOI (inverted y-axis)")
ax.set_title(
    "CRU SOI 3-month means centred on July"
)

ax.axhline(0, color="black", lw=0.8)

highlight_years = [
    2026
]

for yr in highlight_years:

    sel = july[july["date"].dt.year == yr]

    if len(sel):

        ax.scatter(
            sel["date"],
            sel["smooth"],
            s=40,
            color="crimson",
            zorder=5
        )

        ax.text(
            sel["date"].iloc[0],
            sel["smooth"].iloc[0],
            "  "+str(yr),
            ha="left",
            va="center",
            color="crimson",
            fontsize=10
        )

# Draw horiiz line from current year back to the start

sel = july[july["date"].dt.year == 2026]

x2026 = sel["date"].iloc[0]
y2026 = sel["smooth"].iloc[0]

ax.hlines(
    y=y2026,
    xmin=july["date"].min(),
    xmax=x2026,
    color="crimson",
    lw=0.8,
    alpha=0.5
)

fig.text(
    0.98, 0.93,
    "Graphic: CRU, UEA",
    ha="right",
    va="bottom",
    fontsize=9,
    color="0.55"
)


plt.tight_layout()
plt.show()

