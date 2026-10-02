"""Edge cases for the shared numerical contracts."""
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'content'))
from twin import allocate, local_xy, lonlat, network, shortest, mobility, grade_spatial_answer
from experiments import paired_change, access_summary, grade_answer, spatial_suite, grade_suite
from scenes import building_features, scene_html
from twin import city
import json

class Contracts(unittest.TestCase):
    def test_allocation(self):
        np.testing.assert_array_equal(allocate([1,1,0],5),[3,2,0])
        np.testing.assert_array_equal(allocate([1,2],0),[0,0])
        for weights,total in [([0,0],4),([-1,2],4),([1,np.nan],4),([1],-1),([1],1.5)]:
            with self.assertRaises(ValueError): allocate(weights,total)
    def test_roundtrip(self):
        points=np.array([[-100,0],[2000,2000],[0,-100]])
        np.testing.assert_allclose(np.array(local_xy(*lonlat(*points.T))).T,points,atol=1e-6)
    def test_graph(self):
        _,g=network(n=2,step=100)
        np.testing.assert_array_equal(shortest(g,[0]),[0,100,100,200])
        _,g=network(n=2,step=100,blocked=[(0,1),(0,2)])
        self.assertTrue(np.isinf(shortest(g,[0])[1:]).all())
    def test_exposure(self):
        a=mobility(seed=1); b=mobility(seed=1,ventilation=2)
        np.testing.assert_allclose(a['dose'],2*b['dose'])
        np.testing.assert_array_equal(a['trajectory'],b['trajectory'])
    def test_invalid_model_answers(self):
        truth=dict(nearest='A',northmost='C',distance_m=500)
        for text in ['not json','[]','{}','{"nearest":[],"northmost":"C","distance_m":500}',
                     '{"nearest":"A","northmost":"C","distance_m":true}',
                     '{"nearest":"A","northmost":"C","distance_m":NaN}']:
            self.assertFalse(grade_spatial_answer(text,truth,['A','B','C'])['schema_ok'])
        self.assertTrue(grade_spatial_answer('{"nearest":"A","northmost":"C","distance_m":500}',truth,['A','B','C'])['distance_pass'])

    def test_paired_raster(self):
        result=paired_change([[.8,.6],[np.nan,.4]],[[.4,np.nan],[.2,.4]],10,.2)
        self.assertEqual(result['valid_pixels'],2)
        self.assertEqual(result['loss_pixels'],1)
        self.assertEqual(result['loss_area_m2'],100)
        self.assertAlmostEqual(result['mean_change'],-.2)
        self.assertIsNone(paired_change([[np.nan]],[[0]],10,.2)['mean_change'])
        with self.assertRaises(ValueError): paired_change([[0]],[[0,1]],10,.2)

    def test_coverage_denominator(self):
        result=access_summary([5,np.inf],[60,40],15)
        self.assertEqual(result['coverage'],.6)
        self.assertEqual(result['unreachable_population'],40)
        self.assertEqual(result['mean_reachable_min'],5)
        self.assertIsNone(access_summary([np.inf],[10],15)['mean_reachable_min'])
        with self.assertRaises(ValueError): access_summary([np.nan],[10],15)

    def test_strict_grader(self):
        for text in ['{"x":true}','{"x":NaN}','{"x":Infinity}','{"x":1,"x":2}','[]','{"x":1,"extra":0}']:
            self.assertFalse(grade_answer(text,{'x':1})['schema_ok'])
        self.assertTrue(grade_answer('{"x":1.01}',{'x':1},{'x':.02})['passed'])
        self.assertFalse(grade_answer('{"x":2}',{'x':1})['passed'])
        self.assertTrue(grade_answer('{"x":null}',{'x':None})['passed'])
        self.assertFalse(grade_answer('{"x":0}',{'x':None})['passed'])

    def test_suite_reference_independent_checks(self):
        # BFS independently checks unit-weight routing; rectangle inequalities check boundaries.
        cases,answers=spatial_suite(41,30)
        self.assertEqual((cases,answers),spatial_suite(41,30))
        for case in cases:
            evidence=case['evidence']; expected=answers[case['case_id']]
            if case['family']=='routing':
                adjacency={i:[] for i in range(16)}
                for u,v,w in evidence['edges']: adjacency[u].append(v); adjacency[v].append(u)
                steps={0:0}; queue=[0]
                for u in queue:
                    for v in adjacency[u]:
                        if v not in steps: steps[v]=steps[u]+1; queue.append(v)
                self.assertEqual(expected['reachable'],15 in steps)
                self.assertEqual(expected['distance_m'],steps[15]*100 if 15 in steps else None)
            elif case['family']=='containment':
                a,b,c,d=evidence['bounds']; x,y=evidence['point']
                self.assertEqual(expected['inside'],a<=x<=c and b<=y<=d)
        missing=dict(answers); missing.pop(cases[0]['case_id'])
        report=grade_suite(json.dumps(missing),cases,answers)
        self.assertEqual(report['total'],30); self.assertEqual(report['passed'],29)
        self.assertEqual(grade_suite('[]',cases,answers)['passed'],0)
        missing['fabricated']={}
        self.assertEqual(grade_suite(json.dumps(missing),cases,answers)['unexpected_ids'],['fabricated'])

    def test_3d_coordinate_and_height_contract(self):
        c=city(n=4); pop=allocate(c['capacity'],100)
        geo=building_features(c,pop)
        for i,f in enumerate(geo['features']):
            ring=np.array(f['geometry']['coordinates'][0]); xy=np.array(local_xy(*ring.T)).T
            np.testing.assert_allclose(xy[:4].mean(axis=0),c['xy'][i],atol=1e-6)
            self.assertAlmostEqual(np.ptp(xy[:,0]),c['width'][i],places=6)
            self.assertEqual(f['properties']['height_m'],int(c['floors'][i])*3)
        self.assertEqual(sum(f['properties']['population'] for f in geo['features']),100)
        document=scene_html('maplibre',{'text':'</script><script>alert(1)</script>'})
        self.assertNotIn('"text": "</script>',document)
        self.assertNotIn('__DATA__',document)

if __name__=='__main__': unittest.main()
