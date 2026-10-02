"""Execute notebooks with top-level await in fresh namespaces; validate real assertions."""
import ast
import asyncio
import base64
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import shutil
import time
import nbformat

ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLBACKEND','Agg')
os.chdir(ROOT/'content')
sys.path.insert(0,str(ROOT/'content'))

async def main():
    report=[]
    import matplotlib.pyplot as plt
    executed=ROOT/'test-results'/'executed'; executed.mkdir(parents=True,exist_ok=True)
    items=json.loads(Path('notebooks.json').read_text(encoding='utf-8'))
    expected={item['slug']+'.ipynb' for item in items}
    assert expected=={p.name for p in Path('.').glob('*.ipynb')}, 'Notebook manifest differs from files'
    for path in [Path(item['slug']+'.ipynb') for item in items]:
        nb=nbformat.read(path,as_version=4); nbformat.validate(nb)
        scope={'__name__':'__main__'}; start=time.perf_counter()
        outputs=[]
        def show(*args,**kwargs):
            for number in plt.get_fignums():
                buffer=io.BytesIO(); plt.figure(number).savefig(buffer,format='png',bbox_inches='tight')
                outputs.append(nbformat.v4.new_output('display_data',data={'image/png':base64.b64encode(buffer.getvalue()).decode()}))
            plt.close('all')
        def show_value(value,*args,**kwargs):
            data={'text/plain':repr(value)}
            if hasattr(value,'_repr_html_'):
                data['text/html']=value._repr_html_()
            outputs.append(nbformat.v4.new_output('display_data',data=data))
        plt.show=show
        count=0
        for i,c in enumerate(nb.cells):
            if c.cell_type=='code':
                outputs=[]; stdout=io.StringIO(); count+=1
                code=compile(c.source,f'{path}:cell{i}', 'exec',flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
                with contextlib.redirect_stdout(stdout):
                    value=eval(code,scope)
                    if asyncio.iscoroutine(value): await value
                scope['display']=show_value
                if stdout.getvalue(): outputs.append(nbformat.v4.new_output('stream',name='stdout',text=stdout.getvalue()))
                c.execution_count=count; c.outputs=outputs
        if path.name.startswith('10') and '--require-wasm' in sys.argv:
            assert scope['wasm_fn'] is not None,'Compiled Rust/WASM is required for this check'
        plt.close('all')
        nbformat.write(nb,executed/path.name)
        assert 'extension_prompt' in scope and 'extension_grade' in scope,'Missing executable extension'
        assert scope['extension_grade']=={'status':'NOT RUN'},'Do not publish a fabricated model trial'
        plot_count=sum('image/png' in o.get('data',{}) for c in nb.cells if c.cell_type=='code' for o in c.outputs)
        assert plot_count>=3, 'Require baseline, concept map and extension visual'
        report.append(dict(notebook=path.name,passed=True,seconds=round(time.perf_counter()-start,3)))
        print('PASS',path)
    assert len(report)==len(expected)>0
    out=ROOT/'test-results'; out.mkdir(exist_ok=True)
    (out/'desktop.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    scene_dir=out/'scenes'; scene_dir.mkdir(exist_ok=True)
    for name in ['14_maplibre_scene.html','14_real_footprints.html','15_deckgl_scene.html','16_terrain_scene.html','16_real_terrain.html']:
        shutil.copy2(Path('exports')/name,scene_dir/name)

asyncio.run(main())
