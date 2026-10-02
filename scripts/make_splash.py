"""Original editable vector artwork; no external assets or fonts."""
from pathlib import Path
import random
root=Path(__file__).resolve().parents[1]
parts=['''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="620" viewBox="0 0 1440 620" role="img" aria-labelledby="title desc">
<title id="title">JupyterLite + GPT-6 Astra Geospatial</title><desc id="desc">An original isometric city illustration connects buildings, sensors and routes. Sixteen browser-based experiments explore geospatial reasoning, 3D mapping and urban digital twins.</desc>
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#081e2c"/><stop offset="1" stop-color="#123d49"/></linearGradient><radialGradient id="glow"><stop stop-color="#26d5bf" stop-opacity=".18"/><stop offset="1" stop-color="#26d5bf" stop-opacity="0"/></radialGradient></defs>
<rect width="1440" height="620" rx="24" fill="url(#bg)"/><circle cx="1100" cy="280" r="410" fill="url(#glow)"/>
<g font-family="Segoe UI,Arial,sans-serif"><text x="65" y="83" fill="#75e3cf" font-size="16" letter-spacing="4">URBAN TWIN LAB</text>
<text x="62" y="169" fill="#fff" font-size="58" font-weight="700">JupyterLite +</text>
<text x="62" y="236" fill="#fff" font-size="58" font-weight="700">GPT-6 Astra</text>
<text x="62" y="311" fill="#75e3cf" font-size="65" font-weight="700">Geospatial</text>
<text x="65" y="368" fill="#c2d9df" font-size="22">Build a small city. Ask a better question.</text>
<text x="65" y="400" fill="#c2d9df" font-size="22">Test what changes.</text>
<rect x="65" y="453" width="228" height="42" rx="21" fill="#244957"/><text x="87" y="481" font-size="16" fill="#e3f5f6">16 RUNNABLE NOTEBOOKS</text>
<text x="65" y="565" fill="#9dbcc6" font-size="16">DIGITAL TWINS  /  WORLD MODELS  /  PYODIDE + RUST / WASM</text></g>''']
def xy(x,y,z=0): return (1045+(x-y)*34,340+(x+y)*17-z)
def pts(seq): return ' '.join(f'{x:.1f},{y:.1f}' for x,y in seq)
parts.append('<g stroke="#477580" stroke-width="1" opacity=".55">')
for i in range(-5,7):
    a,b=xy(i,-5),xy(i,6);parts.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}"/>')
    a,b=xy(-5,i),xy(6,i);parts.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}"/>')
parts.append('</g>')
rng=random.Random(9)
for y in range(-4,5,2):
 for x in range(-4,5,2):
    h=rng.randint(24,106); w=.95
    a,b,c,d=xy(x,y),xy(x+w,y),xy(x+w,y+w),xy(x,y+w)
    A,B,C,D=xy(x,y,h),xy(x+w,y,h),xy(x+w,y+w,h),xy(x,y+w,h)
    for poly,color in [([b,c,C,B],'#176b77'),([d,c,C,D],'#225261'),([A,B,C,D],'#51adac')]:
        parts.append(f'<polygon points="{pts(poly)}" fill="{color}" stroke="#8fe4d5" stroke-opacity=".35"/>')
route=[xy(-4,5),xy(-1,5),xy(-1,1),xy(3,1),xy(3,-3),xy(5,-3)]
parts.append(f'<polyline points="{pts(route)}" fill="none" stroke="#ffbd69" stroke-width="4" stroke-linejoin="round"/>')
for x,y in route[::2]:
 parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="#ffcf8f"/><circle cx="{x}" cy="{y}" r="17" fill="none" stroke="#ffcf8f" opacity=".5"/>')
parts.append('''<g font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="#d7f2ef"><rect x="1090" y="93" width="191" height="37" rx="8" fill="#214957"/><text x="1104" y="117">OBSERVE → SIMULATE</text><rect x="985" y="509" width="201" height="37" rx="8" fill="#214957"/><text x="1002" y="533">MEASURE → IMPROVE</text></g></svg>''')
(root/'assets').mkdir(exist_ok=True)
(root/'assets/geospatial-splash.svg').write_text('\n'.join(parts),encoding='utf-8')
