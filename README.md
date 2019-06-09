# ハローワークの求人を可視化

## ハローワークの大きな問題点
 - 簡単にパートタイムで働きたい、近い職場にこだわりがある、網羅的に給料で逆引き検索したいなど、ハローワークのWebシステムは検索機能が貧弱で思ったように検索できない

## コード
こちらを参照してください  

https://github.com/GINK03/hellowork-map  

使ったデータに関してはスナップショットを撮っているものがあります  
 - [Dropbox](https://www.dropbox.com/s/0cvmt154adaban0/hellowork-map_2019_06_09.tar.gz?dl=0)

## データの取得
 ハローワークのウェブサイトには操作性と基本設計に問題があって（？）、多くのページ遷移がPOSTなどで制御されているようです。結果として簡単なプログラムではデータが取得できず（データの再利用性が悪い）、API等も厚生労働省の審査を受けなくてはいけない(個人が簡単にどうこうするということはあまり想定されていないよう)ということでかなりめんどくさいです。  
 今回はショット分析なので、seleniumでheadlessのgoogle chromeを利用して、POST等をシミュレーションして、webの構造の全体像を把握しました。  
 秒間1アクセスを守っているので怒られないはず...  

```console
$ python3 A001_hellowork.py
$ python3 B001_parse_rough_html_and_scrape_details.py
$ python3 C001_parse_details_from_local_html.py
```

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
<div align="center">
  <img width="100%" src="https://user-images.githubusercontent.com/4949982/59156504-91c94800-8ad7-11e9-9d73-db8e4ce93242.png">
</div> 

この一連の可視化は[データをダウンロード](https://www.dropbox.com/s/0cvmt154adaban0/hellowork-map_2019_06_09.tar.gz?dl=0)して、[このJupyterのファイル](https://github.com/GINK03/hellowork-map/blob/master/VisualizeAndSearch.ipynb)を実行すれば再現することができます。

## 自分の住んでいるところを優先して検索する
 Google Geocode APIから事業所の緯度経度がわかれば、自分のスマホの位置情報やIPアドレスから近い事業所をリストアップすることができます。   
距離の測り方はL1距離としていますが、まだまだ色んな方法がありそうです。 
<div align="center">
  <img width="100%" src="https://user-images.githubusercontent.com/4949982/59156717-0487f280-8adb-11e9-95b3-9c2040aa6670.png">
</div> 
私は渋谷周辺なので試しに渋谷周辺で近い求人、top 1000を計算してみました。

## 全国区のデータ
 全国区のデータをすべてプロットしようとすると激重なので、別途ローカルで実行できるhtmlをおいておきますので、自分で見てみてください  
 
 [ダウンロード](https://www.dropbox.com/s/k2ttc9vfd573vdr/sample_output_total.html?dl=0)  
<div align="center">
   <img width="100%" src="https://user-images.githubusercontent.com/4949982/59156706-afe47780-8ada-11e9-9d61-70c09d007dd7.png">
</div>
 
 ## Webアプリとして加工したい
  エネルギー不足と気力不足でいまいち乗り気になれないのですが、例えば、求人をスマホの位置情報をクエリに入れたりして、パートタイムジョブが簡単に見つけられたら、一部のユーザには需要がありそうなんですよね。  
  Webサービスまで昇華することができれば、今後のユーザの使用具合や応募の様子をトラックすることで、より高精度な会社と人とのマッチングができそうだと考えています。  
  Webアプリとしてもし作りたい方がいらしたら作りませんか？(お金は払えないかもですが、PCとかGPUとか差し上げられるものがいくつかあります)  
 
