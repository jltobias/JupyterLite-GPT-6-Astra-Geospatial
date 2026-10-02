"""Executable extension cells for notebooks 09–12."""
EXTENSIONS={
'09':dict(title='Build a map atlas with ambiguity and held-out tasks',
    branches=['Thirty reserved-seed cases','Coordinates / graph / boundaries','Atlas + schema-aware scoring','Keep modalities separate'],
    explanation='Generate 30 fresh tasks and an atlas of representative maps. Add exact distance ties, a missing-scale case that requires abstention, and a plausible-looking axis swap. A trial register distinguishes text-only, image-only and tool-assisted conditions; unrun conditions stay unrun. The correct fixture checks evaluator mechanics and is never reported as Astra accuracy.',
    code='''
from experiments import spatial_suite, grade_suite
ex_cases,ex_answers=spatial_suite(seed=8301,count=30)
ex_cases[0]=dict(case_id='8301-000',family='tie',task='Both places are equidistant. Choose alphabetically. Return nearest.',evidence=dict(places={'A':[0,0],'B':[200,0]},query=[100,0],units='metres'),tolerance={})
ex_answers['8301-000']=dict(nearest='A')
ex_cases[1]=dict(case_id='8301-001',family='missing-scale',task='Coordinates are image pixels with no physical scale. Return distance_m=null and needs_scale=true.',evidence=dict(places={'A':[0,0]},query=[300,400],units='pixels',metres_per_pixel=None),tolerance={})
ex_answers['8301-001']=dict(distance_m=None,needs_scale=True)
ex_cases[2]=dict(case_id='8301-002',family='axis-order',task='Test the coordinate against bbox west,south,east,north. Return plausible.',evidence=dict(point=[-24.68,25.91],bbox=[25.8,-24.8,26.1,-24.5],coordinate_order='longitude,latitude'),tolerance={})
ex_answers['8301-002']=dict(plausible=False)
fig,axes=plt.subplots(2,3,figsize=(13,7))
for ax,case in zip(axes.flat,ex_cases[:6]):
    ev=case['evidence']; family=case['family']
    if 'places' in ev:
        for key,point in ev['places'].items(): ax.scatter(*point,s=50); ax.annotate(key,point)
        ax.scatter(*ev['query'],marker='x',c='black',s=65); ax.annotate('Q',ev['query'])
        ax.set_aspect('equal',adjustable='datalim')
    elif 'edges' in ev:
        for u,v,w in ev['edges']: ax.plot([u%4*100,v%4*100],[u//4*100,v//4*100],c='#087f8c')
        ax.scatter([0,300],[0,300],c=['black','red']); ax.set_aspect('equal')
    elif 'bounds' in ev:
        a,b,c,d=ev['bounds']; ax.add_patch(plt.Rectangle((a,b),c-a,d-b,alpha=.2)); ax.scatter(*ev['point'],c='red'); ax.autoscale_view(); ax.set_aspect('equal')
    else:
        ax.text(.5,.65,'Given lon/lat: '+str(ev['point']),ha='center',transform=ax.transAxes)
        ax.text(.5,.35,'Study bbox: '+str(ev['bbox']),ha='center',transform=ax.transAxes,fontsize=8); ax.axis('off')
    ax.set_title(case['case_id']+' · '+family); ax.set_xlabel(ev.get('units','See explicit coordinate contract'))
fig.tight_layout(); extension_figure=fig
assert grade_suite(json.dumps(ex_answers),ex_cases,ex_answers)['passed']==30
ex_trial_register=[dict(condition=condition,model=None,status='NOT RUN',response_file=None) for condition in ['text-only','image-only','tool-assisted']]
export_json('09_extended_cases.json',dict(cases=ex_cases,instructions='Return JSON keyed by case_id. Send no answer key.'))
export_json('09_trial_register.json',ex_trial_register)
extension_evidence=dict(cases=ex_cases[:3],note='These three cases test tie policy, missing scale and coordinate order.')
extension_expected=dict(tie_nearest='A',needs_scale=True,swapped_pair_plausible=False)
extension_task='Solve the three supplied cases. Return tie_nearest, needs_scale and swapped_pair_plausible. Do not invent a pixel-to-metre scale.'
'''),
'10':dict(title='Batch spatial queries and check a grid index',
    branches=['Point set + many query sites','Batched NumPy / WASM calls','Parity + crossover chart','Finite radius ≠ infinite kernel'],
    explanation='Batch 32 queries into one NumPy operation, compare with repeated NumPy and WASM calls, and map a separate radius-query grid index. The original inverse-quadratic kernel has infinite support: a radius index cannot discard its far-field contributions while claiming exact parity. The index example therefore answers an explicitly different question—points within 200 m—and compares that answer to brute force.',
    code='''
from extension_tools import radius_index, radius_query
ex_queries=np.column_stack([np.linspace(100,1900,32),1000+600*np.sin(np.linspace(0,2*np.pi,32))])
def ex_batch(count,queries,decay=200.):
    i=np.arange(count); points=np.column_stack([i*37%2000,i*71%2000]); d2=((queries[:,None,:]-points[None,:,:])**2).sum(axis=2)
    return (1/(1+d2/decay**2)).sum(axis=1)
ex_sizes=[100,1000,5000]; ex_timings={'Batched NumPy':[],'Repeated NumPy':[]}
if wasm_fn: ex_timings['Repeated WASM']=[]
for count in ex_sizes:
    expected=ex_batch(count,ex_queries)
    functions={'Batched NumPy':lambda:ex_batch(count,ex_queries),'Repeated NumPy':lambda:np.array([vectorized(count,x,y,200.) for x,y in ex_queries])}
    if wasm_fn: functions['Repeated WASM']=lambda:np.array([wasm_fn(count,float(x),float(y),200.) for x,y in ex_queries])
    for name,fn in functions.items():
        assert np.allclose(fn(),expected,rtol=1e-11); samples=[]
        for repeat in range(3): start=time.perf_counter(); fn(); samples.append((time.perf_counter()-start)*1000)
        ex_timings[name].append(float(np.median(samples)))
assert np.array_equal(ex_batch(0,ex_queries),np.zeros(32))
i=np.arange(5000); ex_points=np.column_stack([i*37%2000,i*71%2000]); ex_buckets=radius_index(ex_points,200.)
ex_center=ex_queries[10]; ex_hits=radius_query(ex_points,ex_buckets,ex_center,200.,200.)
ex_brute=np.flatnonzero(np.linalg.norm(ex_points-ex_center,axis=1)<=200.)
assert np.array_equal(ex_hits,ex_brute)
fig,axes=plt.subplots(1,3,figsize=(14,4))
axes[0].scatter(*ex_points.T,s=2,c='#bdcbd0'); axes[0].scatter(*ex_points[ex_hits].T,s=8,c='#087f8c'); axes[0].add_patch(plt.Circle(ex_center,200,fill=False,color='#c44e52')); map_axes(axes[0],'Exact finite-radius index query')
for name,values in ex_timings.items(): axes[1].plot(ex_sizes,values,marker='o',label=name)
axes[1].set(xscale='log',yscale='log',xlabel='Point count',ylabel='Median ms, 3 repeats',title='32 queries on this device'); axes[1].legend(fontsize=8)
dots=axes[2].scatter(*ex_queries.T,c=ex_batch(5000,ex_queries),s=65,cmap='magma'); map_axes(axes[2],'Full-support kernel at query sites'); fig.colorbar(dots,ax=axes[2],label='Kernel sum')
fig.tight_layout(); extension_figure=fig
extension_evidence=dict(timings_ms=ex_timings,point_counts=ex_sizes,query_count=32,index_count=len(ex_hits),brute_force_count=len(ex_brute),kernel='1/(1+distance_squared/200**2)',radius_m=200)
extension_expected=dict(index_matches_brute_force=True,truncation_preserves_full_kernel=False)
extension_task='Return index_matches_brute_force and truncation_preserves_full_kernel. Distinguish the finite-radius count from the full inverse-quadratic sum.'
'''),
'11':dict(title='Separate misregistration from an actual changed patch',
    branches=['Two images + nodata','Shift search without wrapping','Alignment residual maps','Registration needs stable texture'],
    explanation='Translate a textured synthetic raster by one pixel and search a small set of corrections using median absolute residual. A separate injected change patch remains after alignment. Search candidates use a central comparison window, jointly valid pixels for each shift and explicit nodata padding; no pixels wrap around the image. This texture, shift and changed patch are controlled synthetic experiments, not measured environmental change. Compare their assumptions with the real Sentinel evidence in notebook 04.',
    code='''
from extension_tools import shift_grid
from experiments import paired_change
rng=np.random.default_rng(54); ex_reference=rng.uniform(.2,.8,(32,32))
ex_changed=ex_reference.copy(); ex_changed[12:18,15:22]-=.25
ex_observed=shift_grid(ex_changed,1,1); ex_observed[3:7,20:25]=np.nan
ex_candidates=[]
for dy in range(-2,3):
    for dx in range(-2,3):
        shifted=shift_grid(ex_observed,dy,dx); residual=(shifted-ex_reference)[4:-4,4:-4]
        ex_candidates.append((float(np.nanmedian(abs(residual))),dy,dx))
ex_score,ex_dy,ex_dx=min(ex_candidates); assert (ex_dy,ex_dx)==(-1,-1)
ex_aligned=shift_grid(ex_observed,ex_dy,ex_dx)
ex_raw=paired_change(ex_reference,ex_observed,20,.2); ex_fixed=paired_change(ex_reference,ex_aligned,20,.2)
assert ex_fixed['loss_pixels']==42
assert paired_change([[np.nan]],[[np.nan]],20,.2)['mean_change'] is None
assert paired_change([[.8,.5],[.4,.3]],[[.4,.5],[.4,.3]],10,.2)['loss_area_m2']==100
fig,axes=plt.subplots(1,3,figsize=(14,4))
for ax,field,title in zip(axes,[ex_raw['delta'],ex_fixed['delta'],ex_fixed['loss']],['Before registration: false change','After alignment: changed patch remains','Detected loss on valid paired pixels']):
    image=ax.imshow(field,origin='lower',extent=[0,640,0,640],cmap='coolwarm',vmin=-.5 if field.dtype!=bool else 0,vmax=.5 if field.dtype!=bool else 1)
    ax.set(title=title,xlabel='Local east (m)',ylabel='Local north (m)'); fig.colorbar(image,ax=ax)
fig.tight_layout(); extension_figure=fig
extension_evidence=dict(search=[dict(median_abs_residual=s,dy=dy,dx=dx) for s,dy,dx in ex_candidates],aligned_loss_pixels=ex_fixed['loss_pixels'],pixel_m=20,nodata='masked, never zero-filled')
extension_expected=dict(correction_dy=-1,correction_dx=-1,loss_area_m2=16800)
extension_task='Select the shift minimizing median absolute residual and compute aligned loss area. Return correction_dy, correction_dx and loss_area_m2.'
'''),
'12':dict(title='Assign residents to capacity-limited facilities',
    branches=['Demand + candidate travel times','Capacity-constrained heuristic','Flows / unserved / group coverage','Service capacity is an assumption'],
    explanation='For each candidate clinic, assign residents using a transparent shortest-pair greedy rule with an explicitly unserved category. Compare 200, 400 and 600 places of added capacity. Report population conservation, facility utilization and geographic-group service fractions. Candidate enumeration is exhaustive, but the assignment inside each candidate is a heuristic; its result must not be labeled a globally optimal allocation.',
    code='''
from extension_tools import capacity_assignment
ex_c=city(); ex_pop=allocate(ex_c['capacity'],1200); ex_nodes,ex_graph=network(blocked=[(r*11+5,r*11+6) for r in range(10)])
ex_idx,ex_connector=snap(ex_c['xy'],ex_nodes); ex_west=ex_c['xy'][:,0]<1100; ex_results=[]
for added in [200,400,600]:
    for candidate in [6,28,50,72,94,116]:
        times=np.column_stack([(shortest(ex_graph,[node])[ex_idx]+ex_connector)/80 for node in [22,candidate]])
        # A 20-minute service limit is part of eligibility, not just presentation.
        times[times>20]=np.inf; assignment,unserved=capacity_assignment(times,ex_pop,[600,added])
        group_coverage=[float(assignment[mask].sum()/ex_pop[mask].sum()) for mask in [ex_west,~ex_west]]
        ex_results.append(dict(added_capacity=added,node=candidate,served=int(assignment.sum()),unserved=int(unserved.sum()),worst_group=min(group_coverage),utilization=assignment.sum(axis=0).tolist()))
        assert (assignment.sum(axis=0)<=np.array([600,added])).all()
ex_choice=min([r for r in ex_results if r['added_capacity']==400],key=lambda r:(-r['worst_group'],-r['served'],r['node']))
times=np.column_stack([(shortest(ex_graph,[node])[ex_idx]+ex_connector)/80 for node in [22,ex_choice['node']]])
times[times>20]=np.inf; ex_assignment,ex_unserved=capacity_assignment(times,ex_pop,[600,400])
fig,axes=plt.subplots(1,3,figsize=(14,4))
for added in [200,400,600]:
    subset=[r for r in ex_results if r['added_capacity']==added]; axes[0].plot([r['node'] for r in subset],[r['worst_group'] for r in subset],marker='o',label=f'+{added} places')
axes[0].set(xlabel='Candidate node',ylabel='Worst-group served fraction',title='Capacity changes the siting objective'); axes[0].legend(fontsize=8)
for j,node in enumerate([22,ex_choice['node']]):
    for i in np.flatnonzero(ex_assignment[:,j]): axes[1].plot([ex_c['xy'][i,0],ex_nodes[node,0]],[ex_c['xy'][i,1],ex_nodes[node,1]],alpha=.2,lw=.5,c=['#087f8c','#b87922'][j])
axes[1].scatter(*ex_nodes[[22,ex_choice['node']]].T,c='black',marker='*',s=100); map_axes(axes[1],'Assignment desire lines (not street routes)')
dots=axes[2].scatter(*ex_c['xy'].T,c=ex_unserved,cmap='magma',s=30); map_axes(axes[2],'Explicit unserved residents'); fig.colorbar(dots,ax=axes[2],label='People')
fig.tight_layout(); extension_figure=fig
extension_evidence=dict(candidates=[r for r in ex_results if r['added_capacity']==400],objective='maximize worst_group, then served, then lowest node',total_population=1200,service_limit_min=20)
extension_expected=dict(chosen_node=ex_choice['node'],unserved=ex_choice['unserved'])
extension_task='Select from the candidate results under the declared objective. Return chosen_node and unserved. These are results of a capacity-limited heuristic, not a claim of global optimality.'
''')}
