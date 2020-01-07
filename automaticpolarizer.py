import serial

"""
    Control the automatic polarizer holder with Python
    （自動偏光子ホルダーをPythonで制御する）

    controller:       OptoSigma,  GSC-01  (シグマ光機，1軸ステージコントローラ GSC-01)
    polarizer holder: TWIN NINES, PWA-100（ツクモ工学，自動偏光子ホルダーφ100用 PWA-100）
"""

class AutomaticPolarizer:
    def __init__(self, port=None, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None):
        self.ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout, xonxoff, rtscts, write_timeout, dsrdtr, inter_byte_timeout)
        
        self.degree_per_pulse = 0.060 #[deg/pulse]
        self.is_sleep_until_stop = True

    def __del__(self):
        try:
            self.ser.close()
        except AttributeError:
            pass
    
    def raw_command(self, cmd):
        self.ser.write(cmd.encode())
        self.ser.write(b"\r\n")
        return_msg = self.ser.readline().decode()[:-2]
        return (True  if return_msg=="OK" else
                False if return_msg=="NG" else
                return_msg)

    def reset(self):
        ret = self.raw_command("H:1")
        if self.is_sleep_until_stop: self.sleep_until_stop()
        return ret
    
    def stop(self, immediate=False):
        return (self.raw_command("L:1") if immediate==False else
                self.raw_command("L:E"))

    def is_stopped(self):
        return_msg = self.raw_command("!:")
        return (True  if return_msg=="R" else #Ready
                False if return_msg=="B" else #Busy
                return_msg)

    def sleep_until_stop(self):
        while not self.is_stopped(): pass
    
    def set_speed(self, spd_min=500, spd_max=5000, acceleration_time=200):
        return self.raw_command("D:1S{0}F{1}R{2}".format(spd_min, spd_max, acceleration_time))
        
    @property
    def degree(self):
        return self._position2degree(self._get_position())

    @degree.setter
    def degree(self, deg_dst):
        deg_src = self.degree
        deg_dst %= 360
        position = self._degree2position((deg_dst-deg_src)%360)
        self._set_position_relative(position)
    
    def _set_position_relative(self, position):
        sign = "+" if position>=0 else "-"
        ret = self.raw_command("M:1"+sign+"P"+str(abs(position)))
        if ret==False: return False
        ret = self.raw_command("G:")
        if self.is_sleep_until_stop: self.sleep_until_stop()
        return ret
    
    def _set_position_absolute(self, position):
        sign = "+" if position>=0 else "-"
        ret = self.raw_command("A:1"+sign+"P"+str(abs(position)))
        if ret==False: return False
        ret = self.raw_command("G:")
        if self.is_sleep_until_stop: self.sleep_until_stop()
        return ret
    
    def _get_position(self):
        for i in range(5):
            return_msg = self.raw_command("Q:")
            try: return int(return_msg.split(",")[0].replace(" ", ""))
            except: continue

    def _degree2position(self, deg):
        return int(deg/self.degree_per_pulse)

    def _position2degree(self, position):
        return (position%(360.0/self.degree_per_pulse)) * self.degree_per_pulse

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("degree", type=int, help="polarizer angle [deg]")
    parser.add_argument("-p", "--port", type=str, default="/dev/tty.usbserial-FTRWB1RN", help="srial port name")
    parser.add_argument("-r", "--reset", action="store_true", help="determines whether to perform a reset")
    args = parser.parse_args()
    
    #command line arguments
    port = args.port
    deg = args.degree
    is_reset = args.reset

    #connect to the polarizer
    polarizer = AutomaticPolarizer(port=port)
    
    #set speed as default
    polarizer.set_speed()
    
    #reset (if required)
    if is_reset:
        polarizer.reset()
    
    #rotate the polarizer
    polarizer.degree = deg
    
    #explicit disconnect request
    del polarizer
    
if __name__=="__main__":
    main()
