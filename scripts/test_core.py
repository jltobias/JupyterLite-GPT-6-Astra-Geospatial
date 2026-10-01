"""Edge cases for the shared numerical contracts."""
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'content'))
from twin import allocate, local_xy, lonlat, network, shortest, mobility, grade_spatial_answer

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

if __name__=='__main__': unittest.main()
