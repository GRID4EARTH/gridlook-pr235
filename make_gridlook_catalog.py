"""Build a Gridlook catalog (static/catalog.json) of the GRID4EARTH HEALPix data.

Sources:
- every item of the STAC API except the eopf-mirror collections (UTM, not HEALPix);
- the multi-resolution test stores under converted/*-multires/<method>/ (not catalogued yet).

For each store, the root consolidated metadata is searched for groups that
carry a HEALPix ``dggs`` attribute and hold arrays (one Gridlook entry per
group), and for groups with a ``multiscales`` layout whose assets resolve to
such groups (one entry for the whole pyramid).

Usage: python -I make_gridlook_catalog.py OUT.json
"""

import json
import subprocess
import sys

STAC = "https://stac-api.grid4earth.eu"
GATEWAY = "https://data.grid4earth.eu"
AWS = "/Users/todaka/micromamba/envs/fishtag/bin/aws"
S3 = ["--endpoint-url", "https://s3.gra.io.cloud.ovh.net", "--profile", "grid4earth"]


def get_json(url):
    # curl rather than urllib: urllib gets truncated bodies through some proxies
    out = subprocess.run(
        ["curl", "-sf", "--retry", "3", "--compressed", url],
        capture_output=True, check=True,
    ).stdout
    return json.loads(out)


def stac_stores():
    for c in get_json(f"{STAC}/collections")["collections"]:
        if c["id"].startswith("mirror-"):
            continue
        items = get_json(f"{STAC}/collections/{c['id']}/items?limit=500")["features"]
        for f in items:
            for a in f["assets"].values():
                if "data" in (a.get("roles") or []) and a.get("href", "").endswith(".zarr"):
                    yield c["id"], a["href"]


def multires_stores():
    out = subprocess.run(
        [AWS, *S3, "s3", "ls", "--recursive", "s3://grid4earth/public/converted/"],
        capture_output=True, text=True, check=True,
    ).stdout
    stores = set()
    for line in out.splitlines():
        key = line.split()[-1]
        if "-multires/" in key and key.endswith(".zarr/zarr.json") and key.count(".zarr/") == 1:
            stores.add(key.removeprefix("public/").removesuffix("/zarr.json"))
    for s in sorted(stores):
        collection = "converted-" + s.split("/")[1]
        yield collection, f"{GATEWAY}/{s}"


def healpix_groups(meta):
    """Group paths with a HEALPix dggs attribute that directly hold arrays."""
    arrays = {k.rsplit("/", 1)[0] if "/" in k else "" for k, v in meta.items() if v.get("node_type") == "array"}
    for path, node in meta.items():
        if node.get("node_type") != "group":
            continue
        dggs = node.get("attributes", {}).get("dggs")
        if isinstance(dggs, dict) and str(dggs.get("name", "")).lower() == "healpix" and path in arrays:
            yield path, dggs.get("refinement_level")


def pyramid_groups(meta, healpix):
    """Groups whose multiscales layout points (relative) at >= 2 HEALPix groups."""
    for path, node in meta.items():
        layout = (node.get("attributes", {}).get("multiscales") or {}).get("layout")
        if node.get("node_type") != "group" or not isinstance(layout, list):
            continue
        levels = [f"{path}/{e['asset']}" for e in layout if isinstance(e, dict) and "asset" in e]
        if len(levels) >= 2 and all(lv in healpix for lv in levels):
            yield path, [healpix[lv] for lv in levels]


def short_name(store_url):
    name = store_url.rstrip("/").rsplit("/", 1)[-1].removesuffix(".zarr")
    parts = name.split("_")
    # S2/S3 EOPF names: platform, product, sensing time, ..., tile
    return " ".join(p for p in parts if p[:1] != "N" or not p[1:].isdigit())


def main():
    datasets = []
    # multires test stores first, so they are at the top of "Open dataset"
    sources = list(multires_stores()) + list(stac_stores())
    for collection, url in sources:
        try:
            meta = get_json(f"{url}/zarr.json").get("consolidated_metadata", {}).get("metadata")
        except Exception as e:  # noqa: BLE001
            print(f"skip {url}: {e}", file=sys.stderr)
            continue
        if not meta:
            print(f"skip {url}: no consolidated metadata", file=sys.stderr)
            continue
        healpix = dict(healpix_groups(meta))
        method = url.split("-multires/")[1].split("/")[0] if "-multires/" in url else None
        for path, levels in pyramid_groups(meta, healpix):
            title = f"{collection} [{method or 'multires'} L{levels[0]}-L{levels[-1]}] {short_name(url)} {path}"
            datasets.append({"title": title, "url": f"{url}/{path}", "tag": "healpix"})
        if method:
            continue  # pyramids: one entry for the whole pyramid is enough
        for path, level in sorted(healpix.items()):
            title = f"{collection} L{level} {short_name(url)} {path}"
            datasets.append({"title": title, "url": f"{url}/{path}", "tag": "healpix"})
        print(f"{url}: {len(healpix)} healpix groups", file=sys.stderr)

    catalog = {"type": "gridlook_catalog", "title": "GRID4EARTH HEALPix data", "datasets": datasets}
    with open(sys.argv[1], "w") as f:
        json.dump(catalog, f, indent=2)
    print(f"{len(datasets)} datasets", file=sys.stderr)


if __name__ == "__main__":
    main()
