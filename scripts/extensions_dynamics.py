"""Executable extension cells for notebooks 05–08."""
EXTENSIONS={
'05':dict(title='Flood thresholds, edge sampling and alternative facilities',
    branches=['Terrain + streets + clinics','Sample endpoints AND midpoint','Disconnected people by level','Screening is not hydraulics'],
    explanation='Compare endpoint-only closures with endpoint-plus-midpoint sampling over a range of water levels. Two alternative clinics are available only while dry. The plots keep unreachable people separate from travel time among reachable people. More sampling can reveal low road segments; it does not turn this screening equation into a hydraulic model.',
    code='''
ex_c=city(); ex_pop=allocate(ex_c['capacity'],1200); ex_nodes,ex_graph=network(); ex_idx,ex_connector=snap(ex_c['xy'],ex_nodes)
def ex_height(points):
    x,y=np.asarray(points).T; return 1000+.003*x+.002*y-4*np.exp(-((x-1100)/250)**2)
ex_levels=np.arange(998.,1005.1,1.); ex_counts={'Endpoints':[],'With midpoint':[]}; ex_means=[]
for level in ex_levels:
    ex_clinics=[node for node in [110,120] if ex_height(ex_nodes[[node]])[0]>=level]
    for method in ex_counts:
        graph={u:[] for u in ex_graph}
        for u,edges in ex_graph.items():
            for v,w in edges:
                samples=np.array([ex_nodes[u],ex_nodes[v]])
                if method=='With midpoint': samples=np.vstack([samples,(ex_nodes[u]+ex_nodes[v])/2])
                if ex_height(samples).min()>=level: graph[u].append((v,w))
        times=(shortest(graph,ex_clinics)[ex_idx]+ex_connector)/80
        reachable=np.isfinite(times); ex_counts[method].append(int(ex_pop[~reachable].sum()))
        if method=='With midpoint': ex_means.append(float(np.average(times[reachable],weights=ex_pop[reachable])) if ex_pop[reachable].sum() else None)
        if method=='With midpoint' and level==1001.: ex_example=(graph,times,ex_clinics)
assert (np.diff(ex_counts['With midpoint'])>=0).all()
assert (np.array(ex_counts['With midpoint'])>=ex_counts['Endpoints']).all()
fig,axes=plt.subplots(1,3,figsize=(14,4))
for method,counts in ex_counts.items(): axes[0].plot(ex_levels,counts,marker='o',label=method)
axes[0].set(title='Disconnected people, all residents counted',xlabel='Screening water level (m)',ylabel='Residents'); axes[0].legend(fontsize=8)
axes[1].plot(ex_levels,[np.nan if v is None else v for v in ex_means],marker='o'); axes[1].set(title='Conditional mean: reachable people only',xlabel='Water level (m)',ylabel='Walking min')
graph,times,clinics=ex_example
for u,edges in graph.items():
    for v,w in edges:
        if u<v: axes[2].plot(*ex_nodes[[u,v]].T,c='#bacad0',lw=.6)
axes[2].scatter(*ex_c['xy'].T,c=np.isfinite(times),cmap='coolwarm_r',s=20)
axes[2].scatter(*ex_nodes[clinics].T,c='gold',marker='*',s=100); map_axes(axes[2],'1001 m: blue reachable, red disconnected')
fig.tight_layout(); extension_figure=fig
extension_evidence=dict(levels_m=ex_levels.tolist(),unreachable_population=ex_counts,reachable_mean_min=ex_means,total_population=1200)
extension_expected=dict(max_unreachable=max(ex_counts['With midpoint']),midpoint_never_improves_access=True)
extension_task='Report max_unreachable across midpoint scenarios and midpoint_never_improves_access, a boolean describing whether stricter closure sampling can restore a path in this fixed graph.'
'''),
'06':dict(title='Link activity histories to places, routes and contact layers',
    branches=['Building IDs + shared events','Homes / work / vehicle layers','Route map + seed comparison','Arbitrary dose ≠ disease'],
    explanation='Attach synthetic place IDs to a building inventory and draw a vehicle route along the street grid. Compare ventilation 1×, 2× and 4× across three fixed seeds using common trajectories within each seed. Split events into household, workplace and vehicle layers. Vehicle positions are illustrative route locations; the original coarse half-hour activity schedule is not GPS tracking or a disease kernel.',
    code='''
ex_c=city(); ex_place_xy=ex_c['xy'][:48]; ex_nodes,ex_graph=network()
ex_route_nodes=list(range(11))+list(range(21,121,11)); ex_route=ex_nodes[ex_route_nodes]
assert all(any(v==b for v,w in ex_graph[a]) for a,b in zip(ex_route_nodes,ex_route_nodes[1:]))
ex_means=[]; ex_layers=[]
for seed in [7,17,27]:
    base=mobility(seed=seed); means=[]
    for ventilation in [1.,2.,4.]:
        run=mobility(seed=seed,ventilation=ventilation)
        assert np.array_equal(run['trajectory'],base['trajectory'])
        assert np.allclose(run['dose'],base['dose']/ventilation)
        means.append(float(run['dose'][run['susceptible']].mean()))
    ex_means.append(means)
    ex_layers.append([sum(e['people']*e['sources']*.02*.5 for e in base['events'] if (e['place']<40 if layer==0 else 40<=e['place']<48 if layer==1 else e['place']>=48)) for layer in range(3)])
ex_run=mobility(seed=7); ex_ids=ex_run['trajectory'][:,0]
ex_agent_xy=np.array([ex_place_xy[p] if p<48 else ex_route[(t*3)%len(ex_route)] for t,p in enumerate(ex_ids)])
fig,axes=plt.subplots(1,3,figsize=(14,4))
axes[0].scatter(*ex_place_xy[:40].T,s=12,label='Home places'); axes[0].scatter(*ex_place_xy[40:].T,marker='s',label='Work places')
axes[0].plot(*ex_route.T,c='#c68423',label='Illustrative vehicle route'); axes[0].scatter(*ex_agent_xy[[0,16,36]].T,c=['black','red','purple'],s=65)
map_axes(axes[0],'Places + street-constrained vehicle route'); axes[0].legend(fontsize=7)
for seed,values in zip([7,17,27],ex_means): axes[1].plot([1,2,4],values,marker='o',label=f'Seed {seed}')
axes[1].set(xlabel='Ventilation multiplier',ylabel='Mean arbitrary dose',title='Common trajectories, changed ventilation'); axes[1].legend(fontsize=8)
bottom=np.zeros(3)
for j,layer in enumerate(['Household','Workplace','Vehicle']):
    values=np.array(ex_layers)[:,j]; axes[2].bar(['7','17','27'],values,bottom=bottom,label=layer); bottom+=values
axes[2].set(xlabel='Seed',ylabel='Summed event dose (all agents)',title='Shared-setting layers'); axes[2].legend(fontsize=8)
fig.tight_layout(); extension_figure=fig
extension_evidence=dict(seeds=[7,17,27],ventilation=[1,2,4],mean_dose=ex_means,units='arbitrary dose',route_node_ids=ex_route_nodes)
extension_expected=dict(dose_ratio_4_to_1=.25,route_uses_street_edges=True)
extension_task='Return dose_ratio_4_to_1 and route_uses_street_edges. Infer the ratio from the fixed-trajectory experiment; grid nodes are row-major on an 11 by 11 grid and consecutive route nodes are listed.'
'''),
'07':dict(title='Map stale sensors and test uncertainty on held-out streams',
    branches=['Timestamped sensor sites','Reject / predict / update','Coverage + staleness maps','Model intervals need calibration'],
    explanation='Six mapped sensors have noisy signals, inserted gaps and outliers. Validate timestamp order, track time since the last accepted observation, and compare interval coverage on 30 independently seeded streams under correctly specified and underestimated observation noise. Coverage is measured rather than forced to 95%; rejection and finite samples can change it.',
    code='''
from extension_tools import kalman_stream, timestamp_check
ex_times=np.datetime64('2026-01-01T00:00')+np.arange(80)*np.timedelta64(15,'m')
assert timestamp_check(ex_times) and not timestamp_check(ex_times[::-1])
ex_sites=city(seed=91,n=6)['xy']; ex_truths=[]; ex_observed=[]; ex_estimates=[]; ex_variances=[]; ex_ages=[]
for site in range(6):
    rng=np.random.default_rng(100+site); truth=30+np.cumsum(rng.normal(0,np.sqrt(.12),80)); observed=truth+rng.normal(0,np.sqrt(1.5),80)
    observed[20:28+site]=np.nan; observed[45]+=15
    mean,var,age=kalman_stream(observed); ex_truths.append(truth); ex_observed.append(observed); ex_estimates.append(mean); ex_variances.append(var); ex_ages.append(age)
ex_coverage={}
for assumed in [.15,1.5,6.]:
    cover=[]
    for seed in range(1000,1030):
        rng=np.random.default_rng(seed); truth=30+np.cumsum(rng.normal(0,np.sqrt(.12),80)); obs=truth+rng.normal(0,np.sqrt(1.5),80); obs[20:28]=np.nan
        mean,var,_=kalman_stream(obs,assumed_sensor_var=assumed); cover.append(float(np.mean(abs(mean-truth)<=1.96*np.sqrt(var))))
    ex_coverage[str(assumed)]=cover
fig,axes=plt.subplots(1,3,figsize=(14,4)); ex_snapshot=30
dots=axes[0].scatter(*ex_sites.T,c=np.array(ex_ages)[:,ex_snapshot],s=150,cmap='magma')
for i,xy in enumerate(ex_sites): axes[0].annotate(f'S{i}',xy,xytext=(5,5),textcoords='offset points')
map_axes(axes[0],'Time since last accepted reading'); fig.colorbar(dots,ax=axes[0],label='15-minute steps')
ex_errors=np.array(ex_estimates)-np.array(ex_truths)
image=axes[1].imshow(ex_errors,aspect='auto',cmap='coolwarm',vmin=-3,vmax=3); axes[1].set(title='Spatial sensor residuals',xlabel='Time step',ylabel='Sensor ID'); fig.colorbar(image,ax=axes[1],label='Synthetic °C error')
axes[2].boxplot(list(ex_coverage.values()),tick_labels=list(ex_coverage)); axes[2].axhline(.95,ls='--',c='gray'); axes[2].set(xlabel='Assumed sensor variance',ylabel='Empirical interval coverage',title='30 held-out streams, true variance 1.5',ylim=(0,1.05))
fig.tight_layout(); extension_figure=fig
extension_evidence=dict(coverage={k:float(np.mean(v)) for k,v in ex_coverage.items()},ages_at_step_30=np.array(ex_ages)[:,30].tolist(),interval='mean ± 1.96 standard deviations',step_minutes=15)
extension_expected=dict(stalest_sensor=int(np.argmax(np.array(ex_ages)[:,30])),max_staleness_minutes=int(np.max(np.array(ex_ages)[:,30])*15))
extension_task='Return stalest_sensor (zero-based ID) and max_staleness_minutes from the provided age vector. Age measures accepted observations, not merely a sensor transmission.'
'''),
'08':dict(title='Learn nonlinear spatial dynamics and expose extrapolation',
    branches=['Neighborhood states + actions','Nonlinear simulator / ensemble','Rollout error + support map','Simulator fidelity ≠ causality'],
    explanation='Introduce nonlinear congestion and fit an ensemble of linear surrogates using whole training trajectories. Evaluate horizons 1, 10 and 35 on held-out episodes, alongside persistence. Map predicted changes for a grid of synthetic neighborhoods. An out-of-support action is shown separately; ensemble spread is a diagnostic, not calibrated real-world uncertainty.',
    code='''
def ex_dynamics(state,action):
    state=np.asarray(state); action=np.asarray(action)
    return transition(state,action)+np.stack([.025*state[...,1]**2-.03*state[...,0]*action[...,0],.07*np.tanh(state[...,1]**2)],axis=-1)
rng=np.random.default_rng(212); ex_episodes=[]
for episode in range(40):
    state=rng.uniform(.1,2,2); rows=[]
    for step in range(40):
        action=rng.uniform(0,.6,2); nxt=ex_dynamics(state,action); rows.append((state.copy(),action.copy(),nxt.copy())); state=nxt
    ex_episodes.append(rows)
ex_ensemble=[]
for member in range(12):
    selected=rng.choice(30,30,replace=True); rows=[r for episode in selected for r in ex_episodes[episode]]
    s,a,t=map(np.array,zip(*rows)); ex_ensemble.append(np.linalg.lstsq(features(s,a),t,rcond=None)[0])
ex_models=np.array(ex_ensemble); ex_horizons=[1,10,35]; ex_errors=[]; ex_persist=[]
for horizon in ex_horizons:
    errors=[]; persistence=[]
    for episode in range(30,40):
        start=ex_episodes[episode][0][0]; true=start.copy(); pred=start.copy()
        for step in range(horizon):
            action=ex_episodes[episode][step][1]; true=ex_dynamics(true,action); pred=(features(pred,action)@ex_models.mean(axis=0))[0]
        errors.append(np.mean((pred-true)**2)); persistence.append(np.mean((start-true)**2))
    ex_errors.append(float(np.sqrt(np.mean(errors)))); ex_persist.append(float(np.sqrt(np.mean(persistence))))
ex_x,ex_y=np.meshgrid(np.linspace(100,1900,8),np.linspace(100,1900,8)); ex_states=np.column_stack([.5+ex_y.ravel()/2000,.5+ex_x.ravel()/2000])
ex_action=np.array([.4,.5]); ex_base=ex_dynamics(ex_states,[0,0]); ex_policy=ex_dynamics(ex_states,ex_action)
ex_predictions=np.array([features(ex_states,np.tile(ex_action,(64,1)))@model for model in ex_models])
fig,axes=plt.subplots(1,3,figsize=(14,4))
dots=axes[0].scatter(ex_x,ex_y,c=(ex_policy-ex_base)[:,0],s=80,cmap='coolwarm',vmin=-.15,vmax=.15); map_axes(axes[0],'Synthetic neighborhood heat change'); fig.colorbar(dots,ax=axes[0],label='Dimensionless heat')
axes[1].plot(ex_horizons,ex_errors,marker='o',label='Linear surrogate'); axes[1].plot(ex_horizons,ex_persist,marker='s',label='Persistence'); axes[1].set(xlabel='Rollout horizon',ylabel='RMSE',title='Whole held-out trajectories'); axes[1].legend(fontsize=8)
axes[2].add_patch(plt.Rectangle((0,0),.6,.6,color='#087f8c',alpha=.2)); axes[2].scatter([.4,1.2],[.5,1.2],c=['#087f8c','#c44e52'],s=90)
axes[2].annotate('Supported',(.4,.5)); axes[2].annotate('Extrapolation',(1.2,1.2),ha='right'); axes[2].set(xlim=(0,1.4),ylim=(0,1.4),xlabel='Cooling action',ylabel='Transit action',title='Declared training support')
fig.tight_layout(); extension_figure=fig
print('Mean ensemble predictive spread:',float(ex_predictions.std(axis=0).mean()),'— not calibrated uncertainty')
extension_evidence=dict(horizons=ex_horizons,surrogate_rmse=ex_errors,persistence_rmse=ex_persist,training_action_bounds=[0,.6],proposed_action=[1.2,1.2],training_episodes=list(range(30)),test_episodes=list(range(30,40)))
extension_expected=dict(episode_overlap=0,proposed_action_supported=False)
extension_task='Audit the split and action support. Return episode_overlap and proposed_action_supported. Do not infer causal validity from simulator error.'
''')}
