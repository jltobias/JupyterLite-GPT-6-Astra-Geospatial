"""Publish executed validation copies through Jupyter Book 1.x."""
import json
import shutil
from pathlib import Path
from jupyter_book.cli.main import main

ROOT=Path(__file__).resolve().parents[1]
book=ROOT/'book'; notebooks=book/'notebooks'; notebooks.mkdir(exist_ok=True)
assets=book/'assets'; assets.mkdir(exist_ok=True)
shutil.copy2(ROOT/'assets/geospatial-splash.svg',assets/'geospatial-splash.svg')
shutil.copy2(ROOT/'docs/GUIDE.md',book/'guide.md')
shutil.copy2(ROOT/'docs/TEACHING.md',book/'teaching.md')
readme=(ROOT/'README.md').read_text(encoding='utf-8')
sources='# Sources, attribution and licenses\n\n'+readme.split('## Data sources and provenance\n',1)[1].split('## Build, validate and publish',1)[0]
sources=sources.replace('](content/','](https://github.com/jltobias/JupyterLite-GPT-6-Astra-Geospatial/blob/main/content/').replace('](assets/','](https://github.com/jltobias/JupyterLite-GPT-6-Astra-Geospatial/blob/main/assets/').replace('](rust/','](https://github.com/jltobias/JupyterLite-GPT-6-Astra-Geospatial/blob/main/rust/')
sources=sources.replace('](LICENSE)','](https://github.com/jltobias/JupyterLite-GPT-6-Astra-Geospatial/blob/main/LICENSE)').replace('](THIRD_PARTY_NOTICES.md)','](https://github.com/jltobias/JupyterLite-GPT-6-Astra-Geospatial/blob/main/THIRD_PARTY_NOTICES.md)')
(book/'sources.md').write_text(sources,encoding='utf-8')
items=json.loads((ROOT/'content/notebooks.json').read_text())
toc='format: jb-book\nroot: index\nchapters:\n  - file: guide\n  - file: teaching\n'
for item in items:
    name=item['slug']+'.ipynb'; source=ROOT/'test-results/executed'/name
    if not source.exists(): raise RuntimeError('Run scripts/check_notebooks.py --require-wasm first')
    nb=json.loads(source.read_text(encoding='utf-8'))
    first=nb['cells'][0]; text=''.join(first['source']) if isinstance(first['source'],list) else first['source']
    title,rest=text.split('\n',1)
    first['source']=title+'\n\n[Open this notebook in JupyterLite](https://jltobias.github.io/JupyterLite-GPT-6-Astra-Geospatial/lite/lab/index.html?path='+name+')\n'+rest
    (notebooks/name).write_text(json.dumps(nb),encoding='utf-8')
    toc+='  - file: notebooks/'+item['slug']+'\n'
toc+='  - file: sources\n'
(book/'_toc.yml').write_text(toc,encoding='utf-8')
main(['build',str(book),'--path-output',str(ROOT/'_book_build'),'--warningiserror','--keep-going'],standalone_mode=False)
shutil.copytree(ROOT/'_book_build/_build/html',ROOT/'_site/book',dirs_exist_ok=True)
print('Built _site/book/index.html')
