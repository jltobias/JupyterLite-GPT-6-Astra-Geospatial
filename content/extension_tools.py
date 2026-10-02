"""Inspectable reference methods for the extended notebook investigations."""
import json
import math
import textwrap
from pathlib import Path
import numpy as np
from twin import local_xy, export_json


def concept_map(title, branches):
    """A labeled mind map: input, operation, evidence, and limits."""
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(12,4.5)); ax.set(xlim=(-3.6,3.6),ylim=(-1.6,1.6)); ax.axis('off')
    ax.text(0,0,textwrap.fill(title,22),ha='center',va='center',fontsize=13,weight='bold',
            bbox=dict(boxstyle='round,pad=.8',fc='#123d49',ec='none'),color='white')
    positions=[(-2.5,1), (2.5,1),(-2.5,-1),(2.5,-1)]
    labels=['INPUT','METHOD','EVIDENCE','LIMIT']
    for (x,y),label,description in zip(positions,labels,branches):
        ax.annotate('',xy=(x*.7,y*.7),xytext=(x*.25,y*.25),arrowprops=dict(arrowstyle='->',color='#7296a0',lw=2))
        ax.text(x,y,label+'\n'+textwrap.fill(description,28),ha='center',va='center',fontsize=10,
                bbox=dict(boxstyle='round,pad=.6',fc='#e1eff0' if label!='LIMIT' else '#fff0d9',ec='#a9c1c8'))
    fig.tight_layout(); return fig


def audit_footprints(collection, bbox=None):
    """Audit simple Polygon exteriors. Holes/MultiPolygons are explicitly unsupported.

    Flags closure, finite coordinates, duplicate IDs, crossings and local area.
    This is an educational audit, not a full OGC validity implementation.
    """
    rows=[]; seen=set()
    def cross(a,b,c):
        u,v=b-a,c-a
        return float(u[0]*v[1]-u[1]*v[0])
    for feature in collection['features']:
        key=feature.get('id'); issues=[]; geometry=feature.get('geometry',{})
        if key in seen: issues.append('duplicate ID')
        if key is None: issues.append('missing ID')
        seen.add(key); area=None
        if geometry.get('type')!='Polygon' or len(geometry.get('coordinates',[]))!=1:
            issues.append('unsupported geometry')
        else:
            try:
                ring=np.asarray(geometry['coordinates'][0],float)
                if ring.ndim!=2 or ring.shape[1]!=2 or len(ring)<4 or not np.isfinite(ring).all(): raise ValueError()
                if not np.array_equal(ring[0],ring[-1]): issues.append('unclosed ring')
                if (abs(ring[:,0])>180).any() or (abs(ring[:,1])>90).any(): issues.append('invalid longitude/latitude')
                if bbox is not None:
                    w,s,e,n=bbox
                    if not ((ring[:,0]>=w)&(ring[:,0]<=e)&(ring[:,1]>=s)&(ring[:,1]<=n)).all(): issues.append('outside study bounds')
                xy=np.array(local_xy(*ring.T)).T
                for i in range(len(xy)-1):
                    for j in range(i+2,len(xy)-1):
                        if i==0 and j==len(xy)-2: continue
                        a,b=xy[i:i+2]; c,d=xy[j:j+2]
                        if cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0:
                            issues.append('self intersection')
                area=abs(float(np.dot(xy[:-1,0],xy[1:,1])-np.dot(xy[1:,0],xy[:-1,1])))/2
                if area<=1e-8: issues.append('zero area')
            except (ValueError,TypeError,IndexError): issues.append('invalid coordinate array')
        rows.append(dict(id=key,issues=sorted(set(issues)),area_m2=area if not issues else None))
    return rows


def capacity_assignment(times, population, capacities):
    """Greedy shortest-pair assignment with explicit unserved people; NOT an optimizer."""
    times=np.asarray(times,float); pop=np.asarray(population,int); cap=np.asarray(capacities,int)
    if times.shape!=(len(pop),len(cap)) or (pop<0).any() or (cap<0).any() or np.isnan(times).any() or (times<0).any():
        raise ValueError('Invalid times, population or capacities')
    remaining=pop.copy(); spare=cap.copy(); assigned=np.zeros_like(times,dtype=int)
    for flat in np.argsort(times,axis=None,kind='stable'):
        i,j=np.unravel_index(flat,times.shape)
        if not np.isfinite(times[i,j]): continue
        count=min(remaining[i],spare[j]); assigned[i,j]+=count; remaining[i]-=count; spare[j]-=count
    assert np.array_equal(assigned.sum(axis=1)+remaining,pop)
    assert (assigned.sum(axis=0)<=cap).all()
    return assigned,remaining


def kalman_stream(observations, process_var=.12, assumed_sensor_var=1.5):
    values=[]; variances=[]; stale=[]; age=0; mean=30.; var=4.
    for obs in observations:
        var+=process_var; age+=1
        if np.isfinite(obs) and abs(obs-mean)<=4*np.sqrt(var+assumed_sensor_var):
            gain=var/(var+assumed_sensor_var); mean+=gain*(obs-mean); var*=1-gain; age=0
        values.append(mean); variances.append(var); stale.append(age)
    return np.array(values),np.array(variances),np.array(stale)


def timestamp_check(times):
    values=np.asarray(times,dtype='datetime64[s]')
    return bool(not np.isnat(values).any() and (np.diff(values)>np.timedelta64(0,'s')).all())


def polygon_relation(point, exterior, holes=(), tolerance=1e-8):
    """Ray casting with explicit boundary classification, including hole boundaries."""
    p=np.asarray(point,float)
    def ring_relation(ring):
        r=np.asarray(ring,float); inside=False
        for a,b in zip(r,np.roll(r,-1,axis=0)):
            delta=b-a
            if np.linalg.norm(delta)==0: continue
            t=np.dot(p-a,delta)/np.dot(delta,delta)
            if -tolerance<=t<=1+tolerance and np.linalg.norm(p-(a+np.clip(t,0,1)*delta))<=tolerance: return 'boundary'
            if (a[1]>p[1])!=(b[1]>p[1]) and p[0] < a[0]+(p[1]-a[1])*(b[0]-a[0])/(b[1]-a[1]): inside=not inside
        return 'inside' if inside else 'outside'
    outer=ring_relation(exterior)
    if outer!='inside': return outer
    for hole in holes:
        relation=ring_relation(hole)
        if relation=='boundary': return 'boundary'
        if relation=='inside': return 'outside'
    return 'inside'


def shift_grid(grid, dy, dx):
    """Translate with nodata padding; never wrap values across image edges."""
    a=np.asarray(grid,float); out=np.full_like(a,np.nan)
    if abs(dy)>=a.shape[0] or abs(dx)>=a.shape[1]: return out
    ys=slice(max(0,-dy),min(a.shape[0],a.shape[0]-dy)); xs=slice(max(0,-dx),min(a.shape[1],a.shape[1]-dx))
    yd=slice(max(0,dy),min(a.shape[0],a.shape[0]+dy)); xd=slice(max(0,dx),min(a.shape[1],a.shape[1]+dx))
    out[yd,xd]=a[ys,xs]; return out


def radius_index(points, cell_m):
    buckets={}
    for i,key in enumerate(np.floor(np.asarray(points)/cell_m).astype(int)):
        buckets.setdefault(tuple(key),[]).append(i)
    return buckets


def radius_query(points, buckets, center, radius, cell_m):
    low=np.floor((np.asarray(center)-radius)/cell_m).astype(int)
    high=np.floor((np.asarray(center)+radius)/cell_m).astype(int)
    candidates=[i for x in range(low[0],high[0]+1) for y in range(low[1],high[1]+1) for i in buckets.get((x,y),[])]
    return np.array(sorted(i for i in candidates if np.linalg.norm(points[i]-center)<=radius),dtype=int)


def export_investigation(number, evidence, expected, task, fig):
    """Separate evidence-only prompt from the reference; no generated model claims."""
    directory=Path('exports'); directory.mkdir(exist_ok=True)
    image_name=f'{number}_extension_map.png'; fig.savefig(directory/image_name,bbox_inches='tight')
    prompt=dict(task=task,output_fields=list(expected),evidence=evidence,
                instructions='Return only JSON with exactly output_fields. Respect units and missing data. Do not infer unsupported geographic or causal facts.')
    export_json(f'{number}_extension_prompt.json',prompt)
    return prompt,expected


def load_data(name):
    return json.loads((Path(__file__).resolve().parent/'data'/name).read_text(encoding='utf-8'))
