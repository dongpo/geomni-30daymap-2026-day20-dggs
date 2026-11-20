import csv,json,collections,datetime
from pathlib import Path
p=Path(__file__).resolve().parents[1]
b=json.load(open('outputs/day20-dggs-transit-v2/source/youbike-taipei.json'))
names={x['sna'].replace('YouBike2.0_',''):x for x in b}
c=collections.Counter(); dates=collections.Counter();h=collections.Counter();bad=collections.Counter();rn=0
for r in csv.DictReader((p/'source/youbike-202312.csv').open()):
 rn+=1;c[r['借車站']]+=1;dates[r['借車日期']]+=1;h[r['借車時間'][11:13]]+=1
 if r['借車站'] not in names:bad[r['借車站']]+=1
print(json.dumps({'rows':rn,'dates':dict(dates),'hours':dict(h),'stations':len(c),'unmatched_stations':len(bad),'unmatched_rows':sum(bad.values()),'top_unmatched':bad.most_common(15)},ensure_ascii=False,indent=2))
(p/'evidence/bike-profile.json').write_text(json.dumps({'rows':rn,'dates':dict(dates),'hours':dict(h),'stations':len(c),'unmatched':dict(bad)},ensure_ascii=False,indent=2))
