#!/usr/bin/env python3
"""Read-only DXF text/inventory helper. NOT a drawing interpreter or takeoff engine.
Writes private output only under the repository's gitignored .local directory.
DWG conversion is separate; preserve original and conversion logs. Python 3.9+.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import ezdxf

ROOT=Path(__file__).resolve().parents[2]

def extract(path,source_id):
 doc=ezdxf.readfile(str(path));records=[];errors=[]
 def record(e,container,parent=None):
  typ=e.dxftype()
  if typ not in ('TEXT','MTEXT','ATTRIB','ATTDEF'):return
  try:
   pos=e.dxf.get('insert',(0,0,0))
   records.append({'source_id':source_id,'handle':e.dxf.handle,'type':typ,'container':container,'parent_insert':parent,'layer':e.dxf.layer,'xy':[float(pos[0]),float(pos[1])],'height':e.dxf.get('char_height') if typ=='MTEXT' else e.dxf.get('height'),'text':e.plain_text() if hasattr(e,'plain_text') else e.dxf.get('text',''),'status':'private_unreviewed_text'})
  except (ezdxf.DXFError,AttributeError,ValueError) as exc:errors.append({'handle':e.dxf.handle,'error':type(exc).__name__})
 for block in doc.blocks:
  for e in block:
   record(e,block.name)
   if e.dxftype()=='INSERT':
    for attr in e.attribs:record(attr,block.name,e.dxf.handle)
 xrefs=[{'name':b.name,'flags':b.block.dxf.flags,'path':b.block.dxf.get('xref_path','')} for b in doc.blocks if b.block.dxf.flags & 12]
 sha=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):sha.update(chunk)
 return {'schema_version':'1.0','source_id':source_id,'input_dxf_sha256':sha.hexdigest(),'classification':'PRIVATE_UNREVIEWED_DO_NOT_PUBLISH','header':{k:str(doc.header.get(k,'')) for k in ['$ACADVER','$DWGCODEPAGE','$INSUNITS','$MEASUREMENT','$EXTMIN','$EXTMAX']},'model_entity_count':len(doc.modelspace()),'model_entity_types':dict(Counter(e.dxftype() for e in doc.modelspace())),'layouts':[{'name':l.name,'entity_count':len(l)} for l in doc.layouts],'block_definition_count':len(doc.blocks),'xref_records':xrefs,'texts':records,'extraction_errors':errors,'limits':['Block definitions are not transformed INSERT instances or physical item quantities.','Nested/dynamic/proxy/MLeader/DIMENSION display and xref dependencies are not resolved by this helper.','No rendered PDF/CAD comparison, sheet delimiting, scale calibration, geometry takeoff or engineering validation.']}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',type=Path,required=True);ap.add_argument('--source-id',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 src=a.input.resolve();dst=a.output.resolve();private=(ROOT/'.local').resolve()
 if src.suffix.lower()!='.dxf' or not src.is_file():ap.error('--input must be an existing DXF')
 if private not in dst.parents:ap.error('--output must be under repository .local/ (private, gitignored)')
 if src==dst or dst.exists():ap.error('Refusing to overwrite input/existing output; choose a new revision filename')
 try:
  data=extract(src,a.source_id);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps({'written_to_private_directory':True,'text_records':len(data['texts']),'extraction_errors':len(data['extraction_errors']),'quantity_takeoff':False}))
 except (OSError,ezdxf.DXFError) as e:print(type(e).__name__+': '+str(e),file=sys.stderr);return 1
 return 0
if __name__=='__main__':sys.exit(main())
