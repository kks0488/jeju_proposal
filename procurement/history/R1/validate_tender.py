#!/usr/bin/env python3
"""Validate R1 owner specification provenance and contractor share pack.
No external requests, vendor pricing, CAD interpretation or design approvals.
"""
import argparse
import json
from pathlib import Path
import sys
import zipfile
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]

def load(n):return json.loads((ROOT/n).read_text(encoding='utf-8'))

def check_data(j,sources,scope,evidence,response):
 errors=[]
 def check(ok,message):
  if not ok:errors.append(message)
 specs=j['specifications'];ids={s['id'] for s in specs};rs={s['id'] for s in sources['sources']};sid={s['id'] for s in scope['items']};ev={e['id'] for e in evidence['records']}
 check(len(ids)==len(specs),'duplicate spec ID')
 check(len(rs)==len(sources['sources']),'duplicate research ID')
 check(j['use_basis']=='상시 거주 주택','residential pricing basis missing')
 check(j['as_built_or_permit_certification'] is False,'must not claim permit/design certification')
 check(j['actually_sent'] is False,'package is not a delivery receipt')
 check(bool(j.get('administrative_note')),'original administrative records must be distinguished')
 check(j['market_price_research_performed'] is False,'allowances must not be represented as researched vendor prices')
 for s in specs:
  for k in ('pricing_basis','included_work','shop_drawing_and_acceptance','selection_reason'):
   check(bool(s.get(k)),s['id']+' missing '+k)
  check(s.get('construction_release') is False,s['id']+' is not a construction release')
  check(s['status']=='specified_for_comparative_quotation',s['id']+' missing pricing status')
  for r in s['research_refs']:check(r in rs,s['id']+' missing research '+r)
  for r in s['drawing_evidence_refs']:check(r in ev,s['id']+' missing CAD evidence '+r)
  for r in s['scope_ids']:check(r in sid,s['id']+' unknown scope '+r)
 mapping=j['scope_spec_mapping']
 check(set(mapping)==sid,'scope-spec mapping must cover all scope IDs')
 for k,refs in mapping.items():
  expected=[s['id'] for s in specs if k in s['scope_ids']]
  check(bool(refs) and refs==expected,k+' wrong spec mapping')
 allowed_hosts={'www.eagonwd.com','www.lxzin.com','www.mapei.com','www.himpel.co.kr','www.lge.co.kr','www.daelimbath.com','webzine.kccworld.co.kr','www.blum.com','uk.prefa.com','krb.co.kr'}
 for r in sources['sources']:
  u=urlsplit(r['url']);check(u.scheme=='https' and u.netloc in allowed_hosts,r['id']+' not an expected primary source')
  check(r['market_price_verified'] is False,r['id']+' must distinguish product facts from prices')
 al=j['material_allowances'];aids={a['id'] for a in al}
 check(len(aids)==len(al),'duplicate allowance ID')
 for a in al:
  check(a['basis_type']=='owner_comparison_allowance_not_observed_market_price',a['id']+' inaccurate price basis')
  check(isinstance(a['material_allowance_ex_vat_krw'],int) and a['material_allowance_ex_vat_krw']>0,a['id']+' invalid material allowance')
  check(a['spec_id'] in ids and a['scope_id'] in sid,a['id']+' broken reference')
  check(a['material_waste_factor']==(1.10 if a['unit']=='m2' else 1.0),a['id']+' unexpected waste factor')
 opts=j['options'];oids={o['id'] for o in opts}
 check(len(oids)==len(opts),'duplicate alternate ID')
 for o in opts:
  check(o['selected_into_base'] is False and o['price_delta_ex_vat'] is None,o['id']+' not an empty optional quote')
  for ref in o['spec_refs']:check(ref in ids,o['id']+' missing spec '+ref)
 for s in specs:
  for r in s['alternative_refs']:check(r in oids,s['id']+' unknown alternate '+r)
 cool=j['cooling_schedule']
 check(sum(c['common_pricing_quantity'] for c in cool if c['id'].startswith('IAC'))==11,'indoor pricing total must remain 11')
 check(sum(c['common_pricing_quantity'] for c in cool if c['id'].startswith('OAC'))==2,'outdoor pricing total must remain 2')
 check(all(c['verified_installed_quantity'] is None for c in cool),'pricing quantities are not verified installed quantities')
 byid={s['id']:s for s in specs}
 check('50S' in byid['SP-20']['pricing_basis'] and '겸용' in byid['SP-20']['pricing_basis'],'boiler must retain combined heating/DHW selection')
 check('7×165×1200' in byid['SP-11']['pricing_basis'] and 'T10' in byid['SP-11']['included_work'],'floor thickness change must be explicit')
 check('바이패스' in byid['SP-24']['pricing_basis'] and 'H13' in byid['SP-24']['pricing_basis'],'ventilation filter/bypass scope missing')
 check(response['package_id']==j['package_id'],'response has wrong package revision')
 check(response['status']=='blank_contractor_return','public response must be blank')
 check({i['item_id'] for i in response['items']}==sid,'response missing scope IDs')
 for i in response['items']:
  check(i['owner_spec_refs']==mapping.get(i['item_id']),i['item_id']+' response spec mismatch')
  for k in ['quantity','material_cost_ex_vat','labor_cost_ex_vat','equipment_cost_ex_vat','total_ex_vat']:
   check(i.get(k) is None,i['item_id']+' public template contains filled '+k)
  check(i.get('quote_status')=='not_priced',i['item_id']+' public response priced')
 returned={a['allowance_id']:a for a in response['allowance_return']}
 check(set(returned)==aids,'response allowance IDs mismatch')
 for a in al:
  ra=returned.get(a['id'],{})
  check(ra.get('fixed_material_allowance_ex_vat')==a['material_allowance_ex_vat_krw'],a['id']+' response price basis mismatch')
  check(ra.get('quantity')==a['common_pricing_quantity'],a['id']+' response pricing quantity mismatch')
  check(ra.get('already_included_in_base') is True,a['id']+' must not double count allowance')
 return errors

def validate():
 j=load('data/owner-specifications.json');rs=load('data/research-sources.json');scope=load('data/scope-items.json');ev=load('data/evidence.json');response=load('data/tender-response-template.json')
 errors=check_data(j,rs,scope,ev,response)
 def check(ok,msg):
  if not ok:errors.append(msg)
 check(load('contractor/specifications.json')==j,'contractor spec JSON differs from canonical')
 check(load('contractor/quote-return.json')==response,'contractor response differs from canonical')
 check((ROOT/'TENDER.md').read_bytes()==(ROOT/'contractor/SPECIFICATIONS.md').read_bytes(),'contractor Markdown differs from canonical document')
 manifest=load('contractor/DRAWING-MANIFEST.json');original=load('data/source-manifest.json')
 check([(s['source_id'],s['sha256']) for s in manifest['files']]==[(s['source_id'],s['sha256']) for s in original['sources']],'contractor drawing hashes differ')
 expected={'README.md','SPECIFICATIONS.md','index.html','style.css','specifications.json','quote-return.json','DRAWING-MANIFEST.json'}
 actual={p.name for p in (ROOT/'contractor').iterdir() if p.is_file()}
 check(actual==expected,'unexpected file in contractor share directory')
 with zipfile.ZipFile(ROOT/'jeju-house-contractor-R1.zip') as z:
  check(z.testzip() is None,'corrupt zip member')
  check(set(z.namelist())=={'jeju-house-R1/'+n for n in expected},'unexpected zip content')
  for n in expected:check(z.read('jeju-house-R1/'+n)==(ROOT/'contractor'/n).read_bytes(),'stale zip file '+n)
 body=(ROOT/'contractor/index.html').read_text(encoding='utf-8')
 check('RANKING.md' not in body and 'DUE-DILIGENCE.md' not in body and 'RFI.html' not in body,'contractor pack leaks internal review navigation')
 for s in j['specifications']:check('id="'+s['id'].lower()+'"' in body,'missing standalone spec anchor '+s['id'])
 check('전부 미정' not in body,'standalone spec reverted to unspecified')
 return {'passed':not errors,'package_id':j['package_id'],'checks':{'specifications':len(j['specifications']),'manufacturer_sources':len(rs['sources']),'common_material_allowances':len(j['material_allowances']),'separate_alternates':len(j['options']),'scope_ids':len(scope['items']),'contractor_files':len(expected),'raw_CAD_in_bundle':False},'errors':errors,'scope':'R1 data/reference/allowance consistency and curated ZIP equality only; not engineering, market-price or permit certification'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--receipt',type=Path);a=ap.parse_args()
 try:result=validate()
 except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:result={'passed':False,'errors':[str(e)]}
 if a.receipt:
  a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['passed'] else 1
if __name__=='__main__':sys.exit(main())
