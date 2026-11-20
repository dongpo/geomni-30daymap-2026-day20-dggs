import json,csv,datetime,collections
from pathlib import Path
p=Path(__file__).resolve().parents[1];d=json.load(open(p/'data.json'));expect=collections.Counter()
for kind,fn,col,valuecol in [('m','metro-202312.csv','出站','人次'),('b','youbike-202312.csv','借車站',None)]:
 target='公館' if kind=='m' else '捷運公館站(2號出口)'
 for r in csv.DictReader(open(p/'source'/fn,encoding='utf-8-sig')):
  date=r['日期'] if kind=='m' else r['借車日期']
  if not date.startswith('2023-12-') or r[col]!=target:continue
  h=int(r['時段']) if kind=='m' else int(r['借車時間'][11:13])
  if h not in [8,18]:continue
  g=int(datetime.date.fromisoformat(date).weekday()>=5)
  expect[(kind,g,h)]+=int(r[valuecol]) if valuecol else 1
 point=next(x for x in d['points'][kind] if x['name']==target)
 for g in [0,1]:
  for h in [8,18]:assert point['counts'][g][h]==expect[(kind,g,h)]
result={'independent_raw_csv_checks':{str(k):v for k,v in expect.items()},'passed':True}
(p/'evidence/independent-qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(result)
