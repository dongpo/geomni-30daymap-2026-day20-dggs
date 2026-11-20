from pathlib import Path
from urllib.parse import quote
p=Path(__file__).resolve().parents[1]
s=(p/'index.html').read_text().replace('<link rel="stylesheet" href="vendor/leaflet.css">','<style>'+(p/'vendor/leaflet.css').read_text()+'</style>')
for f in ['vendor/leaflet.js','data.js']:s=s.replace('<script src="'+f+'"></script>','<script>'+(p/f).read_text().replace('</script','<\\/script')+'</script>')
s=s.replace('href="DATA-NOTES.txt"','href="data:text/plain;charset=utf-8,'+quote((p/'DATA-NOTES.txt').read_text())+'" download="DATA-NOTES.txt"')
(p/'portable.html').write_text(s)
