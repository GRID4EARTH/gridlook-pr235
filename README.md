# Gridlook preview: d70-t/gridlook#235 (multi-resolution levels)

**Temporary preview, not a release.** This is a static production build of the draft pull request
[d70-t/gridlook#235](https://github.com/d70-t/gridlook/pull/235) ("zoom-driven level selection and view-based
loading for multiscales datasets", by espg), commit `f45b093`, built on 2026-10-11 with `npx vite build`.
Source maps and the local test data are left out. Gridlook is MIT-licensed (see the upstream repository).

It is published so that GRID4EARTH can try multi-resolution HEALPix products in Gridlook before #235 is merged.
Discussion: [GRID4EARTH/project-guidelines#21](https://github.com/GRID4EARTH/project-guidelines/issues/21).

## Open

<https://grid4earth.eu/gridlook-pr235/#https://data.grid4earth.eu/converted/sentinel-2-l1c-multires/mean-l20-l12/S2C_MSIL1C_20250514T104641_N0511_R051_T31UDQ_20250514T143130.zarr/measurements/reflectance>

Zoom in on Paris: with "Pick the level from the zoom" on (Variable card), the level switches from 13 to 20.

## Dataset list and default dataset

Same as grid4earth.eu/gridlook (GRID4EARTH/gridlook#2, #6). The "Open dataset" list is read from
`https://data.grid4earth.eu/gridlook-catalog.json`, which `stac-scraper gridlook-catalog` writes with the STAC
metadata (GRID4EARTH/stac-scraper#28): one checked example per STAC collection except the mirrors. Opened without a
dataset in the URL, this build shows ERA5 2 m temperature (`auxiliary/reanalysis-era5-complete`).

These are the only changes to the #235 source: `DEFAULT_CATALOG`, `DEFAULT_DATASET` and a default `varname` in
`src/views/HashGlobeView.vue`, and `public/static/catalog.json` removed.

## Update

Rebuild the pull request and replace the files:

```bash
npm ci && npx vite build
rsync -a --delete --exclude testdata --exclude '*.map' --exclude .git --exclude README.md --exclude screenshots --exclude .nojekyll dist/ <this repository>/
```

Delete this repository once #235 is merged and deployed at <https://grid4earth.eu/gridlook/>.
