# Kullanım: python guncelle.py ozet/dosya.json < yeni.json  -> id'si aynı olanları değiştirir, yenileri ekler
import sys, json
f = sys.argv[1]
try: eski = json.load(open(f, encoding='utf-8'))
except FileNotFoundError: eski = []
yeni = json.load(sys.stdin)
m = {s['id']: s for s in eski}
for s in yeni: m[s['id']] = s
json.dump(sorted(m.values(), key=lambda s: s['id']), open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f, len(m))
