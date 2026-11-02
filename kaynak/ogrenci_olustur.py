"""Öğrenci sayıları sayfası: kaynak/ogrenci.json → site/ogrenci-sayilari.html
ogrenci.json: {"Ana":[["A",erkek,kız]], "5":[["A",erkek,kız], ...], ...}"""
import json
from pathlib import Path
KOK = Path(__file__).resolve().parent.parent
TARIH = "02.11.2026"
d = json.loads((KOK / "kaynak/ogrenci.json").read_text(encoding="utf-8"))

satirlar = []
GE = GK = 0
for g in ["Ana", "5", "6", "7", "8"]:
    TE = TK = 0
    for s, e, k in d[g]:
        ad = f"Ana {s}" if g == "Ana" else f"{g}/{s}"
        satirlar.append(f"<tr><td>{ad}</td><td>{k}</td><td>{e}</td><td>{k+e}</td></tr>")
        TE += e; TK += k
    etiket = "Anasınıfı toplam" if g == "Ana" else f"{g}. sınıflar toplam"
    satirlar.append(f'<tr class="ara"><td>{etiket}</td><td>{TK}</td><td>{TE}</td><td>{TK+TE}</td></tr>')
    GE += TE; GK += TK

html = f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#1d3a5c">
<title>Öğrenci Sayıları</title>
<meta property="og:title" content="Öğrenci Sayıları">
<meta property="og:description" content="Halide Edip Adıvar Ortaokulu sınıf öğrenci sayıları ({TARIH}).">
<meta property="og:image" content="https://halidedipadivar.netlify.app/icon-512.png">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<style>
:root{{--bg:#f3f5f8;--surface:#fff;--ink:#16202c;--muted:#5d6b7c;--line:#d9dfe7;--navy:#1d3a5c;--navy-soft:#e5edf6;color-scheme:light;
  padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0f151d;--surface:#17202b;--ink:#e8edf3;--muted:#93a1b2;--line:#2a3644;--navy:#8fb6e0;--navy-soft:#1c2c40;color-scheme:dark}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:15px}}
main{{max-width:560px;margin:0 auto;padding:20px max(16px,env(safe-area-inset-right,0px)) 40px max(16px,env(safe-area-inset-left,0px))}}
h1{{font-size:22px;margin:0 0 2px}}
p{{margin:0 0 14px;color:var(--muted);font-size:13.5px}}
table{{width:100%;border-collapse:collapse;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden;font-variant-numeric:tabular-nums}}
th,td{{padding:8px 14px;text-align:right;border-bottom:1px solid var(--line)}}
th:first-child,td:first-child{{text-align:left}}
thead th{{position:sticky;top:0;background:var(--navy-soft);color:var(--navy);font-size:13px}}
tr.ara td{{font-weight:600;background:var(--bg)}}
tfoot td{{font-weight:700;border-bottom:0;background:var(--navy-soft);color:var(--navy)}}
</style>
</head>
<body>
<main>
<h1>Öğrenci Sayıları</h1>
<p>Halide Edip Adıvar Ortaokulu · {TARIH}</p>
<table>
<thead><tr><th>Sınıf</th><th>Kız</th><th>Erkek</th><th>Toplam</th></tr></thead>
<tbody>
{chr(10).join(satirlar)}
</tbody>
<tfoot><tr><td>Okul toplamı</td><td>{GK}</td><td>{GE}</td><td>{GK+GE}</td></tr></tfoot>
</table>
</main>
</body>
</html>
"""
(KOK / "site/ogrenci-sayilari.html").write_text(html, encoding="utf-8")
print(f"site/ogrenci-sayilari.html üretildi: {GK} kız, {GE} erkek, {GK+GE} toplam")
