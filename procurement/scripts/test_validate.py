#!/usr/bin/env python3
"""Synthetic tests only; values are not actual bids or project estimates."""
import copy
import unittest
from validate import ROOT,load,validate_bid,BUCKETS

class BidTests(unittest.TestCase):
 def make(self):
  b=load(ROOT/'data/bid-template.json');b['items']=b['items'][:1];b['status']='submitted'
  b['bidder']['legal_entity']='SYNTHETIC_TEST_ONLY';b['basis'].update(drawing_issue_id='TEST',quantity_mode='bidder_takeoff',offer_date='2000-01-01',valid_until='2000-01-02',duration_days=1)
  i=b['items'][0];i.update(quote_status='fixed_measured',cost_bucket='direct',quantity=2,quantity_basis='synthetic test',material_unit_price=20,labor_unit_price=20,equipment_unit_price=10,combined_unit_price=50,amount_ex_vat=100)
  for field in BUCKETS.values():b['summary'][field]=0
  b['summary'].update(direct_cost_ex_vat=100,base_total_ex_vat=100,vat_amount=0,base_total_inc_vat=100)
  return b
 def test_blank_template(self):self.assertFalse(validate_bid(load(ROOT/'data/bid-template.json'))[0])
 def test_valid_synthetic(self):self.assertFalse(validate_bid(self.make())[0])
 def test_null_is_not_zero(self):
  b=load(ROOT/'data/bid-template.json');b['items'][0]['amount_ex_vat']=0;self.assertTrue(validate_bid(b)[0])
 def test_measurement_math(self):
  b=self.make();b['items'][0]['amount_ex_vat']=110;self.assertTrue(validate_bid(b)[0])
 def test_components(self):
  b=self.make();b['items'][0]['material_unit_price']=100;self.assertTrue(validate_bid(b)[0])
 def test_total(self):
  b=self.make();b['summary']['base_total_ex_vat']=110;self.assertTrue(validate_bid(b)[0])
 def test_duplicate(self):
  b=self.make();b['items']+=copy.deepcopy(b['items']);self.assertTrue(validate_bid(b)[0])
 def test_included_cycle(self):
  b=self.make();a=b['items'][0];c=copy.deepcopy(a);c['item_id']='GEN-02';a.update(quote_status='included_elsewhere',included_in_item_id='GEN-02',amount_ex_vat=0);c.update(quote_status='included_elsewhere',included_in_item_id='GEN-01',amount_ex_vat=0);b['items'].append(c);self.assertTrue(any('cycle' in x for x in validate_bid(b)[0]))
 def test_unapproved_provisional(self):
  b=self.make();b['items'][0]['quote_status']='provisional_sum';self.assertTrue(any('addendum' in x for x in validate_bid(b)[0]))
 def test_no_unsupported_normalization(self):
  b=self.make();b['comparison']['status']='comparable_after_normalization';self.assertTrue(validate_bid(b)[0])
 def test_missing_scope(self):self.assertTrue(validate_bid(self.make(),{'GEN-01','GEN-02'})[0])
 def test_submitted_unpriced(self):
  b=self.make();b['items'][0].update(quote_status='not_priced',amount_ex_vat=None);self.assertTrue(validate_bid(b)[0])
 def test_nonfinite(self):
  b=self.make();b['items'][0]['amount_ex_vat']=float('nan');self.assertTrue(validate_bid(b)[0])
 def test_negative_tax(self):
  b=self.make();b['summary'].update(vat_amount=-10,base_total_inc_vat=90);self.assertTrue(validate_bid(b)[0])
if __name__=='__main__':unittest.main(verbosity=2)
