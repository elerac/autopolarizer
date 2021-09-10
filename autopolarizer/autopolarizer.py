"""自動偏光子ホルダーをPythonで制御する

コントローラー:
    OptoSigma,  GSC-01  (シグマ光機，1軸ステージコントローラ GSC-01)
偏光子ホルダー:
    TWIN NINES, PWA-100（ツクモ工学，自動偏光子ホルダーφ100用 PWA-100）

Notes
-----
ツクモ光学の自動偏光子ホルダーは，シグマ光機の1軸ステージコントローラから動かすことが出来ます．
このステージコントローラをコンピュータから動かすには，シリアル通信(UART)と呼ばれる非同期な通信で命令コマンドを送信します．
シリアル通信は古くから使われており，RS-232Cといった専用のインタフェースが必要になります．最近のコンピュータでは，このインタフェースを搭載しているものはほとんどありません．そのため，USBからRS-232Cに変換するアダプタを使用します．
シリアル通信を実行する方法はいくつかありますが，pythonから実行する場合はpySerial(https://github.com/pyserial/pyserial)を利用するのが良いと思います．
このプログラムは，主要な命令コマンドを送信するために，直感的に扱いやすいラッパーを提供しています．

References
----------
.. [1] http://www.twin9.co.jp/product/holders-list/mirror-list-2-2/pwa-100/
.. [2] https://www.global-optosigma.com/jp/Catalogs/pno/?from=page&pnoname=GSC-01&ccode=W9042&dcode=
"""
import time
import serial


class AutoPolarizer(serial.Serial):
    """自動偏光子ホルダーに命令を送信する

    Parameters
    ----------
    引数は全てpyserialのserial.Serial()の引数と同じ
    https://pyserial.readthedocs.io/en/latest/pyserial_api.html#serial.Serial

    Attributes
    ----------
    is_sleep_until_stop : bool
        ステージを動かしたときに待つかのフラグ
    flip_front : bool
        ステージの向きを反転させるかどうかのフラグ
        向きによって回転角度が反転するため，このフラグで補正する

    Methods
    -------
    raw_command(cmd)
        コントローラにコマンドを送信
    reset()
        機械原点復帰命令を送信
    jog_plus()
        +方向にジョグ運転
    jog_minus()
        -方向にジョグ運転
    stop(immediate=False)
        停止命令を送信
    is_stopped()
        ステージが停止しているかを取得
    sleep_until_stop()
        ステージが停止するまで待つ
    set_speed(spd_min=500, spd_max=5000, acceleration_time=200)
        速度設定命令を送信
    """

    # ステージを動かしたときに待つかどうかのフラグ
    is_sleep_until_stop = True

    # ステージの向きを反転させるかどうかのフラグ
    # 向きによって回転角度が反転するため，このフラグで補正する
    flip_front = False

    @property
    def degree_per_pulse(self):
        """1パルスで移動する角度（固定値）"""
        return 0.060  # [deg/pulse]

    def __del__(self):
        """ステージとのシリアル接続を終了"""
        try:
            self.close()
        except AttributeError:
            pass

    def raw_command(self, cmd):
        """コントローラにコマンドを送信

        基本的には直接呼び出さない．
        成功すると"OK"，失敗すると"NG"がコントローラ側から送られてくる．
        そこで，"OK"はTrue，"NG"はFalseと変換して返す．
        例外として，"OK"や"NG"以外の文字列が送られてきた場合は，そのままの文字列を返す．

        Parameters
        ----------
        cmd : str
            コマンドの内容は，GSC-01の取扱説明書を参考にすること．

        Returns
        -------
        ret : bool or str
            OKなら``True``
            NGなら``False``
        """
        self.write(cmd.encode())
        self.write(b"\r\n")
        return_msg = self.readline().decode()[:-2]  # -2: 文字列に改行コードが含まれるため，それ以外を抜き出す．
        return (
            True
            if return_msg == "OK" 
            else False 
            if return_msg == "NG" 
            else return_msg
        )

    def reset(self):
        """機械原点復帰命令を送信"""
        ret = self.raw_command("H:1")
        if self.is_sleep_until_stop:
            self.sleep_until_stop()
        return ret

    def jog_plus(self):
        """+方向にジョグ運転を行います．
        実行すると動き続けるので，停止する場合は停止命令（stop()）を実行してください．
        """
        ret = self.raw_command("J:1+")
        if ret:
            return self.raw_command("G:")
        else:
            return False

    def jog_minus(self):
        """-方向にジョグ運転

        実行すると動き続けるので，停止する場合は停止命令（stop()）を実行してください．
        """
        ret = self.raw_command("J:1-")
        if ret:
            return self.raw_command("G:")
        else:
            return False

    def stop(self, immediate=False):
        """停止命令を送信

        停止命令には，減速停止命令と即停止命令があります．
        引数immediateでどちらを実行するか指定出来ます（通常使用では減速停止命令で良いと思います）．

        Parameters
        ----------
        immediate : bool
            Falseなら減速停止命令
            Trueなら即停止命令
        """
        return (
            self.raw_command("L:1") 
            if immediate == False 
            else self.raw_command("L:E")
        )

    def is_stopped(self):
        """ステージが停止しているかを取得

        Returns
        -------
        ret : bool
            Ready状態（停止）の場合は``True``
            Busy 状態（動作中）の場合は``False``
        """
        return_msg = self.raw_command("!:")
        return (
            True
            if return_msg == "R"
            else False  # Ready
            if return_msg == "B"
            else return_msg  # Busy
        )

    def sleep_until_stop(self):
        """ステージが停止するまで待つ"""
        while not self.is_stopped():
            time.sleep(0.01)

    def set_speed(self, spd_min=500, spd_max=5000, acceleration_time=200):
        """速度設定命令を送信

        速度には3つのパラメータがあり，全て一括で設定します．

        Parameters
        ----------
        spd_min : int
          最小速度
          設定範囲：100～20000（単位：PPS）
        spd_max : int
          最大速度
          設定範囲：100～20000（単位：PPS）
        acceleration_time : int
          加減速時間
          設定範囲：0～1000（単位：mS）

        Notes
        -----
        最大速度は必ず最小速度以上の値を設定
        速度の設定は 100[PPS]単位、100[PPS]未満の値は切り捨て
        """
        clip = lambda v, v_min, v_max: max(v_min, min(v_max, v))
        spd_max = max(spd_max, spd_min)  # 最大速度は必ず最小速度以上の値を設定
        spd_min = clip(int(spd_min), 100, 20000)
        spd_max = clip(int(spd_max), 100, 20000)
        acceleration_time = clip(int(acceleration_time), 0, 1000)
        return self.raw_command(f"D:1S{spd_min}F{spd_max}R{acceleration_time}")

    @property
    def degree(self):
        """現在のステージの回転角度を返す"""
        deg = self._position2degree(self._get_position())
        if self.flip_front:
            deg = 360 - deg
        return deg

    @degree.setter
    def degree(self, deg_dst):
        """ステージを指定した角度に動かす

        Parameters
        ----------
        deg_dst : float
          移動させる角度（絶対位置）

        Notes
        -----
        ステージを回転させる際，回転方向を限定させています．一方の方向にしか回転せず逆方向には回転しません．．
        このような仕様にしているのは，ステージにリミットセンサがあるためです．リミットセンサを検出した場合，ステージは強制的に停止します．この強制停止には回転方向依存があり，停止する方向と，しない方向があります．
        強制停止はさせたくないので，リミットセンサに引っかからない方向だけに，回転するようにしています．
        """
        deg_src = self.degree
        deg_dst %= 360
        if self.flip_front:
            deg_src = 360 - deg_src
            deg_dst = 360 - deg_dst
        position = self._degree2position((deg_dst - deg_src) % 360)
        self._set_position_relative(position)

    def _set_position_relative(self, position):
        """相対移動パルス数設定命令と駆動命令を実行

        Parameters
        ----------
        position : int
          ステージ位置（移動パルス数）
        """
        sign = "+" if position >= 0 else "-"
        ret = self.raw_command("M:1" + sign + "P" + str(abs(position)))
        if ret == False:
            return False

        ret = self.raw_command("G:")
        if self.is_sleep_until_stop:
            self.sleep_until_stop()
        return ret

    def _set_position_absolute(self, position):
        """絶対移動パルス数設定命令と駆動命令を実行

        Parameters
        ----------
        position : int
          ステージ位置（移動パルス数）
        """
        sign = "+" if position >= 0 else "-"
        ret = self.raw_command("A:1" + sign + "P" + str(abs(position)))
        if ret == False:
            return False

        ret = self.raw_command("G:")
        if self.is_sleep_until_stop:
            self.sleep_until_stop()
        return ret

    def _get_position(self):
        """ステータス確認1命令を実行し，現在の座標値を取得

        Notes
        -----
        失敗することがあったので，tryで回避するようにしてforで何度か見るようにしています．
        """
        for i in range(5):
            return_msg = self.raw_command("Q:")
            try:
                return int(return_msg.split(",")[0].replace(" ", ""))
            except:
                continue

    def _degree2position(self, deg):
        """角度（度）からステージ位置（移動パルス数）に変換

        Parameters
        ----------
        deg : float
          角度（度）
        """
        return int(deg / self.degree_per_pulse)

    def _position2degree(self, position):
        """ステージ位置（移動パルス数）から角度（度）に変換

        Parameters
        ----------
        position : int
          ステージ位置（移動パルス数）
        """
        return (position % (360.0 / self.degree_per_pulse)) * self.degree_per_pulse


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "degree", 
        type=int, 
        help="angle of polarizer [deg]"
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default="/dev/tty.usbserial-FTRWB1RN",
        help="srial port name",
    )
    parser.add_argument(
        "-r",
        "--reset",
        action="store_true",
        help="determines whether to perform a reset",
    )
    args = parser.parse_args()

    # command line arguments
    port = args.port
    deg = args.degree
    is_reset = args.reset

    # connect to the polarizer
    polarizer = AutoPolarizer(port=port)

    # set speed as default
    polarizer.set_speed()

    # reset (if required)
    if is_reset:
        polarizer.reset()

    # rotate the polarizer
    polarizer.degree = deg


if __name__ == "__main__":
    main()
    