#!/usr/bin/env python3
"""Offline public-package and basic private-bid validation (Python 3.9+).
Not a quantity survey, CAD verification, legal review or complete JSON Schema engine.
Private bid input is never copied to the repository or reported with its prices.
"""
import argparse
import collections
from decimal import Decimal
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'not_priced','fixed_measured','fixed_lump_sum','included_elsewhere','excluded','optional','provisional_sum','not_applicable'}
BUCKETS={'direct':'direct_cost_ex_vat','general':'general_cost_ex_vat','statutory':'statutory_cost_ex_vat','overhead':'overhead_ex_vat','profit':'profit_ex_vat','provisional':'provisional_sum_ex_vat'}

def load(path):
 return json.loads(Path(path).read_text(encoding='utf-8'),parse_constant=lambda v: (_ for _ in ()).throw(ValueError('Non-finite JSON number')))

def numeric(value):
 return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def close(a,b):
 return abs(Decimal(str(a))-Decimal(str(b))) <= Decimal('1')

def validate_bid(bid,scope_ids=None):
 errors=[]; warnings=[]
 for key in ['schema_version','package_id','status','bidder','basis','items','summary','comparison']:
  if key not in bid:errors.append('missing top-level '+key)
 if errors:return errors,warnings
 if bid['schema_version']!='1.0':errors.append('unsupported schema_version')
 submitted=bid['status'] in ('submitted','reviewed')
 if bid['status'] not in ('template_not_submitted','draft','submitted','reviewed'):errors.append('invalid bid status')
 for key in ('bidder','basis','summary','comparison'):
  if not isinstance(bid[key],dict):errors.append(key+' must be an object')
 if not isinstance(bid['items'],list):errors.append('items must be array')
 if errors:return errors,warnings
 if not bid['items']:errors.append('items must not be empty')
 if bid['basis'].get('currency')!='KRW':errors.append('currency must be KRW')
 if bid['basis'].get('quantity_mode') not in (None,'owner_common_quantities','bidder_takeoff'):errors.append('invalid quantity_mode')
 if submitted:
  for k in ['drawing_issue_id','quantity_mode','offer_date','valid_until','duration_days']:
   if bid['basis'].get(k) is None:errors.append('submitted bid missing basis.'+k)
  if not bid['bidder'].get('legal_entity'):errors.append('submitted bid missing legal_entity')
 ids=[i.get('item_id') for i in bid['items'] if isinstance(i,dict)]
 if len(ids)!=len(bid['items']):return ['all bid rows must be objects'],warnings
 if len(set(ids))!=len(ids):errors.append('duplicate item_id')
 rows={i.get('item_id'):i for i in bid['items']}
 if scope_ids is not None:
  missing=set(scope_ids)-set(ids)
  if missing:errors.append('missing required scope rows: '+','.join(sorted(missing)))
  extra=set(ids)-set(scope_ids)
  if extra:warnings.append('extra/detail rows require scope review: '+','.join(sorted(str(x) for x in extra)))
 totals={b:Decimal('0') for b in BUCKETS}
 unresolved=False
 for item in bid['items']:
  ident=item.get('item_id','?'); st=item.get('quote_status'); prefix=str(ident)+': '
  if not isinstance(ident,str) or not re.fullmatch(r'[A-Z]+-\d{2}(?:-\d{2})?',ident):errors.append(prefix+'invalid item id')
  if st not in ALLOWED:errors.append(prefix+'invalid quote_status');continue
  if item.get('cost_bucket') not in set(BUCKETS)-{'provisional'}:errors.append(prefix+'invalid cost_bucket')
  for field in ['quantity','material_unit_price','labor_unit_price','equipment_unit_price','combined_unit_price','amount_ex_vat']:
   if field not in item:errors.append(prefix+'missing '+field);continue
   v=item[field]
   if v is not None and (not numeric(v) or v<0):errors.append(prefix+field+' must be finite nonnegative number or null')
  amount=item.get('amount_ex_vat');qty=item.get('quantity');unit=item.get('combined_unit_price')
  if st=='not_priced':
   unresolved=True
   if amount is not None:errors.append(prefix+'unpriced is null, not zero/amount')
   if submitted:errors.append(prefix+'submitted row remains unpriced')
  if st=='fixed_measured':
   if not all(numeric(x) for x in (qty,unit,amount)):errors.append(prefix+'measured row requires quantity, combined price, amount')
   elif not close(Decimal(str(qty))*Decimal(str(unit)),amount):errors.append(prefix+'quantity x combined price mismatch')
  if st in ('fixed_measured','fixed_lump_sum','provisional_sum'):
   if not numeric(amount):errors.append(prefix+'priced row missing numeric amount')
   else:totals['provisional' if st=='provisional_sum' else item.get('cost_bucket','direct')]+=Decimal(str(amount))
   if submitted and not item.get('quantity_basis'):errors.append(prefix+'missing scope/quantity basis')
  parts=[item.get(k) for k in ('material_unit_price','labor_unit_price','equipment_unit_price')]
  if all(numeric(x) for x in parts) and numeric(unit):
   if not close(sum(Decimal(str(x)) for x in parts),unit):errors.append(prefix+'component unit prices mismatch')
  if st=='included_elsewhere':
   target=item.get('included_in_item_id')
   if target not in rows or target==ident:errors.append(prefix+'invalid included-in target')
   if amount not in (None,0):errors.append(prefix+'included row would be double-counted')
   if submitted and target in rows and rows[target].get('quote_status') in ('not_priced','excluded','optional','not_applicable'):errors.append(prefix+'included-in target is not a base-priced item')
   seen={ident};cur=target
   while cur in rows and rows[cur].get('quote_status')=='included_elsewhere':
    if cur in seen:errors.append(prefix+'included-in cycle');break
    seen.add(cur);cur=rows[cur].get('included_in_item_id')
  if st in ('excluded','not_applicable'):
   if amount not in (None,0):errors.append(prefix+'excluded/not-applicable amount must be null/zero')
   if submitted and not item.get('exclusion_reason'):errors.append(prefix+'missing exclusion/not-applicable reason')
  if st=='optional' and submitted and not numeric(amount):errors.append(prefix+'option amount missing')
  if submitted and st in ('excluded','provisional_sum'):warnings.append(prefix+'requires approval/normalization before comparison')
 # PS amounts belong in rows, array stores supporting approvals only: avoid duplicate totals.
 ps=[i for i in bid['items'] if i.get('quote_status')=='provisional_sum']
 psmeta=bid.get('provisional_sums',[])
 if not isinstance(psmeta,list):errors.append('provisional_sums must be array')
 elif submitted:
  approved={p.get('item_id') for p in psmeta if isinstance(p,dict) and p.get('approved_addendum_id')}
  for i in ps:
   if i['item_id'] not in approved:errors.append(i['item_id']+': provisional sum lacks common approved addendum')
 summary=bid['summary'];total=sum(totals.values())
 for field,value in summary.items():
  if field!='alternates_excluded_from_base' and value is not None and (not numeric(value) or value<0):errors.append('summary '+field+' must be nonnegative number or null')
 for bucket,field in BUCKETS.items():
  v=summary.get(field)
  if submitted and not numeric(v):errors.append('missing numeric summary.'+field)
  elif numeric(v) and not unresolved and not close(v,totals[bucket]):errors.append('summary category mismatch: '+field)
 v=summary.get('base_total_ex_vat')
 if submitted and not numeric(v):errors.append('missing base_total_ex_vat')
 elif numeric(v) and not unresolved and not close(v,total):errors.append('base total mismatch')
 tax=summary.get('vat_amount');inc=summary.get('base_total_inc_vat')
 if submitted and (not numeric(tax) or not numeric(inc)):errors.append('submitted tax/inc-vat summary missing')
 if all(numeric(x) for x in (v,tax,inc)) and not close(Decimal(str(v))+Decimal(str(tax)),inc):errors.append('inc-vat total mismatch')
 if summary.get('alternates_excluded_from_base') is not True:errors.append('alternates must be separate from base')
 if bid['comparison'].get('status')=='comparable_after_normalization':
  c=bid['comparison'];adjust=c.get('normalization_adjustments',[])
  if unresolved or c.get('unresolved_scope_items'):errors.append('cannot claim comparable with unresolved scope')
  if not c.get('reviewed_by'):errors.append('normalization requires reviewer')
  valid=isinstance(adjust,list) and all(isinstance(a,dict) and numeric(a.get('amount_ex_vat')) and a.get('basis') and a.get('approved_by') for a in adjust)
  if not valid:errors.append('normalization adjustment requires signed amount, basis and approval')
  elif numeric(v) and numeric(c.get('normalized_base_ex_vat')):
   if not close(Decimal(str(v))+sum(Decimal(str(a['amount_ex_vat'])) for a in adjust),c['normalized_base_ex_vat']):errors.append('normalized total mismatch')
  else:errors.append('normalization total missing')
 return errors,warnings

class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.links=[];self.ids=[];self.h1=0;self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag in ('a','link') and a.get('href'):self.links.append(a['href'])

def validate_package():
 errors=[];data={p.name:load(p) for p in (ROOT/'data').glob('*.json')}
 ev=data['evidence.json']['records'];ev_ids={e['id'] for e in ev};sources={s['source_id'] for s in data['source-manifest.json']['sources']}
 if len(ev_ids)!=len(ev):errors.append('duplicate evidence id')
 for e in ev:
  if e['source_id'] not in sources or e['id']!=e['source_id']+':'+e['handle']:errors.append('invalid evidence provenance '+e['id'])
  if e['visual_verified'] or e['approved']:errors.append('R0 must not claim evidence approval '+e['id'])
  if '외부유출시' in e['text'] or e['handle'] in {'EADFA','EADFE','EAE05'}:errors.append('private work-note content in public evidence')
 for name,key in [('drawings.json','drawings'),('equipment.json','items'),('rfi.json','items'),('requirements.json','items'),('scope-items.json','items')]:
  rows=data[name][key];ids=[r['id'] for r in rows]
  if len(ids)!=len(set(ids)):errors.append('duplicate id '+name)
  for r in rows:
   for ref in r.get('evidence_refs',[]):
    if ref not in ev_ids:errors.append(name+' missing evidence '+ref)
 rfis={r['id'] for r in data['rfi.json']['items']}
 for req in data['requirements.json']['items']:
  for r in req['rfi_refs']:
   if r not in rfis:errors.append('requirement references unknown RFI '+r)
 for r in data['rfi.json']['items']:
  if r['status']=='closed' and not all(r.get(f) for f in ['answer','answered_by','answer_date','approved_by','closed_at']):errors.append('closed RFI missing approvals '+r['id'])
 for i in data['equipment.json']['items']:
  if i['verified_quantity'] is not None or i['approved_for_order']:errors.append('R0 schedule quantity incorrectly promoted')
 for i in data['scope-items.json']['items']:
  if i['owner_quantity'] is not None or i['common_spec_approval']:errors.append('R0 scope not approved')
 scope={i['id'] for i in data['scope-items.json']['items']}
 be,bw=validate_bid(data['bid-template.json'],scope);errors+=be
 if data['bid-template.json']['status']!='template_not_submitted':errors.append('public bid is not empty template')
 for i in data['bid-template.json']['items']:
  if i['quote_status']!='not_priced' or i['amount_ex_vat'] is not None:errors.append('public bid contains prices')
 parsed={p.resolve():Page(p.read_text(encoding='utf-8')) for p in ROOT.glob('*.html')};links=0
 for p,page in parsed.items():
  if page.h1!=1:errors.append(p.name+' must have one h1')
  if len(page.ids)!=len(set(page.ids)):errors.append(p.name+' duplicate HTML ids')
  for url in page.links:
   u=urlsplit(url)
   if u.scheme or u.netloc:continue
   target=(p.parent/unquote(u.path)).resolve() if u.path else p
   if target.is_dir():target=target/'index.html'
   links+=1
   if not target.exists():errors.append(p.name+' missing link '+url);continue
   if u.fragment and target in parsed and unquote(u.fragment) not in parsed[target].ids:errors.append(p.name+' missing anchor '+url)
 for p in ROOT.rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.dwg','.dxf','.pdf','.xlsx'):errors.append('unreviewed source/binary in public package '+p.name)
 counts={'drawing_id_candidates':len(data['drawings.json']['drawings']),'rfi':len(rfis),'rfi_p0':sum(i['priority']=='P0' for i in data['rfi.json']['items']),'scope_rows':len(scope),'equipment_rows':len(data['equipment.json']['items']),'evidence_records':len(ev),'html_pages':len(parsed),'local_links_checked':links}
 return errors,counts

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--bid',type=Path,help='Private bid input; only validation diagnostics printed');ap.add_argument('--receipt',type=Path,help='Public package QA summary, never a private bid output');a=ap.parse_args()
 try:
  if a.bid:
   if a.receipt:ap.error('--receipt is not permitted with private --bid')
   errors,warnings=validate_bid(load(a.bid),{i['id'] for i in load(ROOT/'data/scope-items.json')['items']});result={'passed':not errors,'errors':errors,'warnings':warnings,'scope':'basic bid structure/arithmetic, not professional approval'}
  else:
   errors,counts=validate_package();result={'passed':not errors,'checks':counts,'errors':errors,'cad_visual_check':False,'verified_quantity_takeoff':False,'scope':'public JSON cross-references, draft guardrails, empty bid semantics and static HTML links'}
   if a.receipt:
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps(result,ensure_ascii=False,indent=2));return 1 if errors else 0
 except (ValueError,KeyError,OSError,TypeError) as e:
  print(json.dumps({'passed':False,'error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':sys.exit(main())
