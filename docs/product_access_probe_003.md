# Product Access Probe 003

## Purpose

This record documents the small public metadata and endpoint checks performed
for Goal 003. No bulk datasets, raw geometry, rasters, biodiversity records, or
private/credentialed services were downloaded.

## Commands Run

Working directory:

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

HTTP header probe command:

```bash
for u in <official URLs>; do
  printf '%s\n' "$u"
  curl -L -sI --max-time 20 "$u" |
    awk 'BEGIN{IGNORECASE=1} /^HTTP\//{code=$0} /^content-length:/{len=$0} /^content-type:/{type=$0} END{print code; if(type) print type; if(len) print len; print ""}'
done
```

DEA Waterbodies metadata field probe:

```bash
curl -L -s --max-time 20 \
  'https://knowledge.dea.ga.gov.au/data/product/dea-waterbodies-landsat/?tab=details' |
  rg -n 'Download the shapefile|Access the data on AWS|Web Mapping Service|pc_wet|px_wet|less than 90%|Creative Commons'
```

DEA Water Observations metadata field probe:

```bash
curl -L -s --max-time 20 \
  'https://knowledge.dea.ga.gov.au/data/product/dea-water-observations-landsat/?tab=overview' |
  rg -n 'Coverage|16 Aug 1986|Licence|Creative Commons|No Data|Contiguity|Low Solar Angle|Terrain Shadow|High Slope|Cloud Shadow|Cloud|Water|underestimate|vegetated wetlands'
```

All response bodies used by the `rg` probes were streamed to stdout. No
temporary files were written.

## URL Checks

| URL | Result | Notes |
| --- | --- | --- |
| https://knowledge.dea.ga.gov.au/data/product/dea-water-observations-landsat/?tab=overview | HTTP 200; `text/html`; `content-length: 82394` | Official product page reachable. Metadata confirms 30 m Water Observations, 1986-present coverage, CC BY 4.0, bit-field invalid/water classes, and vegetated-wetland omission caveat. |
| https://knowledge.dea.ga.gov.au/data/product/dea-waterbodies-landsat/?tab=details | HTTP 200; `text/html`; `content-length: 128532` | Official product page reachable. Metadata confirms shapefile, AWS, WMS access surfaces, CC BY 4.0, `pc_wet`, `px_wet`, and the Waterbodies 90% observed rule. |
| https://data.dea.ga.gov.au/?prefix=derivative%2Fdea_waterbodies%2F3-0-0%2F | HTTP 200; `text/html`; `content-length: 6457` | Public AWS browser prefix reachable. No files were downloaded. |
| https://geoserver.dea.ga.gov.au/geoserver/web/?0= | HTTP 302 | DEA GeoServer web endpoint redirects; no data requested. |
| https://www.bom.gov.au/water/geofabric/download.shtml | HTTP 403 to `curl -I` | Browser-accessible official page was used in Goal 002; command-line header check is blocked, so use data.gov.au/official docs before executable access. |
| https://www.unsw.edu.au/research/ecosystem/our-research/rivers-and-wetlands/eastern-australian-waterbird-survey | HTTP 200; `text/html;charset=utf-8`; `content-length: 317021` | Official EAWS page reachable; confirms public database surface and survey context. |
| https://aws.ecosystem.unsw.edu.au/ | HTTP 200; `text/html`; `content-length: 5561` | Australian Waterbird Surveys public web surface reachable; no data queried or downloaded. |
| Candidate DCCEEW Ramsar pages for Macquarie, Narran, Gwydir, Kerang, Currawinya, Coorong/Lower Lakes, and Coongie | HTTP 200; `text/html`; page lengths approximately 88-97 KB | Official candidate pages reachable and used only as metadata evidence. |
| https://www.dcceew.gov.au/cewh/water-region/lachlan-river/about | HTTP 200; `text/html`; `content-length: 59640` | Official Lachlan/Great Cumbung context reachable; used to defer lower-Lachlan candidates. |

## Temporary Files

No temporary files were created. No source geometry, rasters, shapefiles,
GeoPackages, CSV data exports, biodiversity records, or survey records were
left in the repository or ignored directories.

## Probe Conclusion

The official metadata surfaces are sufficient for Goal 003's design package.
The project is ready for a later small executable hydrology extraction smoke
test, provided that Goal 004 still avoids biodiversity downloads and commits no
raw source geometry.
