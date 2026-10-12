import unittest
from validate_tender import load,check_data
class ReviewTests(unittest.TestCase):
 def setUp(self):self.args=[load('data/'+n) for n in ['owner-specifications.json','spec-audit.json','hvac-review.json','scope-items.json','evidence.json','tender-response-template.json']]
 def test_valid(self):self.assertEqual(check_data(*self.args),[])
 def test_no_fixed(self):self.args[0]['is_fixed_purchase_specification']=True;self.assertTrue(check_data(*self.args))
 def test_no_count_guess(self):self.args[2]['recommended_indoor_count']=6;self.assertTrue(check_data(*self.args))
 def test_no_fake_auth(self):self.args[5]['identity_verified']=True;self.assertTrue(check_data(*self.args))
 def test_no_filled_price(self):self.args[5]['a_rows'][0]['amount']=1234;self.assertTrue(check_data(*self.args))
 def test_load_sum(self):self.args[0]['cooling_schedule'][0]['cooling_kw_reported']=4;self.assertTrue(check_data(*self.args))
 def test_audit_coverage(self):self.args[1]['items'].pop();self.assertTrue(check_data(*self.args))
 def test_no_build_approval(self):self.args[0]['specifications'][0]['construction_release']=True;self.assertTrue(check_data(*self.args))
if __name__=='__main__':unittest.main(verbosity=2)
