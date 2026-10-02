"""Render the exported scenes and test their controls in a real WebGL browser."""
import functools
import http.server
import json
import os
import sys
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'content'))
from scenes import scene_frame
OUT=ROOT/'test-results'

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(OUT/'scenes')))
threading.Thread(target=server.serve_forever,daemon=True).start()
reports=[]
try:
    with sync_playwright() as p:
        options={'headless':True,'args':['--enable-unsafe-swiftshader']}
        if os.environ.get('BROWSER_EXECUTABLE'): options['executable_path']=os.environ['BROWSER_EXECUTABLE']
        browser=p.chromium.launch(**options)
        page=browser.new_page(viewport={'width':1280,'height':850})
        errors=[]; page.on('pageerror',lambda error:errors.append(str(error)))
        scene_names=['14_maplibre_scene.html','14_real_footprints.html','15_deckgl_scene.html','16_terrain_scene.html','16_real_terrain.html']
        for name in scene_names:
            errors.clear()
            page.goto(f'http://127.0.0.1:{server.server_port}/{name}')
            page.wait_for_function('window.sceneReady===true',timeout=120000)
            assert page.locator('canvas').count()>0
            if name.startswith('14'):
                page.locator('#height').fill('5'); page.locator('#height').dispatch_event('input')
                assert page.evaluate('window.sceneState.factor')==5
                assert page.evaluate('window.sceneMap.getPaintProperty("buildings","fill-extrusion-height")[2]')==5
                page.locator('#top').click()
                assert page.evaluate('window.sceneMap.getPitch()')==0
                page.locator('#reset').click()
                total=page.evaluate('window.sceneData.buildings.features.length')
                assert page.locator('#rows tr').count()==total
                page.locator('#floors').fill('4'); page.locator('#floors').dispatch_event('input')
                assert page.locator('#rows tr').count()==0
                page.locator('#floors').fill('0'); page.locator('#floors').dispatch_event('input')
                assert page.locator('#rows tr').count()==total
                page.wait_for_function('window.sceneMap.loaded()')
            elif name.startswith('15'):
                page.locator('#scenario').select_option('improved')
                page.locator('#metric').select_option('population')
                assert page.evaluate('window.sceneState.scenario')=='improved'
                assert page.evaluate('window.sceneState.metric')=='population'
                assert page.evaluate('window.sceneDeck.props.layers[1].props.getElevation(window.sceneData.buildings[0])')==page.evaluate('window.sceneData.buildings[0].population*3')
                assert page.locator('#rows tr').count()==144
                page.locator('#population').fill('1000'); page.locator('#population').dispatch_event('input')
                assert page.locator('#rows tr').count()==0
                assert page.evaluate('window.sceneState.totalPopulation')==1200
                page.locator('#population').fill('0'); page.locator('#population').dispatch_event('input')
                page.locator('#color').select_option('served')
                page.locator('#time').fill('18'); page.locator('#time').dispatch_event('input')
                assert page.evaluate('window.sceneState.activeTrips')>0
            else:
                initial=page.evaluate('window.sceneState.area')
                page.locator('#exaggeration').fill('50'); page.locator('#exaggeration').dispatch_event('input')
                assert page.evaluate('window.sceneState.area')==initial
                level='20' if 'real' in name else '1004'
                page.locator('#water').fill(level); page.locator('#water').dispatch_event('input')
                assert page.evaluate('window.sceneState.area')>=initial
                assert page.evaluate('document.querySelector("#view").data[1].z[0][0]')==float(level)
                page.locator('#row').fill('5'); page.locator('#row').dispatch_event('input')
                assert page.evaluate('window.profileRow')==5
                assert page.evaluate('document.querySelector("#profile").data[0].y')==page.evaluate('window.sceneData.z[5]')
            page.screenshot(path=str(OUT/(name+'.png')),full_page=True)
            assert not errors,errors
            reports.append(dict(scene=name,passed=True,state=page.evaluate('window.sceneState')))
            print('SCENE PASS',name,flush=True)
        # A standalone scene can work while notebook iframe worker messaging fails.
        for name in scene_names:
            errors.clear()
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            document=(OUT/'scenes'/name).read_text(encoding='utf-8')
            page.set_content(scene_frame(document,name).data)
            frame=page.frames[-1]
            frame.wait_for_function('window.sceneReady===true',timeout=120000)
            assert frame.url.startswith('blob:'),frame.url
            assert frame.locator('canvas').count()>0
            if name.startswith('14'):
                assert frame.evaluate('window.sceneMap.queryRenderedFeatures({layers:["buildings","footprints"]}).length')>0
            page.screenshot(path=str(OUT/('embedded-'+name+'.png')),full_page=True)
            assert not errors,errors
            reports.append(dict(scene=name,embedded=True,passed=True))
            print('EMBEDDED SCENE PASS',name,flush=True)
        browser.close()
finally:
    server.shutdown()
    (OUT/'scenes.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
