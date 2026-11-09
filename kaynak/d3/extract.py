# Her PDF'ten kompakt metin çıkarır: başlık, kazanım, kavramlar, ders akışı, bağlantılar
import sys, os, re, subprocess, json
root, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
idx=[]
for dp,_,fs in os.walk(root):
    for f in sorted(fs):
        if not f.endswith('.pdf'): continue
        p=os.path.join(dp,f); rel=os.path.relpath(p,root)
        parts=rel.split(os.sep)
        t=subprocess.run(['pdftotext','-layout',p,'-'],capture_output=True,text=True).stdout
        t=re.sub(r'[ \t]+',' ',t); lines=[l.strip() for l in t.split('\n') if l.strip()]
        txt='\n'.join(lines)
        head=' '.join(lines[:12])
        m=re.search(r'(\d)\s*DERS SAAT',head,re.I) or re.search(r'(\d+)\s*\((\d+)\s*[×x]',head)
        sure=int(m.group(1)) if m else None
        kaz=re.findall(r'^• ?([A-ZÇĞİÖŞÜ]{1,6}(?:\.[A-Z0-9]+)+\.?)\s',txt,re.M)
        kav=''
        mk=re.search(r'Anahtar Kavramlar\n(.+)',txt)
        if mk: kav=mk.group(1).lstrip('• ')
        # ders akışı
        a=txt.find('Öğrenme Etkinlikleri'); b=txt.find('Ölçme ve Değerlendirme Yöntem')
        akis=txt[a:b] if a>0 else ''
        akis='\n'.join(l for l in akis.split('\n') if not re.match(r'^(TEKNOLOJİ ODAKLI|İlgili Beceriler|Çerçevesi|\d+ \S)',l))
        # bağlantılar
        links=re.findall(r'(\d+)\. ([^\n]{2,120}?):?\s*(https?://meb\.ai/[A-Za-z0-9]+)',txt.replace('\n',' '))
        seen=set(); L=[]
        for n,name,u in links:
            if u in seen: continue
            seen.add(u); L.append([name.strip(' :'),u.split('/')[-1]])
        rec={'id':len(idx),'sinif':parts[0],'ders':parts[1],'dosya':parts[-1][:-4],'sure':sure,'kod':kaz[:4],'kav':kav,'link':L,'akis_len':len(akis)}
        idx.append(rec)
        open(os.path.join(out,f'{rec["id"]:03d}.txt'),'w').write(f"## {rel}\nSURE:{sure} KOD:{' '.join(kaz[:4])}\nKAV:{kav}\n"+akis+"\nLINKS:"+json.dumps(L,ensure_ascii=False))
json.dump(idx,open(os.path.join(out,'index.json'),'w'),ensure_ascii=False,indent=0)
print(len(idx))
