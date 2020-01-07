# Automatic Polarizer

ツクモ工学の[自動偏光子ホルダー(PWA-100)](http://www.twin9.co.jp/product/holders-list/mirror-list-2-2/pwa-100/)をシグマ光機の[1軸ステージコントローラ(GSC-01)](https://www.global-optosigma.com/jp/Catalogs/pno/?from=page&pnoname=GSC-01&ccode=W9042&dcode=)を通して，Pythonで制御します．研究室用に作成．

[![](https://img.youtube.com/vi/dfmbfFGqxJw/0.jpg)](https://www.youtube.com/watch?v=dfmbfFGqxJw)

[https://youtu.be/dfmbfFGqxJw](https://youtu.be/dfmbfFGqxJw)

## Requirement
* [PySerial](https://github.com/pyserial/pyserial)
```
pip install pyserial
```

## Run on command line
```
python automaticpolarizer.py <degree>
```
偏光板を指定した角度`degree`に回転させます．シリアルポート名は`/dev/tty.usbserial-FTRWB1RN`がデフォルトになっています．変更する場合は，`--port`オプションで指定してください．

## Use as a module
### インスタンスの作成
インスタンスの作成時に接続要求が行われます．
```python
from automaticpolarizer import AutomaticPolarizer
polarize = AutomaticPolarizer("/dev/tty.usbserial-FTRWB1RN")
```

### リセット
ステージを機械原点に復帰させます．
```python
polarizer.reset()
```

### 偏光板の角度
クラスのメンバ`degree`は偏光板の角度と連動しています．
```python
print(polarizer.degree) #現在の偏光板の角度を取得
polarizer.degree = 90   #偏光板の角度が90[deg]になるように回転
polarizer.degree += 60  #偏光板の角度が現在の角度から+60[deg]になるように回転
```

### 速度の設定
ステージの移動時の最小速度[PPS]，最大速度[PPS]，加減速時間[mS]（最小速度→最大速度or最大速度→最小速度に切り替わるまでの時間）を設定します．
```python
spd_min = 500 #最小速度[PPS]
spd_max = 5000 #最大速度[PPS]
acceleration_time = 200 #加減速時間[mS]
polarizer.set_speed(spd_min, spd_max, acceleration_time)
```
