"""Three browser-native 3D mapping labs; no Python widget extension required."""

SCENE_HELP = '''## Use and share the interactive scene
The scene appears below in a trusted notebook output. If your notebook viewer blocks the iframe,
download the HTML from `exports/` and open it in a browser. All data are embedded, but the pinned
JavaScript/CSS renderer still downloads from a CDN; this is not fully offline. WebGL must be available.
The static plot and numerical outputs remain usable when the renderer cannot load.

Camera rotation and vertical exaggeration change the view, not the underlying data. Keep a plan view
beside a perspective view to detect occlusion. Download the notebook, scene and evidence JSON before
clearing browser storage. Do not label synthetic geometry as observed Gaborone buildings.
'''


def add_mapping_labs(notebook):
    notebook('14_maplibre_3d', '14 · Geographic building scenes with MapLibre',
        'How can a 3D map preserve geographic position and honest building heights?',
        'Ask Astra to audit a 3D scene against its GeoJSON, then have Codex add a visual control with explicit data invariants.', [
        ('markdown', '''## From footprint to extrusion · 30 minutes
**Learn:** create WGS84 GeoJSON, distinguish local coordinates from geographic coordinates, and use a
MapLibre `fill-extrusion` layer. Horizontal coordinates are longitude/latitude; heights are metres above
an assumed flat ground plane. Floor height is invented, not measured. Change `floor_height_m` and rerun.
MapLibre projects the GeoJSON for display; do not put local east/north metres directly into its coordinates.
**Predict:** should doubling floor height change population or footprint area?'''),
        ('code', '''
from scenes import building_features, export_scene, scene_frame
c=city(); pop=allocate(c['capacity'],1200); floor_height_m=3.
buildings=building_features(c,pop,floor_height_m)
nodes,graph=network()
roads=dict(type='FeatureCollection',features=[dict(type='Feature',properties={},geometry=dict(type='LineString',
    coordinates=[[float(v) for v in lonlat(*nodes[u])],[float(v) for v in lonlat(*nodes[v])]]))
    for u in graph for v,w in graph[u] if u<v])
assert sum(f['properties']['population'] for f in buildings['features'])==1200
assert all(f['geometry']['coordinates'][0][0]==f['geometry']['coordinates'][0][-1] for f in buildings['features'])
heights=np.array([f['properties']['height_m'] for f in buildings['features']])
assert np.allclose(heights,c['floors']*floor_height_m)
center=[float(v) for v in lonlat(1000,1000)]
payload=dict(buildings=buildings,roads=roads,center=center,synthetic=True,vertical_units='metres above flat ground')
export_json('14_buildings.geojson',buildings)
print('Buildings:',len(heights),'| physical heights:',sorted(set(heights)),'m | residents:',pop.sum())
'''),
        ('code', '''
fig,axes=plt.subplots(1,2,figsize=(12,5))
dots=axes[0].scatter(*c['xy'].T,c=heights,s=25,cmap='viridis'); map_axes(axes[0],'Plan-view height audit')
fig.colorbar(dots,ax=axes[0],label='Assumed height (m)')
axes[1].hist(heights,bins=np.arange(.5,4.5)*floor_height_m,color='#087f8c')
axes[1].set(xlabel='Assumed building height (m)',ylabel='Buildings',title='Unexaggerated height distribution')
plt.tight_layout(); plt.show()
'''),
        ('markdown', SCENE_HELP),
        ('code', '''
document=export_scene('14_maplibre_scene.html','maplibre',payload)
display(scene_frame(document,'MapLibre synthetic buildings in 3D'))
'''),
        ('markdown', '''## Astra interpretation and a Codex implementation task
**Astra:** send `14_buildings.geojson` plus a screenshot at 1× and 5× exaggeration.
Ask: “Which differences come from the camera or exaggeration? Which heights are supported by the data?
List the coordinate order, height units and assumptions. Do not infer occupancy or neighborhood deprivation
from appearance.” Score numerical claims against the GeoJSON, and mark screenshot-only impressions separately.

**Codex:** “Add a minimum-floor filter to `content/scene_templates/maplibre.html`. Show the visible count,
preserve IDs and raw heights, and keep the accessible table consistent with the filter. Test zero matches
and restoring all buildings. Do not rescale heights to make the scene look more dramatic.”

**Acceptance:** 144 original IDs; population total 1,200 before filtering; extrusion equals floors × floor height ×
display exaggeration; changing camera leaves data unchanged. Copy the exact prompt, response, model/date and
screenshots into your learning record. The initial notebook contains no measured Astra response.

Reference: [MapLibre 3D buildings](https://maplibre.org/maplibre-gl-js/docs/examples/display-buildings-in-3d/).
Our scene uses original GeoJSON and an empty style rather than the example's external tile source.''')],
        'Import a small licensed footprint extract with documented height units. Report missing heights explicitly and keep the source IDs, dates and attribution. Add terrain only after defining whether heights are above ground or a vertical datum.')

    notebook('15_deckgl_layers', '15 · Layered 3D access maps with deck.gl',
        'Can an interactive map compare access scenarios without confusing people with metres?',
        'Use Astra to critique visual encodings and Codex to implement a layer toggle while preserving computed access results.', [
        ('markdown', '''## Keep physical height and thematic height separate · 35 minutes
**Learn:** combine extruded polygons, street paths, facility markers and picking in deck.gl.
The renderer consumes plain JSON generated by Python; no ipywidgets or pydeck extension is required.
Physical mode uses building heights in metres. Population mode uses **3 display metres per resident** as a
thematic chart. This is never described as actual building height. Color uses the same 0–30 minute scale in
both access scenarios, with values above 30 clipped to the top color; exact values remain in tooltips/table.
**Predict:** which change should affect color, and which should affect extrusion?'''),
        ('code', '''
from scenes import building_features, export_scene, scene_frame
c=city(); pop=allocate(c['capacity'],1200)
nodes,graph=network(blocked=[(r*11+5,r*11+6) for r in range(10)])
idx,connector=snap(c['xy'],nodes); clinic=22; added_clinic=94
baseline=(shortest(graph,[clinic])[idx]+connector)/80.
improved=(shortest(graph,[clinic,added_clinic])[idx]+connector)/80.
assert np.isfinite(baseline).all() and (improved<=baseline+1e-9).all()
geo=building_features(c,pop)
records=[]
for i,f in enumerate(geo['features']):
    records.append(dict(**f['properties'],polygon=f['geometry']['coordinates'][0],
                        baseline=float(baseline[i]),improved=float(improved[i])))
roads=[[[float(a) for a in lonlat(*nodes[u])],[float(a) for a in lonlat(*nodes[v])]] for u in graph for v,w in graph[u] if u<v]
clinics=[dict(position=[float(v) for v in lonlat(*nodes[node])],added=node==added_clinic) for node in [clinic,added_clinic]]
payload=dict(buildings=records,roads=roads,clinics=clinics,center=[float(v) for v in lonlat(1000,1000)],synthetic=True)
export_json('15_layers.json',payload)
print('Population-weighted minutes:',float(np.average(baseline,weights=pop)),'->',float(np.average(improved,weights=pop)))
'''),
        ('code', '''
fig,axes=plt.subplots(1,2,figsize=(12,5))
for ax,times,label in zip(axes,[baseline,improved],['Existing clinic','Additional clinic']):
    dots=ax.scatter(*c['xy'].T,c=times,vmin=0,vmax=30,cmap='viridis_r',s=25)
    map_axes(ax,label)
fig.colorbar(dots,ax=list(axes),label='Walking minutes (same 0–30 scale)',extend='max'); plt.show()
'''),
        ('markdown', SCENE_HELP),
        ('code', '''
document=export_scene('15_deckgl_scene.html','deck',payload)
display(scene_frame(document,'deck.gl population and access scenario layers'))
'''),
        ('markdown', '''## Astra critique and a Codex layer task
**Astra:** provide `15_layers.json` and screenshots of both scenarios with the same camera.
Ask: “Calculate population-weighted mean travel time for each scenario. Explain whether any building's access
worsened, and identify how the population extrusion could mislead a viewer about physical height.” Check its
numbers against this notebook, not apparent column volume. Declare a 0.01-minute tolerance before the trial.

**Codex:** “Add a population-threshold filter and a served-within-15-minutes color mode in
`content/scene_templates/deck.html`. Preserve the original arrays, keep tooltips exact, and show the visible
population separately from the whole-city total. Make the legend and table reflect the active mode.”

**Acceptance:** additional-clinic travel time never exceeds baseline; population is conserved; selecting a
display metric changes no numerical data; the same color maps to the same value in both scenarios.
Try the scene with keyboard-accessible selects and compare its table with the Python export.

References: [deck.gl standalone](https://deck.gl/docs/get-started/using-standalone) and
[PolygonLayer](https://deck.gl/docs/api-reference/layers/polygon-layer).''')],
        'Add trips or OD arcs with timestamps and explicit units. Keep a fixed color domain across animation frames, distinguish observed journeys from synthetic routes, and test that filtering does not silently change summary denominators.')

    notebook('16_terrain_3d', '16 · Terrain and water-level exploration in 3D',
        'How much of a dramatic terrain scene is data, and how much is display exaggeration?',
        'Have Astra compare the 3D rendering with a cell-based area calculation and ask Codex for controls that preserve vertical units.', [
        ('markdown', '''## Surface, datum and screening plane · 30 minutes
**Learn:** construct a 3D surface from a raster, label a vertical datum, and compare a threshold area with a visual impression.
Plotly supplies an orbitable scientific surface rather than a tiled geographic basemap. Coordinates are local
east/north metres; elevations use an invented datum. Each of 40 × 40 cells represents 50 × 50 m, sampled at
its center. The surface interpolates between centers for display; area uses full cell counts.
**Predict:** does changing vertical exaggeration change the area below the water plane?
This threshold model omits drainage and hydraulic connectivity. It is not a flood forecast.'''),
        ('code', '''
from scenes import export_scene, scene_frame
pixel_m=50.; axis=(np.arange(40)+.5)*pixel_m
xx,yy=np.meshgrid(axis,axis)
elevation=1000+.003*xx+.002*yy-4*np.exp(-((xx-1100)/250)**2)
water_level=1001.
below=elevation<water_level
area_m2=int(below.sum())*pixel_m**2
levels=np.arange(998,1008.5,.5)
areas=np.array([np.count_nonzero(elevation<level)*pixel_m**2 for level in levels])
assert (np.diff(areas)>=0).all() and 0<=area_m2<=2000**2
assert elevation.shape==(40,40) and len(axis)*pixel_m==2000
print('Cells below plane:',int(below.sum()),'| screening area:',area_m2,'m²')
payload=dict(x=axis.tolist(),y=axis.tolist(),z=elevation.tolist(),pixel_m=pixel_m,
             synthetic=True,datum='invented local vertical reference',units='metres')
export_json('16_terrain.json',payload)
'''),
        ('code', '''
fig,axes=plt.subplots(1,2,figsize=(12,5))
image=axes[0].imshow(elevation,origin='lower',extent=[0,2000,0,2000],cmap='terrain',vmin=995,vmax=1012)
axes[0].contour(xx,yy,elevation,levels=[water_level],colors=['#176caf'])
map_axes(axes[0],'Plan view and 1001 m contour'); fig.colorbar(image,ax=axes[0],label='Synthetic elevation (m)')
axes[1].plot(levels,areas/1e6,marker='o',color='#087f8c')
axes[1].set(xlabel='Water screening level (m)',ylabel='Area below plane (km²)',title='Cell-based sensitivity; not hydraulic extent')
plt.tight_layout(); plt.show()
'''),
        ('markdown', SCENE_HELP),
        ('code', '''
document=export_scene('16_terrain_scene.html','terrain',payload)
display(scene_frame(document,'Synthetic terrain and water screening plane'))
'''),
        ('markdown', '''## Astra map audit and a Codex surface task
**Astra:** send `16_terrain.json` and screenshots at 1× and 30× vertical exaggeration.
Ask: “How many cell centers lie below 1001 m, and what full-cell area does that represent? Why do the two
views imply different apparent slopes but the same area? Which evidence is missing for a real flood map?”
Grade count and area exactly against the cell calculation; review the scientific explanation separately.

**Codex:** “Add an elevation cross-section at a selected row to `content/scene_templates/terrain.html`.
Keep its y-axis in real metres regardless of 3D exaggeration. Mark the selected row on the scene and test
the cross-section against the corresponding exported array.”

**Acceptance:** water-level increases cannot reduce threshold area; exaggeration cannot change elevations
or cell counts; row zero is south; datum and units remain visible. Record the exact prompt and response before
using the reference calculation to evaluate it.

Reference: [Plotly JavaScript surface plots](https://plotly.com/javascript/3d-surface-plots/).
For georeferenced terrain tiles or a globe, MapLibre terrain or CesiumJS is a further extension requiring
documented elevation sources, licensing and vertical references.''')],
        'Replace the synthetic raster with a small licensed DEM chip after preprocessing CRS, nodata and vertical datum. Preserve a static plan view and hand-checked area calculation; separate hydraulic modeling from a water-plane visualization.')
