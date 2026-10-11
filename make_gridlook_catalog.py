"""Write the Gridlook catalog (static/catalog.json) for the GRID4EARTH instance.

One example dataset per bucket folder, each opened in Gridlook and checked to
plot before it is listed here (rule agreed with the user on 2026-10-11).
To add a folder: pick one store with data, open it in Gridlook, check that it
plots, then add an entry with the date of the check.

Plain converted stores are listed at their root: Gridlook shows the level
groups (measurements/reflectance/17, 19, 20) in a group selector. Multires
stores are listed at measurements/reflectance, the group carrying the
multiscales layout, so that Gridlook picks the level from the zoom.

Usage: python -I make_gridlook_catalog.py OUT.json
"""

import json
import subprocess
import sys

GATEWAY = "https://data.grid4earth.eu"

# (title, description, path under data.grid4earth.eu, date checked in Gridlook)
# Gridlook shows the title on one truncated line (on a phone ~20 characters),
# so it starts with what differs between entries; the rest goes in the
# description, which wraps.
DATASETS = [
    (
        "S2 L1C - T32TPS 2025-04-12",
        "converted/sentinel-2-l1c, 13 bands. Pick a level group: 20 (10 m bands), "
        "19 (20 m bands), 17 (60 m bands).",
        "converted/sentinel-2-l1c/S2C_MSIL1C_20250412T101041_N0511_R022_T32TPS_20250412T134850.zarr",
        "2026-10-11",
    ),
    (
        "S2 L2A - Paris T31UDQ 2025-06-13",
        "converted/sentinel-2-l2a. Pick a level group: 20 (10 m bands), 19 and 17 "
        "(native bands plus the ESA resampled copies).",
        "converted/sentinel-2-l2a/S2C_MSIL2A_20250613T104641_N0511_R051_T31UDQ_20250613T134507.zarr",
        "2026-10-11",
    ),
    (
        "S2 L1C multires - T32TPS 2025-04-12",
        "converted/sentinel-2-l1c-multires/mean-l20-l12. Experimental: each band "
        "starts at its native level, coarser levels are the mean of the finer one. "
        "Pick the level (12-20) by hand here; switching with the zoom needs "
        "d70-t/gridlook#235.",
        "converted/sentinel-2-l1c-multires/mean-l20-l12/"
        "S2C_MSIL1C_20250412T101041_N0511_R022_T32TPS_20250412T134850.zarr/measurements/reflectance",
        "2026-10-11",
    ),
]


def reachable(url):
    """The group's zarr.json answers (catches typos and deleted stores)."""
    return subprocess.run(
        ["curl", "-sfo", "/dev/null", "--retry", "2", f"{url}/zarr.json"]
    ).returncode == 0


def main():
    datasets = []
    for title, description, path, checked in DATASETS:
        url = f"{GATEWAY}/{path}"
        if not reachable(url):
            sys.exit(f"not reachable: {url}")
        datasets.append(
            {"title": title, "description": description, "url": url, "tag": "healpix"}
        )
        print(f"ok ({checked}): {title}", file=sys.stderr)
    catalog = {"type": "gridlook_catalog", "title": "GRID4EARTH", "datasets": datasets}
    with open(sys.argv[1], "w") as f:
        json.dump(catalog, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
