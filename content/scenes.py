"""Export interactive HTML scenes without Python widget/native GIS dependencies."""
import html
import json
import math
from pathlib import Path

from twin import lonlat


def building_features(city, population, floor_height_m=3.):
    if not math.isfinite(floor_height_m) or floor_height_m <= 0:
        raise ValueError('Floor height must be positive and finite')
    if len(population) != len(city['xy']):
        raise ValueError('Population must match the building inventory')
    features = []
    for i, (x, y) in enumerate(city['xy']):
        w, d = city['width'][i]/2, city['depth'][i]/2
        corners = [(x-w,y-d), (x+w,y-d), (x+w,y+d), (x-w,y+d), (x-w,y-d)]
        ring = [[float(v) for v in lonlat(a,b)] for a,b in corners]
        features.append(dict(type='Feature', id=f'b{i:03d}',
            geometry=dict(type='Polygon', coordinates=[ring]),
            properties=dict(id=f'b{i:03d}', floors=int(city['floors'][i]),
                height_m=float(city['floors'][i]*floor_height_m), population=int(population[i]),
                residential=bool(city['residential'][i]), synthetic=True)))
    return dict(type='FeatureCollection', features=features)


def scene_html(kind, payload):
    if kind not in {'maplibre', 'deck', 'terrain'}:
        raise ValueError('Unknown scene kind')
    # Escaping '<' prevents user data from terminating the embedded script element.
    encoded = json.dumps(payload, allow_nan=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    root = Path(__file__).resolve().parent/'scene_templates'
    template = (root/(kind+'.html')).read_text(encoding='utf-8')
    return template.replace('__DATA__', encoded).replace('__STYLE__', (root/'style.css').read_text(encoding='utf-8'))


def export_scene(name, kind, payload):
    folder = Path('exports'); folder.mkdir(exist_ok=True)
    document = scene_html(kind, payload)
    path = folder/name
    path.write_text(document, encoding='utf-8')
    print('Saved', path, '— download and open in a browser; renderer downloads require internet.')
    return document


def scene_frame(document, title):
    """Load a same-origin Blob document without needing a kernel HTTP server.

    MapLibre workers cannot complete GeoJSON loads directly in about:srcdoc
    (upstream issue #7047). A tiny srcdoc bootstrap navigates to a Blob URL,
    preserving the parent origin for worker messaging. Revoke it on load.
    """
    from IPython.display import HTML
    cleanup="<script>addEventListener('load',()=>URL.revokeObjectURL(location.href),{once:true});</script>"
    encoded=json.dumps(document+cleanup).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    loader='<script>location.replace(URL.createObjectURL(new Blob(['+encoded+'],{type:"text/html;charset=utf-8"})));</script>'
    return HTML('<iframe title="'+html.escape(title, quote=True)+'" '
                'style="width:100%;height:680px;border:1px solid #b9c9ce;border-radius:12px" '
                'srcdoc="'+html.escape(loader, quote=True)+'"></iframe>')
