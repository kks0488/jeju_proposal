#!/usr/bin/env python3
"""Mutation tests for R1 cross-reference checks; never real vendor bids."""
import copy
import unittest
from validate_tender import load,check_data
class TenderTests(unittest.TestCase):
 def setUp(self):
  self.args=[load('data/'+n) for n in ['owner-specifications.json','research-sources.json','scope-items.json','evidence.json','tender-response-template.json']]
 def errors(self):return check_data(*self.args)
 def test_valid(self):self.assertEqual(self.errors(),[])
 def test_missing_spec(self):self.args[0]['specifications'][0]['included_work']='';self.assertTrue(self.errors())
 def test_broken_source(self):self.args[0]['specifications'][0]['research_refs']=['MISSING'];self.assertTrue(self.errors())
 def test_wrong_model_count(self):self.args[0]['cooling_schedule'][0]['common_pricing_quantity']=1;self.assertTrue(self.errors())
 def test_private_prices(self):self.args[4]['items'][0]['total_ex_vat']=10;self.assertTrue(self.errors())
 def test_changed_allowance(self):self.args[4]['allowance_return'][0]['fixed_material_allowance_ex_vat']=1;self.assertTrue(self.errors())
 def test_not_a_market_price(self):self.args[0]['material_allowances'][0]['basis_type']='observed_market_price';self.assertTrue(self.errors())
 def test_not_a_permit(self):self.args[0]['as_built_or_permit_certification']=True;self.assertTrue(self.errors())
 def test_not_a_takeoff(self):self.args[0]['cooling_schedule'][0]['verified_installed_quantity']=2;self.assertTrue(self.errors())
 def test_scope_mapping(self):self.args[0]['scope_spec_mapping']['GEN-01']=[];self.assertTrue(self.errors())
if __name__=='__main__':unittest.main(verbosity=2)
