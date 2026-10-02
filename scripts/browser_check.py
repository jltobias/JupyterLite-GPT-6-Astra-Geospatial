"""Execute every notebook through the real JupyterLite/Pyodide browser kernel."""
import functools
import http.server
import json
import os
import argparse
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--only',nargs='+',help='Notebook number prefixes for a focused recheck, e.g. 14 15 16')
args=parser.parse_args()
OUT=ROOT/'test-results'; OUT.mkdir(exist_ok=True)
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT/'_site')))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
reports=[]
try:
    with sync_playwright() as p:
        options={'headless':True,'args':['--enable-unsafe-swiftshader']}
        if os.environ.get('BROWSER_EXECUTABLE'): options['executable_path']=os.environ['BROWSER_EXECUTABLE']
        browser=p.chromium.launch(**options)
        page=browser.new_page(viewport={'width':1440,'height':1000})
        page.goto(base)
        items=json.loads((ROOT/'content/notebooks.json').read_text(encoding='utf-8'))
        assert page.locator('.card').count()==len(items)>0
        page.screenshot(path=str(OUT/'gallery.png'),full_page=True)
        page.goto(base+'/lite/lab/index.html')
        page.wait_for_function('window.jupyterapp && window.jupyterapp.commands',timeout=120000)
        page.evaluate('async () => {await window.jupyterapp.restored;}')
        selected=[item for item in items if not args.only or item['slug'][:2] in args.only]
        assert selected,'No matching notebooks'
        for item in selected:
            path=item['slug']+'.ipynb'
            print('BROWSER RUN',path,flush=True)
            # Use public JupyterLab application/NotebookPanel APIs, not private kernel internals.
            result=page.evaluate('''async (path) => {
                const app=window.jupyterapp;
                const panel=await app.commands.execute('docmanager:open',{path});
                await panel.context.ready;
                await panel.sessionContext.ready;
                if (!panel.sessionContext.session?.kernel) {
                    await panel.sessionContext.changeKernel({name:'python'});
                }
                await app.commands.execute('notebook:run-all-cells');
                const cells=panel.content.model.toJSON().cells;
                const code=cells.filter(c=>c.cell_type==='code');
                const errors=code.flatMap(c=>(c.outputs||[]).filter(o=>o.output_type==='error'));
                const outputs=code.flatMap(c=>c.outputs||[]);
                const summary={path,counts:code.map(c=>c.execution_count),errors,
                    plots:outputs.filter(o=>o.data?.['image/png']).length,
                    text:outputs.map(o=>o.text||'').join('')};
                await panel.context.save();
                return summary;
            }''',path)
            (OUT/(item['slug']+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
            assert not result['errors'],result
            assert all(x is not None for x in result['counts']),result
            assert result['plots']>=3,result
            if path.startswith('10'): assert 'Rust/WASM loaded' in result['text'],result
            if path[:2] in {'14','15','16'}:
                scene=page.frame_locator('iframe[title]').last
                scene.locator('canvas').first.wait_for(timeout=120000)
                frames=[frame for frame in page.frames if frame.parent_frame==page.main_frame]
                assert frames, 'Expected an embedded 3D scene'
                frames[-1].wait_for_function('window.sceneReady===true',timeout=120000)
                if path.startswith('14'):
                    frames[-1].wait_for_function('window.sceneMap.loaded() && window.sceneMap.queryRenderedFeatures({layers:["buildings","footprints"]}).length>0',timeout=120000)
            page.screenshot(path=str(OUT/(item['slug']+'.png')))
            reports.append({'notebook':path,'passed':True,'plots':result['plots']})
            print('BROWSER PASS',path,flush=True)
            page.evaluate('async () => {const app=window.jupyterapp; await app.shell.currentWidget.sessionContext.shutdown(); await app.commands.execute("application:close");}')
        browser.close()
finally:
    server.shutdown()
    name='browser-focused.json' if args.only else 'browser.json'
    (OUT/name).write_text(json.dumps(reports,indent=2),encoding='utf-8')
