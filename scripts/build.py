import csv,json,hashlib,datetime,collections,time
from pathlib import Path
from dggal import *
from shapely.geometry import Point,Polygon
p=Path(__file__).resolve().parents[1];s=p/'source';t=time.perf_counter()
sp=json.loads((s/'spatial-v2.json').read_text());points={'m':sp['metro'],'b':sp['bikes']}
# Only exact, unique name matches. Never fuzzy-geocode unmatched historic stations.
nameidx={k:{pt['name']:i for i,pt in enumerate(v)} for k,v in points.items()}
assert all(len(v)==len(nameidx[k]) for k,v in points.items())
counts={k:[[[0]*24 for g in range(2)] for pt in v] for k,v in points.items()}
dates={k:set() for k in points};hours={k:set() for k in points};unmatched={k:collections.Counter() for k in points};rows={k:0 for k in points};rawtot={k:0 for k in points};mapped={k:0 for k in points};datecounts={k:collections.Counter() for k in points};nulls={k:0 for k in points};excluded_period={'rows':0,'count':0}
def grp(date):return int(datetime.date.fromisoformat(date).weekday()>=5)
for r in csv.DictReader((s/'youbike-202312.csv').open(encoding='utf-8-sig')):
 date=r['借車日期'];dt=datetime.datetime.fromisoformat(r['借車時間']);h=dt.hour;assert dt.utcoffset().total_seconds()==28800
 assert date==dt.date().isoformat();dates['b'].add(date);hours['b'].add(h);rows['b']+=1;rawtot['b']+=1;datecounts['b'][date]+=1
 i=nameidx['b'].get(r['借車站'])
 if i is None:unmatched['b'][r['借車站']]+=1;continue
 counts['b'][i][grp(date)][h]+=1;mapped['b']+=1
for r in csv.DictReader((s/'metro-202312.csv').open(encoding='utf-8-sig')):
 date=r['日期'];h=int(r['時段']);n=int(r['人次']);assert n>=0
 if not date.startswith('2023-12-'):excluded_period['rows']+=1;excluded_period['count']+=n;continue
 dates['m'].add(date);hours['m'].add(h);rows['m']+=1;rawtot['m']+=n;datecounts['m'][date]+=n
 station={'大橋頭站':'大橋頭'}.get(r['出站'],r['出站'])
 i=nameidx['m'].get(station)
 if i is None:unmatched['m'][r['出站']]+=n;continue
 counts['m'][i][grp(date)][h]+=n;mapped['m']+=n
assert dates['m']==dates['b'];assert len(dates['m'])==31
den=[sum(grp(x)==g for x in dates['m']) for g in range(2)];assert den==[21,10]
for k in points:
 for i,pt in enumerate(points[k]):pt['counts']=counts[k][i]
 # Retain only stations actually present in the historical dataset; zero observed all month is not a new 2026 station.
active={k:set(i for i,c in enumerate(counts[k]) if sum(map(sum,c))>0) for k in points}
app=Application(appGlobals=globals());pydggal_setup(app);d=ISEA3H();levels={};qa={}
for lv in [16,17,18]:
 zones={}
 for k,pts in points.items():
  for i in active[k]:
   pt=pts[i];z=d.getZoneFromWGS84Centroid(lv,GeoPoint(pt['lat'],pt['lon']));id=d.getZoneTextID(z)
   if id not in zones:
    vs=[[float(v.lon),float(v.lat)] for v in d.getZoneRefinedWGS84Vertices(z,0)];vs.append(vs[0]);cen=d.getZoneWGS84Centroid(z)
    zones[id]={'ring':vs,'centroid':[float(cen.lon),float(cen.lat)],'area':d.getZoneArea(z),'m':[],'b':[],'sums':{t:[[0]*24 for g in range(2)] for t in points}}
   rec=zones[id];rec[k].append(i)
   assert Polygon(rec['ring']).buffer(1e-8).covers(Point(pt['lon'],pt['lat']))
   assert d.getZoneTextID(d.getZoneFromTextID(id))==id
   for g in range(2):
    for h in range(24):rec['sums'][k][g][h]+=counts[k][i][g][h]
 for k in points:
  assert sum(sum(map(sum,z['sums'][k])) for z in zones.values())==mapped[k]
 levels[str(lv)]=zones;qa[str(lv)]={'cells':len(zones),'metro_sum':sum(sum(map(sum,z['sums']['m'])) for z in zones.values()),'bike_sum':sum(sum(map(sum,z['sums']['b'])) for z in zones.values()),'all_points_inside':True,'id_roundtrip':True}
# Availability: missing metro hours remain null; bike hours3/4 absent across source => null, not measured0.
data={'points':points,'levels':levels,'boundary':sp['boundary'],'lines':sp['lines'],'days':den,'hours':{k:sorted(v) for k,v in hours.items()},'period':'2023-12','qa':{'excluded_metro_other_month':excluded_period,'raw_rows':rows,'raw_totals':rawtot,'mapped_totals':mapped,'active_stations':{k:len(v) for k,v in active.items()},'unmatched_bike_rows':sum(unmatched['b'].values())}}
(p/'data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
(p/'data.js').write_text('const D='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
(p/'evidence/qa.json').write_text(json.dumps({'elapsed_seconds':time.perf_counter()-t,'levels':qa,'days':den,'date_counts':{k:dict(v) for k,v in datecounts.items()},'hours':data['hours'],**data['qa']},ensure_ascii=False,indent=2))
(p/'evidence/unmatched.json').write_text(json.dumps({k:dict(v) for k,v in unmatched.items()},ensure_ascii=False,indent=2))
(p/'source/sha256.json').write_text(json.dumps({x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in s.iterdir() if x.name!='sha256.json'},indent=2))
print(json.dumps(data['qa'],ensure_ascii=False));print('seconds',time.perf_counter()-t)
