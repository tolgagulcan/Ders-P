# Kim Nerede — Halide Edip Adıvar Ortaokulu

İdarecilerin bir öğretmenin ya da sınıfın **şu an** nerede/hangi derste olduğunu gördüğü sayfa.

Yayın adresi: https://halide-edip-kim-nerede.netlify.app
Netlify bu depoya bağlıdır; `main` dalına yapılan her gönderim siteyi otomatik günceller.

## Klasörler

| Yol | İçerik |
|---|---|
| `site/` | Yayınlanan sayfa (Netlify sadece bu klasörü yayınlar) |
| `kaynak/sablon.html` | Sayfanın tasarımı ve kodu; `__DATA__` yerine program verisi konur |
| `kaynak/data.json` | Ders programı verisi: `sınıf → [gün][ders saati] = [ders, [öğretmenler]]` |
| `kaynak/olustur.py` | PDF'i okuyup `data.json` ve `site/index.html` üretir |
| `kaynak/program-*.pdf` | aSc'den alınan kaynak PDF |
| `kaynak/Ogretmen_Ders_Programi.xlsx` | Öğretmen–sınıf–saat listesi (Excel) |

## Program değişince

```bash
pip install pdfplumber
python kaynak/olustur.py yeni_program.pdf
git add -A && git commit -m "Ders programı güncellendi" && git push
```

Sadece tasarım değiştiyse: `python kaynak/olustur.py` (PDF'siz, mevcut `data.json` ile).
