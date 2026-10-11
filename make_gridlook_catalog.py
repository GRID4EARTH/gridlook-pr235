"""Write the Gridlook catalog (static/catalog.json) for the GRID4EARTH instance.

One example dataset per bucket folder, each opened in Gridlook and checked to
plot before it is listed here (rule agreed with the user on 2026-10-11).
To add a folder: pick one store with data, open it in Gridlook, check that it
plots, then add an entry with the date of the check.

Plain stores are listed at their root: Gridlook shows the level
groups (measurements/reflectance/17, 19, 20) in a group selector. Multires
stores are listed at measurements/reflectance, the group carrying the
multiscales layout, so that Gridlook picks the level from the zoom.

Usage: python -I make_gridlook_catalog.py OUT.json
"""

import json
import subprocess
import sys

GATEWAY = "https://data.grid4earth.eu"

# One entry per STAC collection except the mirrors (2026-10-11, user):
# (title, description, path under data.grid4earth.eu, variable to open first
# or None, date checked to plot on grid4earth.eu/gridlook).
# Gridlook shows the title on one truncated line (on a phone ~20 characters),
# so it starts with what differs between entries; the rest goes in the
# description, which wraps. Left out: auxiliary/copernicus-dem-glo-30 (27e9
# cells, Gridlook shows no data).
BIG = "Large: takes about a minute and over 1 GB of memory to load."
DATASETS = [
    (
        "ERA5 - 2 m temperature 2018-05-04 21:00",
        "auxiliary/reanalysis-era5-complete: global, HEALPix level 7 on the "
        "WGS84 ellipsoid. Other variables in measurements/enda and measurements/oper.",
        "auxiliary/reanalysis-era5-complete/"
        "S00__ADF_ECMWA_20180504T210000_20180504T210000_20260619T111831.zarr",
        "measurements/enda/t2m",
        "2026-10-11",
    ),
    (
        "CAMS EAC4 - AOD 550 nm 2018-05-04 21:00",
        "auxiliary/cams-global-reanalysis-eac4: global aerosol optical depth, "
        "HEALPix level 6 on the WGS84 ellipsoid.",
        "auxiliary/cams-global-reanalysis-eac4/"
        "S00__ADF_CAMSA_20180504T210000_20180504T210000_20260619T111832.zarr",
        None,
        "2026-10-11",
    ),
    (
        "S2 L1C - T32TPS 2025-04-12",
        "converted/sentinel-2-l1c, 13 bands. Pick a level group: 20 (10 m bands), "
        "19 (20 m bands), 17 (60 m bands).",
        "converted/sentinel-2-l1c/S2C_MSIL1C_20250412T101041_N0511_R022_T32TPS_20250412T134850.zarr",
        None,
        "2026-10-11",
    ),
    (
        "S2 L2A - Paris T31UDQ 2025-06-13",
        "converted/sentinel-2-l2a. Pick a level group: 20 (10 m bands), 19 and 17 "
        "(native bands plus the ESA resampled copies).",
        "converted/sentinel-2-l2a/S2C_MSIL2A_20250613T104641_N0511_R051_T31UDQ_20250613T134507.zarr",
        None,
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
        None,
        "2026-10-11",
    ),
    (
        "S3 OLCI EFR - 2026-01-17",
        "converted/sentinel-3-olci-l1-efr: one granule, HEALPix level 15. " + BIG,
        "converted/sentinel-3-olci-l1-efr/"
        "S3A_OL_1_EFR____20260117T092230_20260117T092438_20260118T102513_0128_135_093_1980_PS1_O_NT_004_psf.zarr",
        None,
        "2026-10-11",
    ),
    (
        "S3 SLSTR RBT - 2026-01-07 night",
        "converted/sentinel-3-slstr-l1-rbt: night granule, opens on the S8 "
        "brightness temperature (10.85 um, nadir); the radiance bands are empty at night.",
        "converted/sentinel-3-slstr-l1-rbt/"
        "S3A_SL_1_RBT____20260107T200924_20260107T201224_20260107T223844_0180_134_342_0900_PS1_O_NR_004_psf.zarr",
        "measurements/inadir/s8_bt_in",
        "2026-10-11",
    ),
    (
        "S2 L2A reprocessed - T32TPS 2025-04-12",
        "reprocessed/sentinel-2-l2a. Pick a level group: 20, 19, 17.",
        "reprocessed/sentinel-2-l2a/S2C_MSIL2A_20250412T101041_N0511_R022_T32TPS_20250412T154117.zarr",
        None,
        "2026-10-11",
    ),
    (
        "S3 synergy reprocessed - 2026-09-15",
        "reprocessed/sentinel-3-synergy: OLCI and SLSTR radiances of one overpass "
        "on a common HEALPix level 15 grid. " + BIG,
        "reprocessed/sentinel-3-synergy/synergy_20260915T101708_psf_level15.zarr",
        None,
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
    for title, description, path, varname, checked in DATASETS:
        url = f"{GATEWAY}/{path}"
        if not reachable(url):
            sys.exit(f"not reachable: {url}")
        # Gridlook reads "::key=value" after the store URL as view parameters
        if varname:
            url += f"::varname={varname}"
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
