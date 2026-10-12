#!/usr/bin/env python3
"""R2 proposal/blank-template/package checks; not engineering or account-security certification."""
import argparse,copy,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(n):return json.loads((ROOT/n).read_text(encoding='utf-8'))
def check_data(j,audit,hvac,scope,evidence,reply):
 errors=[]
 def check(ok,msg):
  if not ok:errors.append(msg)
 specs=j['specifications'];ids={s['id'] for s in specs};scopes={s['id'] for s in scope['items']};ev={e['id'] for e in evidence['records']}
 check(len(specs)==37 and len(ids)==37,'expected 37 unique specs')
 check(j['package_id']=='JEJU-HOUSE-RFQ-20261013-R2','wrong revision')
 check(j['is_fixed_purchase_specification'] is False,'must be a proposal')
 check(j['as_built_or_permit_certification'] is False,'must not claim permit/design certification')
 check(j['actually_sent'] is False,'not a delivery receipt')
 check({x['id'] for x in audit['items']}==ids,'audit coverage mismatch')
 check(set(j['scope_spec_mapping'])==scopes,'61 scope mapping mismatch')
 for s in specs:
  check(s['status']=='comparison_proposal_not_purchase_fixed',s['id']+' wrong proposal state')
  check(s['alternatives_allowed'] is True and s['construction_release'] is False,s['id']+' alternatives/approval state wrong')
  check(bool(s['proposal_review']['r2_action']),s['id']+' missing review action')
  check(s['proposal_review']['house_specific_engineering_verified'] is False,s['id']+' not engineered')
  for x in s['drawing_evidence_refs']:check(x in ev,s['id']+' missing evidence '+x)
  for x in s['scope_ids']:check(x in scopes,s['id']+' missing scope '+x)
 for key,refs in j['scope_spec_mapping'].items():check(refs==[s['id'] for s in specs if key in s['scope_ids']],key+' mapping inconsistent')
 check(hvac['recommended_indoor_count'] is None and hvac['thermal_load_calculated'] is False,'needed AC quantity is unverified')
 check(len(hvac['label_records'])==11,'expected 11 distinct text records')
 check(len({x['id'] for x in hvac['label_records']})==11,'duplicated text records')
 indoors=[x for x in j['cooling_schedule'] if x['id'].startswith('IAC')]
 outdoors=[x for x in j['cooling_schedule'] if x['id'].startswith('OAC')]
 check(sum(x['common_pricing_quantity'] for x in indoors)==11,'A reference indoor count changed')
 check(abs(sum(x['common_pricing_quantity']*x['cooling_kw_reported'] for x in indoors)-60.9)<1e-8,'indoor arithmetic mismatch')
 check(abs(sum(x['common_pricing_quantity']*x['cooling_kw_reported'] for x in outdoors)-61.6)<1e-8,'outdoor arithmetic mismatch')
 for x in j['cooling_schedule']:check(x['locked_for_purchase'] is False and x['verified_installed_quantity'] is None,x['id']+' is not verified need')
 for x in j['material_allowances']:check(x['basis_type']=='owner_comparison_allowance_not_observed_market_price',x['id']+' is not researched market price')
 check(reply['schema_version']=='2.0' and reply['package_id']==j['package_id'],'reply schema/revision mismatch')
 check(reply['status']=='local_draft_not_submitted' and reply['identity_verified'] is False,'must not imply submission/authentication')
 check(len(reply['a_rows'])==61 and {x['item_id'] for x in reply['a_rows']}==scopes,'reply scope mismatch')
 for r in reply['a_rows']:
  check(r['status']=='unpriced',r['item_id']+' public template must be blank')
  check(all(r[k] is None for k in ['qty','unit_price','amount']),r['item_id']+' public price data')
  check(r['spec_refs']==j['scope_spec_mapping'][r['item_id']],r['item_id']+' spec mismatch')
 check(not reply['b_proposals'] and not reply['comments'],'public response not blank')
 return errors

def validate():
 j=load('data/owner-specifications.json');reply=load('data/tender-response-template.json')
 errors=check_data(j,load('data/spec-audit.json'),load('data/hvac-review.json'),load('data/scope-items.json'),load('data/evidence.json'),reply)
 if load('contractor/specifications.json')!=j:errors.append('stale contractor spec')
 if load('contractor/quote-return.json')!=reply:errors.append('stale contractor reply template')
 if (ROOT/'TENDER.md').read_bytes()!=(ROOT/'contractor/SPECIFICATIONS.md').read_bytes():errors.append('stale contractor Markdown')
 expected={'README.md','SPECIFICATIONS.md','index.html','style.css','specifications.json','quote-return.json','DRAWING-MANIFEST.json','reply.html','reply.js','reply.css'}
 if {x.name for x in (ROOT/'contractor').iterdir() if x.is_file()}!=expected:errors.append('unexpected contractor files')
 with zipfile.ZipFile(ROOT/'jeju-house-contractor-R2.zip') as z:
  if z.testzip() is not None:errors.append('corrupt archive')
  if set(z.namelist())!={'jeju-house-R2/'+n for n in expected}:errors.append('archive file list differs')
  for n in expected:
   if z.read('jeju-house-R2/'+n)!=(ROOT/'contractor'/n).read_bytes():errors.append('archive stale '+n)
 body=(ROOT/'contractor/reply.html').read_text()
 if '로컬 초안' not in body or '실제 제출 기능 없음' not in body:errors.append('missing local-only notice')
 return {'passed':not errors,'package_id':j['package_id'],'checks':{'spec_audit_rows':37,'A_reference_indoor_count':11,'verified_needed_indoor_count':None,'response_rows':61,'contractor_files':10,'authenticated_submission_service':False},'errors':errors,'scope':'reference/proposal integrity and local draft packaging; not field engineering or live access-control validation'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path);a=p.parse_args()
 try:r=validate()
 except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:r={'passed':False,'errors':[str(e)]}
 if a.receipt:a.receipt.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['passed'] else 1
if __name__=='__main__':sys.exit(main())
