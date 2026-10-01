"""Small deterministic spatial models. All generated city data are synthetic."""
import heapq
import json
import math
from pathlib import Path
import numpy as np

ORIGIN = (25.91, -24.68)  # approximate Gaborone-area anchor, not a surveyed location
R = 6371008.8

def lonlat(x, y):
    return (ORIGIN[0] + np.asarray(x) / (R * math.cos(math.radians(ORIGIN[1]))) * 180 / math.pi,
            ORIGIN[1] + np.asarray(y) / R * 180 / math.pi)

def local_xy(lon, lat):
    return ((np.asarray(lon) - ORIGIN[0]) * math.pi / 180 * R * math.cos(math.radians(ORIGIN[1])),
            (np.asarray(lat) - ORIGIN[1]) * math.pi / 180 * R)

def city(seed=42, n=144):
    rng = np.random.default_rng(seed)
    xy = rng.uniform(80, 1920, (n, 2))
    width = rng.uniform(12, 35, n)
    depth = rng.uniform(12, 28, n)
    floors = rng.integers(1, 4, n)
    residential = rng.random(n) > .2
    capacity = width * depth * floors * residential
    return dict(xy=xy, width=width, depth=depth, floors=floors,
                residential=residential, capacity=capacity)

def allocate(weights, total):
    """Largest remainder apportionment; exact integer conservation."""
    weights = np.asarray(weights, dtype=float)
    if not np.isfinite(weights).all() or (weights < 0).any() or weights.sum() <= 0:
        raise ValueError('weights must be finite, nonnegative and have positive sum')
    if not isinstance(total, (int, np.integer)) or total < 0:
        raise ValueError('total must be a nonnegative integer')
    raw = weights / weights.sum() * total
    result = np.floor(raw).astype(int)
    result[np.argsort(-(raw-result), kind='stable')[:total-int(result.sum())]] += 1
    return result

def network(n=11, step=200., blocked=()):
    xy = np.array([(x*step, y*step) for y in range(n) for x in range(n)])
    blocked = {tuple(sorted(e)) for e in blocked}
    graph = {i: [] for i in range(n*n)}
    for u in graph:
        x, y = u % n, u // n
        for v in ([u+1] if x<n-1 else []) + ([u+n] if y<n-1 else []):
            if tuple(sorted((u,v))) not in blocked:
                graph[u].append((v, step)); graph[v].append((u, step))
    return xy, graph

def shortest(graph, sources):
    dist = {u: math.inf for u in graph}
    queue = []
    for source in sources:
        dist[source] = 0.; heapq.heappush(queue, (0., source))
    while queue:
        d, u = heapq.heappop(queue)
        if d != dist[u]: continue
        for v, w in graph[u]:
            if w < 0: raise ValueError('Dijkstra requires nonnegative weights')
            candidate = d+w
            if candidate < dist[v]:
                dist[v] = candidate; heapq.heappush(queue, (candidate, v))
    return np.array([dist[u] for u in sorted(graph)])

def snap(points, nodes):
    distances = np.linalg.norm(np.asarray(points)[:,None,:]-nodes[None,:,:], axis=2)
    idx = distances.argmin(axis=1)
    return idx, distances[np.arange(len(idx)),idx]

def raster(size=40):
    a = np.linspace(0,2000,size)
    xx, yy = np.meshgrid(a,a)
    green = np.exp(-((xx-500)**2+(yy-1400)**2)/(2*450**2))
    heat = 33 + 3*np.sin(xx/450)*np.cos(yy/650) - 5*green
    elevation = 1000 + .003*xx + .002*yy - 4*np.exp(-((xx-1100)/250)**2)
    return xx, yy, green, heat, elevation

def mobility(seed=7, ventilation=1., agents=160, steps=48):
    """Toy daily shared-setting contact model; no disease progression or calibration."""
    rng = np.random.default_rng(seed)
    homes = rng.integers(0,40,agents)
    work = rng.integers(40,48,agents)
    infectious = np.zeros(agents,dtype=bool); infectious[:4] = True
    dose = np.zeros(agents); events=[]; trajectory=[]
    for t in range(steps):
        hour=t*24/steps
        loc = homes.copy()
        if 8<=hour<17: loc=work.copy()
        if 7<=hour<8 or 17<=hour<18: loc=48+(np.arange(agents)%4)
        for place in np.unique(loc):
            people=np.flatnonzero(loc==place); sources=int(infectious[people].sum())
            if sources:
                dose[people] += sources*.02*(24/steps)/ventilation
                events.append(dict(step=t, place=int(place), people=len(people), sources=sources))
        trajectory.append(loc.copy())
    return dict(dose=dose, susceptible=~infectious, events=events, trajectory=np.array(trajectory))

def transition(state, action, noise=None):
    """Invented two-variable urban heat/congestion dynamics, dimensionless."""
    heat, traffic = np.asarray(state).T
    cooling, transit = np.asarray(action).T
    next_state = np.stack([.86*heat+.08*traffic-.22*cooling+.12,
                           .91*traffic-.25*transit+.10],axis=-1)
    return next_state + (0 if noise is None else noise)

def features(state, action):
    state=np.atleast_2d(state); action=np.atleast_2d(action)
    return np.column_stack([np.ones(len(state)),state,action])

def grade_spatial_answer(text, truth, labels, tolerance_m=1.):
    """Treat invalid model output as a failed trial rather than crashing the evaluator."""
    try:
        answer=json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {'schema_ok':False, 'reason':'invalid JSON'}
    ok=(isinstance(answer,dict) and set(answer)=={'nearest','distance_m','northmost'}
        and isinstance(answer['nearest'],str) and answer['nearest'] in labels
        and isinstance(answer['northmost'],str) and answer['northmost'] in labels
        and type(answer['distance_m']) in (int,float)
        and math.isfinite(answer['distance_m']) and answer['distance_m']>=0)
    if not ok: return {'schema_ok':False,'reason':'wrong fields, types or values'}
    error=abs(answer['distance_m']-truth['distance_m'])
    return dict(schema_ok=True,nearest_correct=answer['nearest']==truth['nearest'],
                northmost_correct=answer['northmost']==truth['northmost'],
                distance_absolute_error_m=error,distance_pass=error<=tolerance_m)

def export_json(name, payload):
    folder=Path('exports'); folder.mkdir(exist_ok=True)
    path=folder/name
    path.write_text(json.dumps(payload, indent=2, allow_nan=False),encoding='utf-8')
    print('Saved',path,'- download from the JupyterLite file browser to keep a copy.')
    return path

def style():
    import matplotlib.pyplot as plt
    plt.rcParams.update({'figure.figsize':(9,5),'axes.spines.top':False,
                         'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,
                         'font.size':11,'figure.dpi':110})

def map_axes(ax, title):
    ax.set(xlabel='Local east (m)',ylabel='Local north (m)',title=title,
           xlim=(-50,2050),ylim=(-50,2050),aspect='equal')
