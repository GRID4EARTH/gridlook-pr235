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

# (title, path under data.grid4earth.eu, date checked in Gridlook #235 build f45b093)
DATASETS = [
    (
        "Sentinel-2 L1C converted - S2C 2025-04-12 T32TPS",
        "converted/sentinel-2-l1c/S2C_MSIL1C_20250412T101041_N0511_R022_T32TPS_20250412T134850.zarr",
        "2026-10-11",
    ),
    (
        "Sentinel-2 L2A converted - S2C 2025-06-13 T31UDQ (Paris)",
        "converted/sentinel-2-l2a/S2C_MSIL2A_20250613T104641_N0511_R051_T31UDQ_20250613T134507.zarr",
        "2026-10-11",
    ),
    (
        "Sentinel-2 L1C multi-resolution (mean-l20-l12) - S2C 2025-04-12 T32TPS",
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
    for title, path, checked in DATASETS:
        url = f"{GATEWAY}/{path}"
        if not reachable(url):
            sys.exit(f"not reachable: {url}")
        datasets.append({"title": title, "url": url, "tag": "healpix"})
        print(f"ok ({checked}): {title}", file=sys.stderr)
    catalog = {"type": "gridlook_catalog", "title": "GRID4EARTH", "datasets": datasets}
    with open(sys.argv[1], "w") as f:
        json.dump(catalog, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
