"""Auditoría local del piloto y regeneración de bloques, sin red ni descargas.

Ejecutar desde la raíz con `uv run --offline --no-sync python <este archivo>`.
Lee la versión archivada 1.0.0 cuando existe; produce las nuevas tablas en una
carpeta temporal. No escribe sesiones originales ni el corpus activo.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys
from tempfile import TemporaryDirectory

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from features.coding_chunks import WORD_RE, count_words, paragraph_blocks, paragraph_fragments, segment_token, length_bin, text_sha256
from features.manual_validation.service import load_corpus_records, ValidationService

OUT = Path(__file__).resolve().parent
temporary = TemporaryDirectory(prefix='coding-audit-')
NEW_ROOT = Path(temporary.name)
SESSIONS = {
    '21419': 'validation_20260903T201432999213Z_1e8a5130.json',
    '21538': 'validation_20260903T203413684795Z_a63b3b9d.json',
}
metrics = {}; inputs = []; short_rows = []; samples = []; omitted = []; mapping = []; comparison = []
cells = re.findall(r'```\{python\}\n(.*?)\n```', (ROOT/'proc.qmd').read_text(), re.S)
start = next(i for i,c in enumerate(cells) if 'MINIMUM_WORDS = ' in c)
for law,bill in [('21419','14588-13'),('21538','15625-13'),('21735','15480-13')]:
    folder = ROOT/'data/proc_data'/f'ley_{law}'
    oldpath = folder/'coding_chunks_long.coding-chunks-1.0.0.parquet'
    if not oldpath.exists(): oldpath = folder/'coding_chunks_long.parquet'
    old = pd.read_parquet(oldpath)
    assert old.chunk_schema_version.eq('coding-chunks-1.0.0').all()
    speech = pd.read_parquet(folder/'speech_df.parquet')
    indexed = speech.set_index('utterance_id')
    target = NEW_ROOT/f'ley_{law}'; target.mkdir(parents=True,exist_ok=True)
    env = dict(pd=pd,LAW_NUMBER=law,BILL_NUMBER=bill,PROC_DATA_DIR=target,speech_df=speech,paragraph_blocks=paragraph_blocks,paragraph_fragments=paragraph_fragments,segment_token=segment_token,length_bin=length_bin)
    for cell in cells[start:]: exec(cell,env)
    new = env['coding_chunks_long']
    load_corpus_records(target/'coding_chunks_long.parquet')
    short = new[new.n_words<50]
    assert short.source_utterance_n_words.lt(50).all() and short.utterance_chunk_count.eq(1).all()
    newgroups = dict(tuple(new.groupby('utterance_id',sort=False)))
    for utt,group in newgroups.items():
        source = indexed.loc[utt,'content']
        assert WORD_RE.findall(source)==[w for text in group.content for w in WORD_RE.findall(text)]
        for block in group.itertuples():
            for seg in json.loads(block.source_segments_json):
                assert text_sha256(source[seg['source_start_char']:seg['source_end_char']])==seg['content_sha256']
    for block in old.itertuples():
        group = newgroups[block.utterance_id]
        candidates = group[(group.source_start_char<=block.source_start_char)&(group.source_end_char>=block.source_end_char)]
        assert len(candidates)==1
        replacement=candidates.iloc[0]
        mapping.append(dict(law=law,old_unit_id=block.unit_id,new_unit_id=replacement.unit_id,old_sha256=block.content_sha256,new_sha256=replacement.content_sha256,old_words=block.n_words,new_words=replacement.n_words))
    comparison.append(dict(law=law,old_chunks=len(old),new_chunks=len(new),fewer_chunks=len(old)-len(new),reduction_percent=round(100*(len(old)-len(new))/len(old),2),old_under50=int(old.n_words.lt(50).sum()),new_under50=len(short),new_short_fragments=0,new_over150=int(new.n_words.gt(150).sum()),new_max_words=int(new.n_words.max()),restored_words=int(new.n_words.sum()-old.n_words.sum())))
    if law not in SESSIONS: continue
    sessionpath = ROOT/'output/validation'/SESSIONS[law]
    session=json.loads(sessionpath.read_text())
    for path in (sessionpath,oldpath,folder/'speech_df.parquet',folder/'speech_df_full.parquet',folder/'datos_bcn_akn.parquet'):
        inputs.append(dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    for utt,group in old.groupby('utterance_id',sort=False):
        records=group.sort_values('utterance_chunk_number').to_dict('records')
        for i,record in enumerate(records):
            if record['n_words']>=50: continue
            previous=records[i-1] if i else None; following=records[i+1] if i+1<len(records) else None
            short_rows.append(dict(law=law,unit_id=record['unit_id'],utterance_id=utt,n_words=record['n_words'],utterance_words=count_words(indexed.loc[utt,'content']),utterance_chunks=len(records),previous_words_same_utterance=previous['n_words'] if previous else None,next_words_same_utterance=following['n_words'] if following else None,mergeable_whole_neighbor=any(r and r['n_words']+record['n_words']<=150 for r in (previous,following)),content=record['content']))
        # Intervalos originales que la versión 1 dejó fuera del corpus de bloques.
        spans=sorted((seg['source_start_char'],seg['source_end_char']) for r in records for seg in json.loads(r['source_segments_json']))
        source=indexed.loc[utt,'content']; last=0
        for begin,end in [*spans,(len(source),len(source))]:
            gap=source[last:begin].strip()
            if count_words(gap): omitted.append(dict(law=law,utterance_id=utt,n_words=count_words(gap),content=gap,has_other_chunks=True))
            last=end
    codable=speech[speech.kind.eq('participation')&speech.analysis_included&~speech.is_preamble]
    for row in codable[~codable.utterance_id.isin(old.utterance_id)].itertuples():
        if str(row.content).strip():
            assert count_words(row.content)<5
            omitted.append(dict(law=law,utterance_id=row.utterance_id,n_words=count_words(row.content),content=row.content,has_other_chunks=False))
    for item in session['items']:
        original=old[old.unit_id.eq(item['unit_id'])].iloc[0]
        assert original.content==item['target_text']
        for ann in item['annotations']:
            span=ann['span']; assert item['target_text'][span['start_char']:span['end_char']]==span['text']
        sample=dict(law=law,sample_number=item['sample_index']+1,unit_id=item['unit_id'],n_words=item['n_words'],decision=item['decision'],annotations=len(item['annotations']),quality_flags='|'.join(item['quality_flags']))
        for side in ('previous','next'):
            ctx=item.get(f'{side}_context')
            sample[f'{side}_same_utterance']=ctx['same_utterance'] if ctx else None
            sample[f'{side}_same_actor']=bool(indexed.loc[item['utterance_id'],'speaker_id']==indexed.loc[ctx['utterance_id'],'speaker_id']) if ctx and ctx['utterance_id'] in indexed.index else None
        samples.append(sample)
    shorts=[r for r in short_rows if r['law']==law]
    metrics[law]=dict(corpus_chunks=len(old),under_50=len(shorts),under_20=sum(r['n_words']<20 for r in shorts),short_entire_utterance=sum(r['utterance_chunks']==1 for r in shorts),short_inside_long_utterance=sum(r['utterance_chunks']>1 for r in shorts),mergeable_whole_neighbor_under50=sum(bool(r['mergeable_whole_neighbor']) for r in shorts),sample_statements=sum(i['decision']=='statements' for i in session['items']),sample_annotations=sum(len(i['annotations']) for i in session['items']),sampling=session['sampling'],book_version=session['codebook']['version'],book_sha256=session['codebook']['sha256'],omitted_fragments=sum(r['law']==law and r['has_other_chunks'] for r in omitted),omitted_whole_utterances=sum(r['law']==law and not r['has_other_chunks'] for r in omitted))
for path in (ROOT/'features/coding_chunks.py',ROOT/'proc.qmd',ROOT/'features/manual_validation/service.py'):
    inputs.append(dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
metrics['inputs']=inputs
(OUT/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
(OUT/'new_metrics.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2))
for name,records in [('short_chunks',short_rows),('sample_checks',samples),('omitted',omitted),('unit_mapping',mapping)]:
    pd.DataFrame(records).to_csv(OUT/f'{name}.csv',index=False)
# Los mapeos son datos procesados, conservados también en Parquet.
pd.DataFrame(mapping).to_parquet(OUT/'unit_mapping.parquet',index=False)
# Probar la apertura con copias; open_item actualiza marcas temporales.
validation_copy=NEW_ROOT/'validation_copy'
shutil.copytree(ROOT/'output/validation',validation_copy,dirs_exist_ok=True)
service=ValidationService(source_path=NEW_ROOT,codebook_path=ROOT/'data/codebook/codebook_v0.3.json',output_dir=validation_copy)
for filename in SESSIONS.values():
    original=json.loads((ROOT/'output/validation'/filename).read_text())
    for i,item in enumerate(original['items']):
        assert service.open_item(Path(filename).stem,i)['item']['target_text']==item['target_text']
print(json.dumps(comparison,ensure_ascii=False,indent=2))
temporary.cleanup()
