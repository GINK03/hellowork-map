# ハローワークの求人を可視化

## ハローワークの大きな問題点
 - 簡単にパートタイムで働きたい、近い職場にこだわりがある、網羅的に給料で逆引き検索したいなど、ハローワークのWebシステムは検索機能が貧弱で思ったように検索できない
 
## 会社の名前と登録住所から緯度経度を得る
  Google APIのGeoCodeを用いるとできる  
  2019年で、1件あたり0.5セント ⇒ 0.5円くらい  

```python
from pathlib import Path
import json
import pandas as pd
import requests
from concurrent.futures import ProcessPoolExecutor as PPE
import os
GOOGLE_API_GEO = os.environ['GOOGLE_API_GEO']
url = f'https://maps.googleapis.com/maps/api/geocode/json?key={GOOGLE_API_GEO}'

df = pd.read_csv('./local.csv')
df = df[pd.notnull(df['所在地'])]

Path('geos').mkdir(exist_ok=True)
def pmap(arg):
    key, geos = arg
    for geo in geos:
        if Path(f'geos/{geo}.json').exists():
            continue
        params = {'sensor': 'false', 'address': geo}
        r = requests.get(url, params=params)
        result = r.json()
        if result['status'] != 'OK':
            print('cannot do this')
            continue
        result['OriginGeo'] = geo
        print(result)
        with open(f'geos/{geo}.json', 'w') as fp:
            fp.write(json.dumps(result, ensure_ascii=False, indent=2))

print(len(set(df['所在地'].tolist())))
exit()
args = {}
for idx, geo in enumerate(set(df['所在地'].tolist())):
    key = idx%32
    if args.get(key) is None: args[key] = []
    args[key].append(geo)
args = [(key, geos) for key, geos in args.items()]
with PPE(max_workers=24) as exe:
    exe.map(pmap, args)
```

## Jupyterで事業所と、金銭の密度を計算してヒートマップを作成する  
 そもそもお金だけでなく事業所が多いと赤くなってしまうという性質があるので、そもそもヒートマップで出す意義はなんなのかという視点がありますが、単純に求人している事業所密度と
 考えても良さそうです（さらに、賃金が高くなればより赤くなる）
