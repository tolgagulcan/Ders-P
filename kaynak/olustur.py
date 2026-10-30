"""
Kim Nerede — siteyi üretir.

Kullanım:
    python kaynak/olustur.py                     # mevcut kaynak/data.json ile site/index.html üretir
    python kaynak/olustur.py yeni_program.pdf    # önce PDF'ten data.json'u yeniler, sonra siteyi üretir

Gereken: pip install pdfplumber   (sadece PDF okunacaksa)

PDF, aSc Ders Planlayıcı'nın "Sınıf Ders Programları" çıktısı olmalı:
her sayfa bir sınıf; üstte 5 gün × 8 saat ızgarası, altta "Dersin Adı / HDS / Öğretmenin Adı" tablosu.
"""
import json
import re
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
KAYNAK = KOK / "kaynak"
SITE = KOK / "site"
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def pdf_oku(pdf_yolu):
    """PDF'teki her ders saatini {sinif: [gün][saat] = [ders, [öğretmenler]]} yapısına çevirir."""
    import pdfplumber

    veri = {}
    sorunlar = []
    with pdfplumber.open(pdf_yolu) as pdf:
        for no, sayfa in enumerate(pdf.pages, 1):
            m = re.search(r"Sınıfın Adı\s+(\S+)", sayfa.extract_text() or "")
            if not m:
                continue
            sinif = m.group(1)
            tablolar = sayfa.extract_tables()
            izgara = next(t for t in tablolar if t and t[0] and len(t[0]) >= 9 and "8:50" in (t[0][1] or ""))
            bilgi = next(t for t in tablolar if t and t[0] and norm(t[0][0]) == "Dersin Adı")
            dersler = [(norm(r[0]), norm(r[2])) for r in bilgi[1:] if norm(r[0]) and norm(r[0]) != "Toplam Saat"]

            tablo = [[None] * 8 for _ in GUNLER]
            for satir in izgara[1:]:
                g = GUNLER.index(norm(satir[0]))
                for s, hucre in enumerate(satir[1:9]):
                    metin = norm(hucre).replace(" ", "")
                    if not metin:
                        continue
                    # PDF'te bölünmüş adlar ("REHBERL İK") için boşluksuz karşılaştır, en uzun eşleşen ders adı kazanır
                    aday = [(len(d), d, o) for d, o in dersler if metin.startswith(d.replace(" ", ""))]
                    if not aday:
                        sorunlar.append(f"{sinif} {GUNLER[g]} {s + 1}. ders: {norm(hucre)}")
                        continue
                    _, ders, ogretmen = max(aday)
                    tablo[g][s] = [ders, [t.strip() for t in ogretmen.split(",")]]
            veri[sinif] = tablo

    if sorunlar:
        print("Eşleşmeyen hücreler:\n  " + "\n  ".join(sorunlar))
    return veri


def site_uret(veri):
    sablon = (KAYNAK / "sablon.html").read_text(encoding="utf-8")
    govde = sablon.replace("__DATA__", json.dumps(veri, ensure_ascii=False, separators=(",", ":")))
    # şablonun <style> bloğuna kadar olan kısmı <head>'e, kalanı <body>'ye
    i = govde.index("</style>") + len("</style>")
    bas = (
        '<!doctype html>\n<html lang="tr">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="robots" content="noindex, nofollow">\n<meta name="theme-color" content="#1d3a5c">\n'
        "<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}"
        "body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n"
        # telefona uygulama olarak eklenince: ad "Ders-P", simge, tam ekran
        '<link rel="manifest" href="/manifest.webmanifest">\n'
        '<link rel="icon" type="image/png" href="/favicon.png">\n'
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
        '<meta name="apple-mobile-web-app-capable" content="yes">\n'
        '<meta name="mobile-web-app-capable" content="yes">\n'
        '<meta name="apple-mobile-web-app-title" content="Ders-P">\n'
        '<meta name="application-name" content="Ders-P">\n'
        '<meta name="apple-mobile-web-app-status-bar-style" content="default">\n'
    )
    sw = '<script>if("serviceWorker" in navigator)addEventListener("load",()=>navigator.serviceWorker.register("/sw.js").catch(()=>{}));</script>\n'
    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(bas + govde[:i] + "\n</head>\n<body>\n" + govde[i:] + "\n" + sw + "</body>\n</html>\n", encoding="utf-8")


if __name__ == "__main__":
    veri_yolu = KAYNAK / "data.json"
    if len(sys.argv) > 1:
        veri = pdf_oku(sys.argv[1])
        veri_yolu.write_text(json.dumps(veri, ensure_ascii=False, indent=1), encoding="utf-8")
        saat = {s: sum(1 for g in t for h in g if h) for s, t in veri.items()}
        print(f"{len(veri)} sınıf okundu: " + ", ".join(f"{s}={n}" for s, n in saat.items()))
    else:
        veri = json.loads(veri_yolu.read_text(encoding="utf-8"))
    site_uret(veri)
    print(f"site/index.html üretildi ({len(veri)} sınıf).")
