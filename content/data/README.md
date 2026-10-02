# Small public-data extracts

These files support the extended investigations without requiring learner accounts, GIS servers or live data APIs. They are external data, **not MIT-licensed synthetic fixtures**. Each file contains its own provenance. The synthetic population, roads, facilities and health scenarios are not observations of the places in these extracts.

| File | Source and snapshot | Processing and units | Terms |
|---|---|---|---|
| `gaborone_buildings.geojson` | OpenStreetMap API bounding box `25.910,-24.681,25.913,-24.678`, retrieved October 2, 2026 | 125 closed building ways; longitude/latitude in OGC:CRS84; source IDs, versions and timestamps retained; contributor identities omitted | © OpenStreetMap contributors; [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/), [attribution](https://www.openstreetmap.org/copyright) |
| `sentinel_chip.json` | EarthSearch item `S2C_35JLN_20250123_0_L2A`, acquired January 23, 2025 at 08:27:41.731 UTC; retrieved October 2, 2026 | 64 × 64 pixels at 20 m, EPSG:32735; red and NIR nearest-neighbor resampled to the SCL window; STAC scale 0.0001 and offset −0.1 applied | Contains modified Copernicus Sentinel data (2025), processed by ESA; COG distribution by Element 84; [Sentinel Data Legal Notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice) |
| `gaborone_terrain.json` | [Mapzen Terrarium tile 14/9371/9351](https://s3.amazonaws.com/elevation-tiles-prod/terrarium/14/9371/9351.png), retrieved October 2, 2026 | Decode `R*256 + G + B/256 - 32768` metres; sample every eighth pixel to 32 × 32; reverse rows to south-to-north; retain sample centers in an approximate local equirectangular frame | Mapzen; USGS SRTM/GMTED2010 and NOAA ETOPO1 sources; [source attribution and terms](https://github.com/tilezen/joerd/blob/master/docs/attribution.md) |

The OSM derivative is available here as editable GeoJSON under ODbL. Retain attribution and applicable share-alike obligations when redistributing derivatives. All 125 features lack numeric reported height/level tags in this snapshot: unknown remains unknown. The simple notebook polygon audit is not a full OGC validator or a completeness assessment.

The Sentinel chip contains SCL classes 4 (vegetation) and 5 (not vegetated). Notebook 04 adds a clearly labeled **artificial cloud patch** for teaching masking. Red/NIR NDVI is not land-surface temperature. The committed arrays contain reflectance after scaling; do not scale them again. Projected bounds, asset URLs and acquisition metadata are included in the JSON.

The terrain tile is a composite elevation product. Its exact vertical datum and local accuracy were not independently verified. Notebook 16 subtracts the chip minimum, labels relative elevations explicitly, and treats below-plane area as a screening statistic, not a hydraulic forecast. Approximate cell area is tile area divided by 1,024; subsampling does not create new survey precision. Raw OSM and terrain source SHA-256 hashes are retained in provenance.

## Reproducing the preparation

Learners do not need this step. On a desktop, install `requirements-data.txt`, then run `python scripts/prepare_teaching_data.py` from the repository root. It fetches public source inputs into ignored `test-results/source-data/`, validates TLS using OS trust roots, and writes the three extracts. Rasterio and Pillow are build-time tools only; notebook execution uses JSON and NumPy.

The script preserves the original retrieval date when reusing this snapshot's cache. An uncached OSM request fetches current data, so it may differ from this snapshot: update the retrieval date, source records, expected fixture counts and validation results when intentionally replacing the dataset. Immutable Sentinel item/asset identifiers and the recorded hashes help audit provenance; the terrain endpoint itself is not version-pinned. See [third-party notices](../../THIRD_PARTY_NOTICES.md).
