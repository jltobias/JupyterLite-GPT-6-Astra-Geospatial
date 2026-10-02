"""Executable extension cells for notebooks 13–16."""
EXTENSIONS={
'13':dict(title='Evaluate polygon holes and explicit boundary semantics',
    branches=['Exterior + interior ring','Ray casting + boundary checks','Hole map + failure cases','A bounding box is insufficient'],
    explanation='Add a fourth benchmark family: polygon containment with a hole. A point in the hole is outside; either ring boundary is labeled boundary, avoiding an implicit contains-versus-covers convention. Ten new cases are added to the existing 30-case suite inside this notebook. Check missing answers, fabricated IDs and malformed JSON before running any model trial.',
    code='''
from extension_tools import polygon_relation
ex_outer=[[200,200],[1800,200],[1800,1800],[200,1800]]; ex_hole=[[800,800],[1200,800],[1200,1200],[800,1200]]
ex_points=[[400,400],[1000,1000],[800,1000],[200,500],[1900,1000],[1200,1200],[1600,900],[750,1000],[1000,1250],[0,0]]
ex_relations=[polygon_relation(p,ex_outer,[ex_hole]) for p in ex_points]
assert ex_relations[:5]==['inside','outside','boundary','boundary','outside']
ex_extra=[]; ex_keys=dict(answer_key)
for i,p in enumerate(ex_points):
    key=f'holes-991-{i:02d}'; ex_extra.append(dict(case_id=key,family='polygon-holes',task='Return relation: inside, outside or boundary. Hole interiors are outside; either ring edge is boundary.',evidence=dict(point=p,exterior=ex_outer,holes=[ex_hole],units='metres'),tolerance={}))
    ex_keys[key]=dict(relation=ex_relations[i])
ex_all=cases+ex_extra; ex_fixture=json.dumps(ex_keys)
assert grade_suite(ex_fixture,ex_all,ex_keys)['passed']==len(ex_all)
ex_fabricated=dict(ex_keys); ex_fabricated['invented-id']={}
assert grade_suite(json.dumps(ex_fabricated),ex_all,ex_keys)['unexpected_ids']==['invented-id']
ex_missing=dict(ex_keys); ex_missing.pop(ex_extra[0]['case_id'])
assert grade_suite(json.dumps(ex_missing),ex_all,ex_keys)['passed']==len(ex_all)-1
assert grade_suite('not JSON',ex_all,ex_keys)['passed']==0
fig,axes=plt.subplots(1,2,figsize=(12,5))
for ax in axes:
    ax.add_patch(plt.Polygon(ex_outer,color='#087f8c',alpha=.2)); ax.add_patch(plt.Polygon(ex_hole,color='white',ec='#c44e52',lw=2)); map_axes(ax,'Boundary and hole semantics')
for i,(p,relation) in enumerate(zip(ex_points,ex_relations)):
    axes[0].scatter(*p,c={'inside':'#087f8c','outside':'#c44e52','boundary':'#b47b00'}[relation],s=60); axes[0].annotate(str(i),p,xytext=(5,5),textcoords='offset points')
axes[1].text(1000,1450,'Polygon interior',ha='center'); axes[1].text(1000,1000,'Hole = outside',ha='center'); axes[1].annotate('Hole edge = boundary',xy=(800,1000),xytext=(250,500),arrowprops=dict(arrowstyle='->'))
fig.tight_layout(); extension_figure=fig
export_json('13_four_family_tasks.json',dict(cases=ex_all,synthetic=True,condition='text-evidence; no answer key supplied'))
extension_evidence=dict(exterior=ex_outer,holes=[ex_hole],points=ex_points,units='metres',boundary_policy='separate boundary label')
extension_expected=dict(inside_count=ex_relations.count('inside'),boundary_count=ex_relations.count('boundary'),outside_count=ex_relations.count('outside'))
extension_task='Classify the listed points against the polygon and hole under the declared policy. Return inside_count, boundary_count and outside_count.'
'''),
'14':dict(title='Import real footprints and preserve unknown heights',
    branches=['OSM IDs + height tags','Audit / filter / preserve nulls','Real map + assumption range','Missing height stays unknown'],
    explanation='Import the bundled OSM extract with source IDs, timestamps and license. None of these 125 buildings reports a numeric height; the map therefore keeps them flat and labels height as unknown. A separate chart shows how assumed heights change hypothetical volume, explicitly distinguishing assumptions from observations. The interactive building scene now includes the requested minimum-floor filter, visible counts and a synchronized table.',
    code='''
from extension_tools import load_data, audit_footprints
from scenes import export_scene, scene_frame
from copy import deepcopy
ex_real=load_data('gaborone_buildings.geojson'); ex_audit=audit_footprints(ex_real)
ex_features=[]; ex_areas=[]
for f,r in zip(ex_real['features'],ex_audit):
    if r['issues']: continue
    feature=deepcopy(f); p=feature['properties']; ex_areas.append(r['area_m2'])
    p.update(id=f['id'],floors=p['levels'],population=None,residential=False,height_known=p['height_m'] is not None)
    ex_features.append(feature)
ex_known=sum(f['properties']['height_known'] for f in ex_features)
ex_coordinates=np.concatenate([np.array(f['geometry']['coordinates'][0]) for f in ex_features])
fig,axes=plt.subplots(1,2,figsize=(12,5))
for f in ex_features:
    ring=np.array(f['geometry']['coordinates'][0]); axes[0].fill(*np.array(local_xy(*ring.T)),color='#8c9ca5',alpha=.65)
axes[0].set(aspect='equal',xlabel='Local east (m)',ylabel='Local north (m)',title='Real footprints; height unavailable')
ex_assumed=[3,6,9]; ex_volume=[float(sum(ex_areas)*h) for h in ex_assumed]
axes[1].bar(['Assume 3 m','Assume 6 m','Assume 9 m'],ex_volume,color='#b88741'); axes[1].set(ylabel='Hypothetical total volume (m³)',title='Height assumptions, NOT observed volume')
fig.text(.01,.01,'© OpenStreetMap contributors · ODbL 1.0 · openstreetmap.org/copyright',fontsize=9); fig.tight_layout(rect=[0,.05,1,1]); extension_figure=fig
ex_payload=dict(buildings=dict(type='FeatureCollection',features=ex_features),roads=dict(type='FeatureCollection',features=[]),center=ex_coordinates.mean(axis=0).tolist(),zoom=17.5,
    title='Real footprints, unknown heights',description='OSM geometry is observed mapping evidence; absent heights remain unknown and render flat.',attribution='© OpenStreetMap contributors · ODbL 1.0 · openstreetmap.org/copyright',synthetic=False)
ex_document=export_scene('14_real_footprints.html','maplibre',ex_payload); display(scene_frame(ex_document,'Real OSM footprint audit with unknown heights'))
assert ex_known==sum(f['properties']['height_m'] is not None for f in ex_features)
extension_evidence=dict(provenance=ex_real['provenance'],feature_count=len(ex_features),reported_height_count=ex_known,total_footprint_m2=float(sum(ex_areas)),assumed_heights_m=ex_assumed)
extension_expected=dict(measured_height_count=ex_known,can_infer_real_volume=False)
extension_task='Return measured_height_count (reported numeric height fields) and can_infer_real_volume. Missing tags must not become fabricated measurements.'
'''),
'15':dict(title='Add timestamped street trips and explicit filtering',
    branches=['Timed synthetic node paths','Move along verified edges','OD map + active-trip timeline','Straight OD lines are not routes'],
    explanation='Construct timestamped trips along verified edges of the synthetic street graph. The scene adds a moving trip marker layer, a population filter and a served-within-15-minutes color mode. Legends and tables follow the active filter; the full-city total stays visible. The static map shows routed polylines and their origin/destination markers; the neighboring timeline shows departure and arrival times.',
    code='''
ex_nodes,ex_graph=network(blocked=[(r*11+5,r*11+6) for r in range(10)]); ex_trips=[]
for j in range(8):
    row=j+1; path=list(range(row*11,row*11+6))+[r*11+5 for r in range(row+1,11)]+[116]+[r*11+6 for r in range(9,row-1,-1)]+list(range(row*11+7,row*11+11)); start=j*3.
    times=(start+np.arange(len(path))*200/80).tolist()
    assert np.all(np.diff(times)>0) and all(any(v==b for v,w in ex_graph[a]) for a,b in zip(path,path[1:]))
    ex_trips.append(dict(id=f'trip-{j}',node_ids=path,timestamps_min=times,path=[[float(a) for a in lonlat(*ex_nodes[node])] for node in path]))
payload['trips']=ex_trips
document=export_scene('15_deckgl_scene.html','deck',payload)
display(scene_frame(document,'deck.gl access filters and timestamped trips'))
ex_snapshot=18.; ex_active=[t for t in ex_trips if t['timestamps_min'][0]<=ex_snapshot<=t['timestamps_min'][-1]]
fig,axes=plt.subplots(1,3,figsize=(14,4))
for t in ex_trips:
    path=ex_nodes[t['node_ids']]; axes[0].plot(*path.T,alpha=.6)
    axes[0].scatter(*path[0],marker='o',s=20,c='black'); axes[0].scatter(*path[-1],marker='>',s=30,c='#c44e52')
map_axes(axes[0],'Verified street-edge trip paths')
for j,t in enumerate(ex_trips): axes[1].plot([t['timestamps_min'][0],t['timestamps_min'][-1]],[j,j],lw=5)
axes[1].axvline(ex_snapshot,c='#c44e52',ls='--'); axes[1].set(xlabel='Minutes from scenario start',ylabel='Trip ID',title='Which trips are active at 18 minutes?')
ex_cutoffs=[0,5,10,20,1000]; ex_visible=[int(sum(r['population'] for r in records if r['population']>=cutoff)) for cutoff in ex_cutoffs]
axes[2].bar([str(x) for x in ex_cutoffs],ex_visible,color='#087f8c'); axes[2].axhline(1200,c='gray',ls='--'); axes[2].set(xlabel='Minimum building population',ylabel='Visible residents',title='Filtering is not population change')
assert ex_visible[0]==1200 and ex_visible[-1]==0
fig.tight_layout(); extension_figure=fig
extension_evidence=dict(trips=ex_trips,snapshot_min=ex_snapshot,population_cutoffs=ex_cutoffs,visible_population=ex_visible,full_city_population=1200)
extension_expected=dict(active_trips=len(ex_active),full_city_population=1200)
extension_task='Count trips active at the snapshot (including endpoints) and retain the unfiltered population total. Return active_trips and full_city_population.'
'''),
'16':dict(title='Inspect a real terrain chip and an elevation cross-section',
    branches=['Terrarium DEM + sample centers','Decode / orient / inspect nodata','Hillshade + profile + 3D','Vertical datum not independently verified'],
    explanation='Load a bundled Mapzen terrain extract near Gaborone, decoded from Terrarium RGB and downsampled on the desktop. It retains actual sample coordinates, processing notes and source attribution. Work in elevation relative to the chip minimum because this composite’s vertical datum has not been independently verified. The 3D inspector adds a selectable cross-section whose elevations remain in real metres when the view is exaggerated. A below-plane area remains a screening statistic, never a hydraulic flood extent.',
    code='''
from extension_tools import load_data
from scenes import export_scene, scene_frame
ex_dem=load_data('gaborone_terrain.json'); ex_z=np.array(ex_dem['z']); ex_x=np.array(ex_dem['x']); ex_y=np.array(ex_dem['y'])
assert ex_z.shape==(len(ex_y),len(ex_x)) and np.isfinite(ex_z).all() and (np.diff(ex_x)>0).all() and (np.diff(ex_y)>0).all()
ex_relative=ex_z-ex_z.min(); ex_row=16; ex_level=10.
gy,gx=np.gradient(ex_relative,ex_y,ex_x); ex_hill=np.clip((1-gx-gy)/np.sqrt(3*(1+gx*gx+gy*gy)),0,1)
ex_area=float(np.count_nonzero(ex_relative<ex_level)*ex_dem['pixel_area_m2'])
fig,axes=plt.subplots(1,3,figsize=(14,4)); extent=[ex_x.min(),ex_x.max(),ex_y.min(),ex_y.max()]
axes[0].imshow(ex_hill,origin='lower',extent=extent,cmap='gray'); axes[0].axhline(ex_y[ex_row],color='#c44e52'); axes[0].set(title='Real terrain hillshade + profile row',xlabel='Local east (m)',ylabel='Local north (m)')
image=axes[1].imshow(ex_relative,origin='lower',extent=extent,cmap='terrain'); fig.colorbar(image,ax=axes[1],label='Metres above chip minimum'); axes[1].set(title='Relative elevation, datum caveat retained',xlabel='Local east (m)',ylabel='Local north (m)')
axes[2].plot(ex_x,ex_relative[ex_row],c='#087f8c'); axes[2].axhline(ex_level,c='#318dcc',ls='--'); axes[2].set(title='Cross-section: real vertical units',xlabel='Local east (m)',ylabel='Metres above chip minimum')
fig.text(.01,.01,'Mapzen terrain tiles · USGS SRTM/GMTED2010 / NOAA ETOPO1 · see data provenance for processing and attribution',fontsize=8)
fig.tight_layout(rect=[0,.05,1,1]); extension_figure=fig
ex_payload=dict(x=ex_x.tolist(),y=ex_y.tolist(),z=ex_relative.tolist(),pixel_m=float(np.sqrt(ex_dem['pixel_area_m2'])),relative=True,attribution=ex_dem['provenance']['attribution'],title='Real terrain: relative elevation',description='Mapzen chip near Gaborone; elevations relative to the chip minimum; vertical datum not independently verified.')
ex_html=export_scene('16_real_terrain.html','terrain',ex_payload); display(scene_frame(ex_html,'Real terrain chip and selectable cross-section'))
extension_evidence=dict(provenance=ex_dem['provenance'],profile_m=ex_relative[ex_row].tolist(),cell_count_below_plane=int(np.count_nonzero(ex_relative<ex_level)),cell_area_m2=ex_dem['pixel_area_m2'],plane_m_above_minimum=ex_level)
extension_expected=dict(profile_range_m=float(np.ptp(ex_relative[ex_row])),below_plane_area_m2=ex_area)
extension_task='Calculate profile_range_m and below_plane_area_m2. Use the provided cell-area approximation and do not interpret the screening plane as a flood forecast.'
''')}
