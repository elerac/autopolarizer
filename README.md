# Automatic Polarizer

ツクモ工学の[自動偏光子ホルダー(PWA-100)](http://www.twin9.co.jp/product/holders-list/mirror-list-2-2/pwa-100/)をシグマ光機の[1軸ステージコントローラ(GSC-01)](https://www.global-optosigma.com/jp/Catalogs/pno/?from=page&pnoname=GSC-01&ccode=W9042&dcode=)を通して，Pythonで制御します．研究室用に作成．

[![](https://img.youtube.com/vi/dfmbfFGqxJw/0.jpg)](https://www.youtube.com/watch?v=dfmbfFGqxJw)

[https://youtu.be/dfmbfFGqxJw](https://youtu.be/dfmbfFGqxJw)

## Requirement
* [pySerial](https://github.com/pyserial/pyserial)

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
polarizer = AutomaticPolarizer("/dev/tty.usbserial-FTRWB1RN")
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
ステージの移動時の最小速度[PPS]，最大速度[PPS]，加減速時間[mS]（最小速度→最大速度or最大速度→最小速度に切り替わるまでの時間）を設定します．最小速度・最大速度の設定範囲は100-20000です．加減速時間の設定範囲は0-1000です．最大速度は最小速度以上の値に設定する必要があります．速度の設定は100[PPS]単位で行う必要があります．
```python
spd_min = 500 #最小速度[PPS]
spd_max = 5000 #最大速度[PPS]
acceleration_time = 200 #加減速時間[mS]
polarizer.set_speed(spd_min, spd_max, acceleration_time)
```

### ジョグ運転
ステージを連続で回転させることができます．
```python
polarizer.jog() #+方向に回転
time.sleep(1) #1秒待つ
polarizer.stop() #ステージ停止

polarizer.jog(reverse=True)　#-方向に回転
time.sleep(1) #1秒待つ
polarizer.stop() #ステージ停止
```

### 移動中に別の動作を行う
`reset`や`degree`でのステージの移動において，デフォルトでは移動が完了するまで待つ処理を行っています．移動中にも別の処理を行いたい場合は，メンバ変数`is_sleep_until_stop`を`False`に設定してください．
```python
polarizer.is_sleep_until_stop = False #移動完了を待つフラグをFalseにする
polarizer.degree = 180 #移動開始（移動完了を待たずに次の処理に行く）
"""ここに移動中に行う処理を書く"""
polarizer.sleep_until_stop() #明示的に移動完了を待つ
```
