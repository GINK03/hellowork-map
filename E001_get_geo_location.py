
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
