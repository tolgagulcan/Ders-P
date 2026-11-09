# Akışı çıkarılamamış senaryoları (İngilizce ve farklı başlıklı olanlar) yeniden çıkarır. Kullanım: yeniden_cikar.py <zip kökü>
import sys, os, re, subprocess, json
K = os.path.dirname(os.path.abspath(__file__)); root = sys.argv[1]
I = json.load(open(os.path.join(K, 'index.json'), encoding='utf-8'))
BAS = re.compile(r'Öğrenme ?Etkinlikleri|Learning Activities|^Activities$|^Before the Lesson|^Lesson 1\b|^1\.? ?(?:ve 2\.? )?Ders \(|^Ders Öncesi Çalışmalar', re.M)
SON = re.compile(r'Ölçme ve Değerlendirme Yöntem|Measurement and Assessment|Assessment Methods|^Related Links|^İlgili Bağlantılar', re.M)
for r in I:
    if r['akis_len'] >= 500: continue
    p = os.path.join(root, r['sinif'], r['ders'], r['dosya'] + '.pdf')
    t = subprocess.run(['pdftotext', '-layout', p, '-'], capture_output=True, text=True).stdout
    t = re.sub(r'[ \t]+', ' ', t); lines = [l.strip() for l in t.split('\n') if l.strip()]
    txt = '\n'.join(lines)
    m = BAS.search(txt); e = SON.search(txt, m.end() if m else 0)
    akis = txt[m.start():e.start() if e else len(txt)] if m else ''
    akis = re.sub(r'^(\d+) ve (\d+)\.? Ders', r'\1. ve \2. Ders', akis, flags=re.M)
    akis = re.sub(r'^Lesson (\d+)', r'\1. Ders', akis, flags=re.M)
    akis = '\n'.join(l for l in akis.split('\n') if not re.match(r'^(TEKNOLOJİ ODAKLI|APPLICATION|İlgili Beceriler|Çerçevesi|Related Skills)', l))
    head = ' '.join(lines[:14])
    mm = re.search(r'(\d)\s*(DERS SAAT|LESSON HOUR)', head, re.I)
    if mm: r['sure'] = int(mm.group(1))
    if not r['kav']:
        mk = re.search(r'(?:Anahtar Kavramlar|Key Concepts)\n(.+)', txt)
        if mk: r['kav'] = mk.group(1).lstrip('• ')
    r['akis_len'] = len(akis)
    L = json.dumps(r['link'], ensure_ascii=False)
    open(os.path.join(K, 'ham', f"{r['id']:03d}.txt"), 'w', encoding='utf-8').write(
        f"## {r['sinif']}/{r['ders']}/{r['dosya']}.pdf\nSURE:{r.get('sure')} KOD:{' '.join(r['kod'])}\nKAV:{r['kav']}\n{akis}\nLINKS:{L}")
    print(r['id'], r['ders'], r['sure'], r['akis_len'])
json.dump(I, open(os.path.join(K, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
