"""Executable extension cells for notebooks 01–04."""
EXTENSIONS = {
'01': dict(title='Audit a real footprint extract before measuring it',
    branches=['OSM rings + source IDs','Bounds, closure, crossings','Flag map + valid areas','Incomplete map ≠ census'],
    explanation='Load 125 small OpenStreetMap building ways, retaining ODbL attribution and source timestamps. Audit them before calculating approximate local areas. A second copy deliberately contains four errors: swapped axes, an open ring, a crossing ring and a duplicate ID. The audit supports simple polygon exteriors; unsupported geometry is flagged rather than silently flattened.',
    code='''
from copy import deepcopy
from extension_tools import audit_footprints, load_data
ex_real=load_data('gaborone_buildings.geojson')
ex_audit=audit_footprints(ex_real,bbox=[25.89,-24.70,25.94,-24.65])
ex_good=[r for r in ex_audit if not r['issues']]
assert ex_good and len({f['id'] for f in ex_real['features']})==len(ex_real['features'])
ex_broken=deepcopy(ex_real['features'][:1])*1
ex_axis=deepcopy(ex_real['features'][0]); ex_axis['id']='axis_error'
ex_axis['geometry']['coordinates'][0]=[p[::-1] for p in ex_axis['geometry']['coordinates'][0]]
ex_open=deepcopy(ex_real['features'][0]); ex_open['id']='open_ring'; ex_open['geometry']['coordinates'][0].pop()
ex_cross=dict(type='Feature',id='crossed',properties={},geometry=dict(type='Polygon',coordinates=[[[25.91,-24.68],[25.912,-24.678],[25.91,-24.678],[25.912,-24.68],[25.91,-24.68]]]))
ex_broken += [ex_axis,ex_open,ex_cross,deepcopy(ex_real['features'][0])]
ex_faults=audit_footprints(dict(features=ex_broken),[25.89,-24.70,25.94,-24.65])
assert sum(bool(r['issues']) for r in ex_faults)==4
fig,axes=plt.subplots(1,3,figsize=(14,4))
for feature,audit in zip(ex_real['features'],ex_audit):
    ring=np.array(feature['geometry']['coordinates'][0]); x,y=local_xy(*ring.T)
    axes[0].fill(x,y,color='#087f8c' if not audit['issues'] else '#c44e52',alpha=.65)
axes[0].set(title='Real OSM footprints: audit first',xlabel='Local east (m)',ylabel='Local north (m)',aspect='equal')
axes[1].hist([r['area_m2'] for r in ex_good],bins=15,color='#087f8c'); axes[1].set(title='Only valid rings contribute area',xlabel='Approximate footprint m²',ylabel='Buildings')
ex_labels=['axis_error','open_ring','crossed',ex_real['features'][0]['id']]
axes[2].barh(ex_labels,[len(r['issues']) for r in ex_faults[1:]],color='#c44e52'); axes[2].set(title='Injected defects detected',xlabel='Failed checks')
fig.text(.01,.01,'© OpenStreetMap contributors · ODbL 1.0 · openstreetmap.org/copyright',fontsize=9)
fig.tight_layout(rect=[0,.05,1,1]); extension_figure=fig
extension_evidence=dict(provenance=ex_real['provenance'],features=ex_broken,study_bbox=[25.89,-24.70,25.94,-24.65])
extension_expected=dict(invalid_features=4)
extension_task='Audit these simple polygon records for coordinate order, study bounds, closure, crossings and duplicate IDs. Return invalid_features as the number of records with any defect.'
print('Real extract:',len(ex_real['features']),'| accepted:',len(ex_good),'| injected bad records:',4)
'''),
'02': dict(title='Constrain neighborhoods and map allocation uncertainty',
    branches=['Four invented area totals','Allocate within each area','Conservation + range maps','Floors are not occupants'],
    explanation='Allocate independently within four geographic quadrants, then compare single-floor, generated-floor and taller-building assumptions. Every scenario conserves each neighborhood total. The spread describes sensitivity to assumptions, not a confidence interval or observed household occupancy. Real OSM height fields are inspected separately: missing height remains unknown.',
    code='''
from extension_tools import load_data
ex_c=city(); ex_groups=(ex_c['xy'][:,0]>=1000).astype(int)+2*(ex_c['xy'][:,1]>=1000)
ex_totals=np.array([300,250,400,250]); ex_floor_options=[np.ones(144),ex_c['floors'],ex_c['floors']+2]
ex_allocations=[]
for floors in ex_floor_options:
    allocation=np.zeros(144,dtype=int)
    for group,total in enumerate(ex_totals):
        mask=ex_groups==group
        allocation[mask]=allocate(ex_c['width'][mask]*ex_c['depth'][mask]*floors[mask]*ex_c['residential'][mask],int(total))
        assert allocation[mask].sum()==total
    assert allocation.sum()==1200 and not allocation[~ex_c['residential']].any()
    ex_allocations.append(allocation)
ex_allocations=np.array(ex_allocations); ex_spread=np.ptp(ex_allocations,axis=0)
ex_reassigned=int(abs(ex_allocations[1]-ex_allocations[0]).sum()//2)
print('Minimum residents reassigned between flat and generated-floor scenarios:',ex_reassigned)
fig,axes=plt.subplots(1,3,figsize=(14,4))
for ax,values,title,cmap in zip(axes,[ex_groups,ex_allocations[1]-ex_allocations[0],ex_spread],['Neighborhood constraints','People reassigned: floors minus flat','Range across floor assumptions'],['tab10','coolwarm','magma']):
    options={}
    if title.startswith('People'):
        limit=max(1,int(abs(values).max())); options=dict(vmin=-limit,vmax=limit)
    dots=ax.scatter(*ex_c['xy'].T,c=values,cmap=cmap,s=30,**options); map_axes(ax,title)
    colorbar=fig.colorbar(dots,ax=ax,label='Area ID' if title.startswith('Neighborhood') else 'People')
    if title.startswith('Neighborhood'): colorbar.set_ticks([0,1,2,3])
    ax.axvline(1000,color='gray',lw=.6); ax.axhline(1000,color='gray',lw=.6)
fig.tight_layout(); extension_figure=fig
ex_osm=load_data('gaborone_buildings.geojson'); ex_missing=sum(f['properties']['height_m'] is None for f in ex_osm['features'])
print('Scenario neighborhood totals:',[[int(a[ex_groups==g].sum()) for g in range(4)] for a in ex_allocations])
print('Real OSM features without reported height:',ex_missing,'— do not invent measured heights.')
extension_evidence=dict(neighborhood_totals=ex_totals.tolist(),population_by_scenario=ex_allocations.tolist(),group=ex_groups.tolist(),units='people',minimum_reassigned=ex_reassigned,floor_scenarios=['one','generated','generated plus two'])
extension_expected=dict(total_population=1200,max_building_range=int(ex_spread.max()))
extension_task='Verify population conservation and calculate the largest per-building population range across scenarios. Return total_population and max_building_range. The range is assumption sensitivity, not a statistical confidence interval.'
'''),
'03': dict(title='Access depends on mode, hours, waiting and capacity',
    branches=['Street graph + residents','Mode / opening / capacity','Unserved population map','Greedy ≠ optimal assignment'],
    explanation='Compare walking, slower accessible travel, a closed facility, and a six-minute transfer wait. An inaccessible crossing disconnects one part of the accessible network. A shortest-pair greedy allocation respects clinic capacities and explicitly records unserved residents; it is a transparent heuristic, not an optimal service allocation. The transfer wait is an invented scenario, not an observed combi schedule.',
    code='''
from extension_tools import capacity_assignment
ex_c=city(); ex_pop=allocate(ex_c['capacity'],1200)
ex_barrier=[(r*11+5,r*11+6) for r in range(10)]
ex_nodes,ex_walk=network(blocked=ex_barrier); _,ex_access=network(blocked=ex_barrier+[(115,116)])
ex_idx,ex_connector=snap(ex_c['xy'],ex_nodes); ex_clinics=[22,94]
ex_modes={}; ex_served={}; ex_unserved={}
for label,graph,speed,wait,opened in [('Walk',ex_walk,80.,0.,[True,True]),('Accessible',ex_access,55.,0.,[True,True]),('Late / east closed',ex_access,55.,0.,[True,False]),('Transfer wait',ex_walk,80.,6.,[True,True])]:
    times=np.column_stack([(shortest(graph,[node])[ex_idx]+ex_connector)/speed+wait if is_open else np.full(144,np.inf) for node,is_open in zip(ex_clinics,opened)])
    allocation,unserved=capacity_assignment(times,ex_pop,[600,400])
    ex_modes[label]=times; ex_served[label]=allocation; ex_unserved[label]=unserved
    assert allocation.sum()+unserved.sum()==1200
fig,axes=plt.subplots(1,3,figsize=(14,4))
labels=list(ex_modes); axes[0].barh(labels,[ex_unserved[k].sum() for k in labels],color='#c44e52')
axes[0].set(title='Capacity + disconnection + hours',xlabel='Unserved residents')
for label in labels:
    nearest=ex_modes[label].min(axis=1)
    coverage=[float(ex_pop[nearest<=limit].sum()/1200) for limit in [5,10,15,20,30]]
    assert (np.diff(coverage)>=0).all()
    axes[1].plot([5,10,15,20,30],coverage,marker='o',label=label)
ex_original_coverage={}
for label,travel in [('Baseline: 1 clinic',base),('Chosen addition',improved)]:
    values=[float(pop[travel<=limit].sum()/pop.sum()) for limit in [5,10,15,20,30]]
    assert (np.diff(values)>=0).all()
    ex_original_coverage[label]=values
    axes[1].plot([5,10,15,20,30],values,ls='--',label=label)
assert (improved<=base+1e-10).all()
axes[1].set(xlabel='Travel threshold (min)',ylabel='Fraction of all residents',title='Potential access before capacity'); axes[1].legend(fontsize=7)
dots=axes[2].scatter(*ex_c['xy'].T,c=ex_unserved['Late / east closed'],s=30,cmap='magma'); map_axes(axes[2],'Late-session unserved residents'); fig.colorbar(dots,ax=axes[2],label='People')
fig.tight_layout(); extension_figure=fig
extension_evidence=dict(population=1200,capacity=[600,400],unserved_by_mode={k:int(v.sum()) for k,v in ex_unserved.items()},original_clinic_coverage=ex_original_coverage,thresholds_min=[5,10,15,20,30],assumptions='Greedy shortest-pair allocation; synthetic schedules and travel modes')
extension_expected=dict(capacity_shortfall=200,worst_mode=max(ex_unserved,key=lambda k:ex_unserved[k].sum()))
extension_task='Compute the minimum shortfall from nominal capacity alone and name the scenario with the largest unserved total. Return capacity_shortfall and worst_mode. Explain no extra claims in the JSON.'
'''),
'04': dict(title='Inspect real Sentinel reflectance, masks and scale',
    branches=['Sentinel red / NIR / SCL','Scale, mask, compute NDVI','Valid pixels + uncertainty','NDVI is not temperature'],
    explanation='This bundled 20 m Sentinel-2 chip is real surface-reflectance evidence near the teaching anchor, acquired January 23, 2025. Red/NIR scale and offset were applied during preprocessing; SCL is categorical and resampled with nearest-neighbor logic. We retain vegetation, bare-ground and water classes (4, 5, 6). An additional artificial cloud patch demonstrates missing-data behavior and is explicitly labeled. NDVI is not land-surface or air temperature, and does not validate the earlier cooling equation.',
    code='''
from extension_tools import load_data
from matplotlib.colors import BoundaryNorm, ListedColormap
ex_chip=load_data('sentinel_chip.json'); ex_red=np.array(ex_chip['red']); ex_nir=np.array(ex_chip['nir']); ex_scl=np.array(ex_chip['scl'])
ex_valid=np.isin(ex_scl,[4,5,6]) & ((ex_red+ex_nir)>0)
ex_ndvi=np.full(ex_red.shape,np.nan); ex_ndvi[ex_valid]=(ex_nir[ex_valid]-ex_red[ex_valid])/(ex_nir[ex_valid]+ex_red[ex_valid])
assert np.isfinite(ex_ndvi[ex_valid]).all()
ex_cloud=ex_valid.copy(); ex_cloud[20:35,25:45]=False
ex_masked=np.where(ex_cloud,ex_ndvi,np.nan)
fig,axes=plt.subplots(1,3,figsize=(14,4)); bounds=ex_chip['bounds']; extent=[bounds[0],bounds[2],bounds[1],bounds[3]]
for ax,field,title,cmap in zip(axes,[ex_ndvi,ex_scl,ex_masked],['Real NDVI, original valid pixels','Observed SCL classes','Artificial cloud added for teaching'],['RdYlGn','tab10','RdYlGn']):
    options=dict(vmin=-1,vmax=1) if title!='Observed SCL classes' else dict(norm=BoundaryNorm([3.5,4.5,5.5,6.5],3))
    if title=='Observed SCL classes': cmap=ListedColormap(['#328a55','#c9a16a','#398ac4'])
    image=ax.imshow(field,extent=extent,origin='upper',cmap=cmap,**options); colorbar=fig.colorbar(image,ax=ax,shrink=.72,pad=.08)
    if title=='Observed SCL classes': colorbar.set_ticks([4,5,6],labels=['Vegetation','Not vegetated','Water'])
    short_title={'Real NDVI, original valid pixels':'Observed NDVI','Observed SCL classes':'Observed SCL classes','Artificial cloud added for teaching':'NDVI with artificial cloud'}[title]
    ax.set(title=short_title,xlabel='UTM easting (m)',ylabel='UTM northing (m)'); ax.ticklabel_format(style='plain',useOffset=False)
    ax.title.set_fontsize(10); ax.tick_params(labelsize=8); colorbar.ax.tick_params(labelsize=8)
    ax.set_xticks(np.linspace(extent[0],extent[1],3))
fig.text(.01,.01,'Contains modified Copernicus Sentinel data (2025) · ESA / Element 84 · '+ex_chip['crs'],fontsize=9)
fig.tight_layout(rect=[0,.05,1,1]); extension_figure=fig
print('Observed mean NDVI:',float(np.nanmean(ex_ndvi)),'| after artificial cloud mask:',float(np.nanmean(ex_masked)))
print('Original area vs population-weighted cooling:',float(effect.mean()),float(before_mean-after_mean),'synthetic °C')
assert pop.sum()==1200 and np.array_equal(heat-0*effect,heat)
extension_evidence=dict(provenance=ex_chip['provenance'],original_valid_pixels=int(ex_valid.sum()),retained_pixels=int(ex_cloud.sum()),pixel_m=20,artificial_cloud=True,synthetic_cooling=dict(area_average_c=float(effect.mean()),population_weighted_c=float(before_mean-after_mean),sampling='Nearest raster pixel; row = northing; all 1200 residents included'))
extension_expected=dict(hidden_area_m2=int((ex_valid&~ex_cloud).sum())*400,temperature_observed=False)
extension_task='Calculate area hidden by the added artificial cloud and determine whether red/NIR NDVI observes temperature. Return hidden_area_m2 and temperature_observed.'
''')}
