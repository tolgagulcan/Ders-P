# Kullanım: show.py id [id...]  -> derslere bölünmüş, kırpılmış akış
import sys,re,json
D=__import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/ham/'
LIM=int(__import__('os').environ.get('LIM','900'))
for i in sys.argv[1:]:
    t=open(D+f'{int(i):03d}.txt').read()
    head,_,rest=t.partition('\n'); meta=rest.split('\n')[:2]
    body=rest.split('\n',2)[2].rsplit('\nLINKS:',1)
    akis,links=body[0],json.loads(body[1])
    print(f'=== {i} {head[3:]}\n{meta[0]} | {meta[1][:120]}')
    blocks=re.split(r'\n(?=\d\. ?Ders\b)',akis)
    for b in blocks:
        b=re.sub(r'\s*\n\s*',' ',b)
        print(' >',b[:LIM])
    print(' L:',' | '.join(f'{k+1}.{n}' for k,(n,u) in enumerate(links)))
