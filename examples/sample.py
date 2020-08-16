from autopolarizer import *
import time

def main():
    port = "/dev/tty.usbserial-FTRWB1RN"
    polarizer = AutoPolarizer(port)
    
    print("Reset")
    polarizer.reset()

    time.sleep(1)
    
    print("jog+")
    polarizer.jog_plus()
    time.sleep(1)
    print("jog-")
    polarizer.jog_minus()
    time.sleep(1)
    
    polarizer.stop()
    time.sleep(1)
    
    print("Set speed as default")
    polarizer.set_speed()

    print("Rotate +45")
    for i in range(8):
        polarizer.degree += 45
        print("\t", polarizer.degree)

    time.sleep(1)

    print("Set speed faster")
    polarizer.set_speed(500, 10000, 200)
    
    print("Rotate +45")
    for i in range(8):
        polarizer.degree += 45
        print("\t", polarizer.degree)

if __name__=="__main__":
    main()
