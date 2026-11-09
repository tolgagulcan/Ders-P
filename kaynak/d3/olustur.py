# D3 senaryo sayfalarını üretir.
# Girdi : kaynak/d3/index.json (PDF'lerden çıkarılan bilgiler), kaynak/d3/ham/*.txt, kaynak/d3/ozet/*.json (elle yazılan özetler)
# Çıktı : site/d3.html (giriş), site/d3/<sinif>-<ders>.html (branş), site/d3/s/<id>.html (senaryo)
# Kullanım: python kaynak/d3/olustur.py
import json, os, re, glob, html, unicodedata

K = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(K, '..', '..', 'site')
idx = {r['id']: r for r in json.load(open(os.path.join(K, 'index.json'), encoding='utf-8'))}

DERS_AD = {'Arapca': 'Arapça', 'Bilisim Teknolojileri': 'Bilişim Teknolojileri', 'Din Kulturu': 'Din Kültürü',
           'Fen Bilimleri': 'Fen Bilimleri', 'Ingilizce': 'İngilizce', 'Matematik': 'Matematik',
           'Sosyal Bilgiler': 'Sosyal Bilgiler', 'Turkce': 'Türkçe', 'Inkilap Tarihi': 'İnkılap Tarihi', 'Diger': 'Diğer'}
SINIF_AD = {'5. Sinif': '5. Sınıf', '6. Sinif': '6. Sınıf', '7. Sinif': '7. Sınıf', '8. Sinif': '8. Sınıf',
            'Turkce Dil Kursu': 'Türkçe Dil Kursu'}
SINIF_SIRA = list(SINIF_AD)
# Aylık bültenler: ay -> senaryo id listesi (özette 'pdf' alanı varsa D3'teki doğrudan PDF linki kullanılır)
BULTEN = {'Ekim': [100, 258, 114, 268, 57, 209, 80, 223, 165, 67]}
PDF_GENEL = 'https://d3.eba.gov.tr/senaryolar'

def slug(s):
    s = unicodedata.normalize('NFKD', s.replace('ı', 'i').replace('İ', 'I')).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def norm(s):
    return re.sub(r'\s+', ' ', s.replace('İ', 'i').replace('I', 'ı').lower())

def etiketler(dersler):
    """Her ders öğesinin kapsadığı ders numaraları. Öğede 3. alan varsa ("1-2" gibi) o kullanılır."""
    out, n = [], 1
    for d in dersler:
        if len(d) > 2:
            a, _, b = str(d[2]).partition('-'); rng = list(range(int(a), int(b or a) + 1))
        else:
            rng = [n]
        out.append(rng); n = rng[-1] + 1
    return out

def link_dagit(i, dersler):
    """Her bağlantıyı adının ilk geçtiği yerdeki derse koyar ('Ders Öncesi' notu bir sonraki derse sayılır)."""
    t = open(os.path.join(K, 'ham', f'{i:03d}.txt'), encoding='utf-8').read().rsplit('\nLINKS:', 1)[0]
    t = norm(re.sub(r'\s*\n\s*', ' ', t))
    isaret = [(m.start(), int(m.group(1)) if m.group(1) else None)
              for m in re.finditer(r'(\d)\.(?: ve \d\.)? ?ders\b|ders öncesi', t)]
    ets = etiketler(dersler)
    out = [[] for _ in dersler]
    elle = {int(k): v for k, v in oz[i].get('link_ders', {}).items()}  # özetteki elle düzeltme: link sırası -> ders no
    for j, (ad, kod) in enumerate(idx[i]['link'], 1):
        key = norm(ad.replace('EBA ', ''))[:22]
        pos = t.find(key)
        no, son = None, 0
        for p, num in isaret:
            if pos < 0 or p > pos: break
            no = num if num else son + 1
            if num: son = num
        if pos < 0 or no is None: no = ets[-1][-1] if pos < 0 else 1
        no = elle.get(j, no)
        k = next((k for k, r in enumerate(ets) if no in r), min(range(len(ets)), key=lambda k: abs(ets[k][0] - no)))
        out[k].append((ad, kod))
    return out

e = lambda s: html.escape(str(s))

CSS = '''<style>
:root{--bg:#f3f5f8;--card:#fff;--ink:#16202c;--muted:#5d6b7c;--line:#d9dfe7;--accent:#1d3a5c;--soft:#e5edf6;--link:#1f5fbf;--hd:#1d3a5c;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#0f151d;--card:#17202b;--ink:#e8edf3;--muted:#93a1b2;--line:#2a3644;--accent:#8fb6e0;--soft:#1c2c40;--link:#8fb6e0;--hd:#0b1118;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
header{background:var(--hd);color:#fff;padding:22px 16px 18px}header .w{padding:0}
.w{max-width:820px;margin:0 auto;padding:0 16px}
.k{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:#9fc3ea;font-weight:600}
h1{margin:4px 0;font-size:24px;line-height:1.25}header p{margin:0;color:#c3c8d2;font-size:14px}header a{color:#fff}
main{padding:18px 0 40px}
.nav{font-size:14px;margin-bottom:12px}.nav a{color:var(--link);text-decoration:none;font-weight:600}
h2{font-size:19px;margin:22px 0 10px}
.grid{display:flex;flex-wrap:wrap;gap:8px}
.btn{display:inline-block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 14px;color:var(--ink);text-decoration:none}
.btn small{color:var(--muted)}.btn.off{opacity:.5;pointer-events:none}
.item{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin-bottom:8px;color:var(--ink);text-decoration:none}
.item:hover{border-color:var(--accent)}.item b{display:block;font-size:17px}.item p{margin:2px 0 0;color:var(--muted);font-size:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}
.meta{display:flex;flex-wrap:wrap;gap:6px}.tag{background:var(--soft);border-radius:6px;padding:2px 8px;font-size:13px;color:var(--muted)}
h3{font-size:14px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin:18px 0 8px}
.ozu{border-left:3px solid var(--accent);padding:8px 14px;background:var(--soft);border-radius:0 8px 8px 0}.ozu p{margin:0}
table{border-collapse:collapse;width:100%;font-size:14px;margin-top:8px}td,th{border:1px solid var(--line);padding:6px 8px;text-align:left}
ol.d{list-style:none;padding:0;margin:0}ol.d li{padding:10px 0;border-top:1px solid var(--line)}ol.d li:first-child{border-top:0}ol.d b{display:block}
.lk{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}.lk a{background:var(--soft);border-radius:8px;padding:4px 10px;font-size:14px;text-decoration:none;color:var(--link)}
.pdf{display:inline-block;margin-top:16px;background:#1d3a5c;color:#fff;text-decoration:none;padding:9px 16px;border-radius:8px;font-weight:600}
@media (max-width:560px){h1{font-size:21px}.card{padding:16px}}
</style>'''

def sayfa(title, ust, govde, desc='Halide Edip Adıvar Ortaokulu · Teknoloji odaklı örnek ders planları'):
    return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow"><meta name="theme-color" content="#1d3a5c">
<title>{e(title)}</title><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="https://halidedipadivar.netlify.app/icon-512.png">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">{CSS}</head>
<body><header><div class="w"><div class="k">D3 · Örnek Ders Planları</div><h1>{e(ust)}</h1>
<p>Halide Edip Adıvar Ortaokulu · Tamamı: <a href="https://d3.eba.gov.tr/" target="_blank" rel="noopener">d3.eba.gov.tr</a></p></div></header>
<main><div class="w">{govde}</div></main></body></html>'''

# --- özetleri yükle
oz = {}
for f in sorted(glob.glob(os.path.join(K, 'ozet', '*.json'))):
    for s in json.load(open(f, encoding='utf-8')):
        oz[s['id']] = s
bulten_pdf = {i: s['pdf'] for i, s in oz.items() if s.get('pdf')}

os.makedirs(os.path.join(SITE, 'd3', 's'), exist_ok=True)
for old in glob.glob(os.path.join(SITE, 'd3', 's', '*.html')) + glob.glob(os.path.join(SITE, 'd3', '*.html')):
    os.remove(old)

def bslug(r): return slug(f"{r['sinif']}-{r['ders']}")

# --- senaryo sayfaları
for i, s in oz.items():
    r = idx[i]
    sinif, ders = SINIF_AD[r['sinif']], DERS_AD[r['ders']]
    L = link_dagit(i, s['dersler'])
    ets = etiketler(s['dersler'])
    lis = ''
    for k, d in enumerate(s['dersler']):
        bas, metin = d[0], d[1]
        no = f'{ets[k][0]}–{ets[k][-1]}' if len(ets[k]) > 1 else ets[k][0]
        lk = ''.join(f'<a href="https://meb.ai/{c}" target="_blank" rel="noopener">🔗 {e(a)}</a>' for a, c in L[k])
        lis += f'<li><b>{no}. ders: {e(bas)}</b>{e(metin)}{f"<div class=lk>{lk}</div>" if lk else ""}</li>'
    tags = [ders, sinif] + ([f"{r['sure']} ders saati"] if r.get('sure') else []) + [c.rstrip('.') for c in r['kod'][:3]]
    pdf = f'https://d3.eba.gov.tr/pdf-goster/dosya_{bulten_pdf[i]}' if i in bulten_pdf else PDF_GENEL
    pdf_txt = "📄 Senaryonun PDF'ini aç" if i in bulten_pdf else "📄 Tam senaryo (d3.eba.gov.tr → Senaryolar)"
    g = f'''<div class="nav"><a href="../{bslug(r)}.html">← {e(sinif)} {e(ders)}</a></div>
<article class="card"><div class="meta">{''.join(f'<span class="tag">{e(t)}</span>' for t in tags)}</div>
<h2 style="margin-top:8px">{e(s['ad'])}</h2><p>{e(s['ozet'])}</p>
<h3>Konunun özü</h3><div class="ozu">{s['ozu']}</div>
<h3>Ders ders akış</h3><ol class="d">{lis}</ol>
<h3>Gerekenler</h3><p>{e(s['gerek'])}</p>
<a class="pdf" href="{pdf}" target="_blank" rel="noopener">{pdf_txt}</a></article>'''
    open(os.path.join(SITE, 'd3', 's', f'{i:03d}.html'), 'w', encoding='utf-8').write(
        sayfa(s['ad'], s['ad'], g, f"{sinif} {ders} · {s['ozet']}"))

# --- branş sayfaları
grup = {}
for i, r in idx.items():
    grup.setdefault((r['sinif'], r['ders']), []).append(i)
for (sn, dr), ids in grup.items():
    hazir = [i for i in ids if i in oz]
    if not hazir: continue
    uniteler = {}
    for i in hazir: uniteler.setdefault(oz[i]['unite'], []).append(i)
    g = '<div class="nav"><a href="../d3.html">← Tüm sınıflar</a></div>'
    if len(hazir) < len(ids):
        g += f'<p style="color:var(--muted)">{len(ids)} senaryodan {len(hazir)} tanesinin özeti hazır; diğerleri ekleniyor.</p>'
    for u, us in uniteler.items():
        g += f'<h2>{e(u)}</h2>' + ''.join(
            f'<a class="item" href="s/{i:03d}.html"><b>{e(oz[i]["ad"])}</b><p>{e(oz[i]["ozet"])}</p></a>' for i in us)
    t = f'{SINIF_AD[sn]} {DERS_AD[dr]}'
    open(os.path.join(SITE, 'd3', f'{slug(sn + "-" + dr)}.html'), 'w', encoding='utf-8').write(sayfa(t, t, g))

# --- giriş sayfası
g = ''
for ay, ids in BULTEN.items():
    var = [i for i in ids if i in oz]
    if var:
        g += f'<h2>{e(ay)} ayı senaryoları</h2>' + ''.join(
            f'<a class="item" href="d3/s/{i:03d}.html"><b>{e(oz[i]["ad"])}</b><p>{e(SINIF_AD[idx[i]["sinif"]])} · {e(DERS_AD[idx[i]["ders"]])}</p></a>' for i in var)
for sn in SINIF_SIRA:
    dl = sorted({dr for (s_, dr) in grup if s_ == sn}, key=lambda d: slug(DERS_AD[d]))
    if not dl: continue
    g += f'<h2>{e(SINIF_AD[sn])}</h2><div class="grid">'
    for dr in dl:
        ids = grup[(sn, dr)]; n = sum(1 for i in ids if i in oz)
        cls = 'btn' if n else 'btn off'
        g += f'<a class="{cls}" href="d3/{slug(sn + "-" + dr)}.html">{e(DERS_AD[dr])} <small>{n}/{len(ids)}</small></a>'
    g += '</div>'
open(os.path.join(SITE, 'd3.html'), 'w', encoding='utf-8').write(sayfa('D3 Örnek Ders Planları', 'Örnek Ders Planları', g))
print('özet:', len(oz), '/', len(idx))
