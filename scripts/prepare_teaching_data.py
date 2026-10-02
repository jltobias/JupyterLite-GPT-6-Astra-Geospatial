"""One-time desktop preparation of the small, licensed teaching extracts.

Requires rasterio and Pillow, not installed or used in JupyterLite. Inputs are
the URLs recorded below. Committed JSON outputs let learners work without APIs.
"""
import hashlib
import json
import math
from pathlib import Path
import ssl
import urllib.request
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
import rasterio
from rasterio.windows import Window, from_bounds, bounds
from rasterio.warp import transform

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'content/data'; DATA.mkdir(exist_ok=True)
CACHE=ROOT/'test-results/source-data'; CACHE.mkdir(parents=True,exist_ok=True)
DATE='2026-10-02'
OSM='https://api.openstreetmap.org/api/0.6/map?bbox=25.910,-24.681,25.913,-24.678'
TERRAIN='https://s3.amazonaws.com/elevation-tiles-prod/terrarium/14/9371/9351.png'
STAC='https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items/S2C_35JLN_20250123_0_L2A'

def obtain(name,url):
    path=CACHE/name
    if not path.exists():
        staged=DATA/name
        if staged.exists(): path.write_bytes(staged.read_bytes())
        else:
            with urllib.request.urlopen(url,timeout=90) as response: path.write_bytes(response.read())
    return path

def write(name,value):
    (DATA/name).write_text(json.dumps(value,indent=1,allow_nan=False),encoding='utf-8')

osm=obtain('gaborone.osm',OSM); root=ET.parse(osm).getroot()
nodes={n.attrib['id']:[float(n.attrib['lon']),float(n.attrib['lat'])] for n in root.findall('node')}
features=[]
for way in root.findall('way'):
    tags={t.attrib['k']:t.attrib['v'] for t in way.findall('tag')}
    ids=[n.attrib['ref'] for n in way.findall('nd')]
    if 'building' not in tags or len(ids)<4 or ids[0]!=ids[-1] or any(i not in nodes for i in ids): continue
    ring=[nodes[i] for i in ids]
    def number(key):
        try: return float(tags[key])
        except (KeyError,ValueError): return None
    features.append(dict(type='Feature',id='way/'+way.attrib['id'],geometry=dict(type='Polygon',coordinates=[ring]),
        properties=dict(source_id='way/'+way.attrib['id'],source_version=way.attrib['version'],
            source_timestamp=way.attrib['timestamp'],building=tags['building'],height_m=number('height'),
            levels=number('building:levels'),height_raw=tags.get('height'),synthetic=False)))
write('gaborone_buildings.geojson',dict(type='FeatureCollection',features=features,
    provenance=dict(source=OSM,retrieved=DATE,crs='OGC:CRS84',license='ODbL-1.0',
        license_url='https://opendatacommons.org/licenses/odbl/1-0/',attribution='© OpenStreetMap contributors',
        sha256_source=hashlib.sha256(osm.read_bytes()).hexdigest(),
        processing='Closed building ways only; retain source IDs/version/time and height tags; omit contributor identities; no completeness claim')))

tile=obtain('terrain.png',TERRAIN)
rgb=np.array(Image.open(tile),dtype=float)
z=(rgb[:,:,0]*256+rgb[:,:,1]+rgb[:,:,2]/256-32768)[::8,::8][::-1]
zoom,tx,ty=14,9371,9351
lon0=tx/2**zoom*360-180; lon1=(tx+1)/2**zoom*360-180
lat0=math.degrees(math.atan(math.sinh(math.pi*(1-2*(ty+1)/2**zoom))))
lat1=math.degrees(math.atan(math.sinh(math.pi*(1-2*ty/2**zoom))))
width=6371008.8*math.cos(math.radians((lat0+lat1)/2))*math.radians(lon1-lon0)
height=6371008.8*math.radians(lat1-lat0)
# Exact sampled column/row centers transformed to the local equirectangular frame.
lons=(tx+(np.arange(32)*8+.5)/256)/2**zoom*360-180
lats=np.degrees(np.arctan(np.sinh(np.pi*(1-2*(ty+(np.arange(32)*8+.5)/256)/2**zoom))))[::-1]
x=6371008.8*np.cos(np.radians((lat0+lat1)/2))*np.radians(lons-lon0)
y=6371008.8*np.radians(lats-lat0)
write('gaborone_terrain.json',dict(x=x.tolist(),y=y.tolist(),z=z.tolist(),
    pixel_area_m2=width*height/1024,bounds_lonlat=[lon0,lat0,lon1,lat1],synthetic=False,
    provenance=dict(source=TERRAIN,retrieved=DATE,encoding='Terrarium: R*256+G+B/256-32768 metres',
        horizontal_frame='Local equirectangular approximation; exact sample centers; rows south to north',
        vertical_datum='Not independently verified for this composite; use relative elevation, not absolute flood levels',
        processing='Every eighth source pixel, reversed north-to-south rows; area uses approximate tile area / 1024',
        attribution='Mapzen; USGS SRTM/GMTED2010 and NOAA ETOPO1 terrain sources',
        license_url='https://github.com/tilezen/joerd/blob/master/docs/attribution.md',
        sha256_source=hashlib.sha256(tile.read_bytes()).hexdigest())))

item_path=obtain('sentinel-item.json',STAC)
item=json.loads(item_path.read_text()); item=item['features'][0] if 'features' in item else item
# Export the OS trust roots for GDAL rather than disabling TLS verification.
certs=ssl.create_default_context().get_ca_certs(binary_form=True)
ca=CACHE/'os-trust.pem'; ca.write_text(''.join(ssl.DER_cert_to_PEM_cert(c) for c in certs))
with rasterio.Env(GDAL_HTTP_CA_BUNDLE=str(ca),GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT='90'):
    with rasterio.open(item['assets']['scl']['href']) as src:
        ex,ny=transform('EPSG:4326',src.crs,[25.9115],[-24.6795])
        rr,cc=src.index(ex[0],ny[0]); window=Window(cc-32,rr-32,64,64)
        scl=src.read(1,window=window); bbox=bounds(window,src.transform)
        affine=src.window_transform(window); crs=str(src.crs)
    bands={}
    for band in ['red','nir']:
        with rasterio.open(item['assets'][band]['href']) as src:
            dn=src.read(1,window=from_bounds(*bbox,transform=src.transform),out_shape=(64,64))
        spec=item['assets'][band]['raster:bands'][0]
        values=dn*spec.get('scale',1)+spec.get('offset',0)
        bands[band]=values.tolist()
    write('sentinel_chip.json',dict(**bands,scl=scl.tolist(),shape=[64,64],bounds=list(bbox),crs=crs,pixel_m=20,
        synthetic=False,provenance=dict(item_id=item['id'],acquired=item['properties']['datetime'],retrieved=DATE,
            source=STAC,assets={b:item['assets'][b]['href'] for b in ['red','nir','scl']},
            processing='64x64 SCL window; red/NIR nearest-neighbor resampled to this 20 m grid; STAC scale/offset applied',
            attribution='Contains modified Copernicus Sentinel data (2025), processed by ESA; COG distribution by Element 84',
            license_url='https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice')))
print('Prepared',len(features),'OSM footprints, terrain',z.shape,'and Sentinel chip',scl.shape)
