"""Exporta la revisión escrita junto a las evidencias originales, sin recodificar."""
from pathlib import Path
import json
import re
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
report_path=ROOT/'docs/auditoria-codificaciones-21419-21538.md'
report=report_path.read_text()
sessions={}
for law in ('21419','21538'):
    path=next(p for p in (ROOT/'output/validation').glob('validation_20260903*.json') if json.loads(p.read_text()).get('law_number')==law)
    sessions[law]=(path,json.loads(path.read_text()))
pattern=re.compile(r'^### (21419|21538)-(\d{2}) · ([^\n]+)\n\n(.*?)(?=^### (?:21419|21538)-|^## |\Z)', re.M|re.S)
matches=list(pattern.finditer(report))
assert len(matches)==40
rows=[];anns=[]
for match in matches:
    law,number,title,body=match.groups()
    path,session=sessions[law]
    item=session['items'][int(number)-1]
    body=re.sub(r'^Unidad `[^\n]+\n\n','',body).strip()
    rows.append(dict(law=law,sample_number=int(number),unit_id=item['unit_id'],session_file=str(path.relative_to(ROOT)),assessment=title,review=body,n_words=item['n_words'],original_decision=item['decision'],original_comment=item['general_comment'],quality_flags='|'.join(item['quality_flags']),target_text=item['target_text'],annotations_json=json.dumps(item['annotations'],ensure_ascii=False),previous_context_json=json.dumps(item.get('previous_context'),ensure_ascii=False),next_context_json=json.dumps(item.get('next_context'),ensure_ascii=False)))
    reviews=re.findall(r'^\d+\. (.+)$',body,re.M)
    if len(item['annotations'])>1: assert len(reviews)==len(item['annotations'])
    for i,ann in enumerate(item['annotations']):
        span=ann['span']
        assert item['target_text'][span['start_char']:span['end_char']]==span['text']
        anns.append(dict(law=law,sample_number=int(number),annotation_number=i+1,unit_id=item['unit_id'],annotation_id=ann['annotation_id'],concept_id=ann['concept_id'],stance=ann['stance'],span=span['text'],start_char=span['start_char'],end_char=span['end_char'],review=reviews[i] if reviews else body))
assert len(anns)==16
for filename,data in [('revision_40_unidades',rows),('revision_16_anotaciones',anns)]:
    df=pd.DataFrame(data);df.to_csv(OUT/f'{filename}.csv',index=False);df.to_parquet(OUT/f'{filename}.parquet',index=False)
# Añadir las claves de localización al propio informe, de manera idempotente.
for match in reversed(matches):
    law,number,title,body=match.groups()
    item=sessions[law][1]['items'][int(number)-1]
    if body.startswith('Unidad `'): continue
    codes='; '.join(f"`{a['concept_id']}/{a['stance']}`" for a in item['annotations']) or '`no_statements`'
    metadata=f"Unidad `{item['unit_id']}` · {item['n_words']} palabras · Registro: {codes}.\n\n"
    report=report[:match.start(4)]+metadata+report[match.start(4):]
report_path.write_text(report)
print(f'{len(rows)} unidades; {len(anns)} anotaciones; evidencias y ubicaciones verificadas.')
