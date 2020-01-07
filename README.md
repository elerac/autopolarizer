# Automatic Polarizer

ツクモ工学の[自動偏光子ホルダー(PWA-100)](http://www.twin9.co.jp/product/holders-list/mirror-list-2-2/pwa-100/)をシグマ光機の[1軸ステージコントローラ(GSC-01)](https://www.global-optosigma.com/jp/Catalogs/pno/?from=page&pnoname=GSC-01&ccode=W9042&dcode=)を通して，Pythonで制御します．

## Usage
### Run on command line
```
python automaticpolarizer.py <degree>
```
偏光板を指定した角度`degree`に回転させます．シリアルポート名は`/dev/tty.usbserial-FTRWB1RN`がデフォルトになっています．変更する場合は，`--port`オプションで指定してください．

### Use as a module
