"""Build JupyterLite plus a small accessible notebook gallery."""
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,'-m','jupyterlite_core','build','--contents','content','--output-dir','_site/lite'],cwd=ROOT,check=True)
items=json.loads((ROOT/'content/notebooks.json').read_text())
scene_names=['14_maplibre_scene.html','14_real_footprints.html','15_deckgl_scene.html','16_terrain_scene.html','16_real_terrain.html']
scene_dir=ROOT/'_site/scenes'; scene_dir.mkdir(exist_ok=True)
for name in scene_names:
    source=ROOT/'test-results/scenes'/name
    if not source.exists(): raise RuntimeError('Run scripts/check_notebooks.py before building the scene gallery')
    shutil.copy2(source,scene_dir/name)
cards='\n'.join(f'<a class="card" href="lite/lab/index.html?path={x["slug"]}.ipynb"><span>EXPERIMENT {i:02d}</span><h2>{html.escape(x["title"].split(" · ")[1])}</h2><p>{html.escape(x["question"])}</p><b>Open notebook →</b></a>' for i,x in enumerate(items,1))
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Urban Twin Lab | Astra + JupyterLite</title><style>
*{box-sizing:border-box}body{margin:0;background:#f3f6f7;color:#15323e;font:17px/1.6 system-ui,sans-serif}main{max-width:1150px;margin:auto;padding:60px 24px}
.eyebrow{font-weight:700;letter-spacing:.15em;color:#087f8c;font-size:13px}h1{font-size:clamp(40px,6vw,70px);line-height:1.06;letter-spacing:-.04em;margin:18px 0}header p{max-width:750px;font-size:20px;color:#47606b}
nav{display:flex;gap:20px;flex-wrap:wrap;margin:30px 0}nav a{color:#087f8c;font-weight:700}a:focus-visible{outline:3px solid #ec991a;outline-offset:4px}
.note{background:#e0eef0;border-left:4px solid #087f8c;padding:18px 22px;margin:35px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}.card{display:block;text-decoration:none;color:inherit;background:white;border:1px solid #d4dfe3;border-radius:12px;padding:25px}.card:hover{border-color:#087f8c;box-shadow:0 6px 18px #16333e12}.card span{font-size:12px;letter-spacing:.1em;color:#087f8c}.card h2{font-size:23px;line-height:1.2}.card p{font-size:16px;color:#47606b}.card b{color:#087f8c;font-size:15px}footer{margin-top:38px;color:#47606b;font-size:14px}
</style><main><header><div class="eyebrow">BROWSER-SIZED EXPERIMENTS · OPEN-ENDED QUESTIONS</div><h1>A city you can<br>question, test and change.</h1><p>Sixteen experiments in spatial data, 3D mapping and urban digital twins. Explore scenarios, learn a world model, and measure Astra's answers against reproducible calculations.</p></header>
<nav><a href="book/index.html">Read the JupyterBook</a><a href="lite/lab/index.html">Launch JupyterLite</a><a href="https://github.com/jltobias/JupyterLite-GPT-6-Astra-Geospatial/blob/main/docs/GUIDE.md">Learning guide</a><a href="https://github.com/jltobias/JupyterLite-GPT-6-Astra-Geospatial">Source &amp; contributions</a></nav>
<div class="note"><strong>Start with any notebook.</strong> Select Python (Pyodide), then Run → Run All Cells. Initial loading downloads the Python runtime and packages. Synthetic baselines and labeled public-data extracts support the investigations. Astra prompts are optional, manual experiments; the notebooks do not run a language model in your browser. Download edits to keep them.</div>
<nav aria-label="Interactive 3D scene previews"><strong>Explore 3D:</strong><a href="scenes/14_maplibre_scene.html">MapLibre buildings</a><a href="scenes/15_deckgl_scene.html">deck.gl access layers</a><a href="scenes/16_terrain_scene.html">Terrain and water</a><a href="scenes/14_real_footprints.html">Real OSM footprints</a><a href="scenes/16_real_terrain.html">Real terrain cross-section</a></nav><p>3D scenes need WebGL and a renderer download. No tile account or API key required.</p>
<section class="grid">CARDS</section><footer>Inspired by James Tobias's Gaborone digital-twin and JupyterLite presentations. Educational MVPs; no patient data, paid map tiles or API keys.</footer></main></html>'''.replace('CARDS',cards)
(ROOT/'_site/index.html').write_text(page,encoding='utf-8')
(ROOT/'_site/.nojekyll').touch()
print('Built _site/index.html and _site/lite/lab/index.html')
