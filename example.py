import time
from autopolarizer import AutoPolarizer


def main():
    port = "/dev/tty.usbserial-FTRWB1RN"
    polarizer = AutoPolarizer(port)
    polarizer.stop()

    print("polarizer.reset()")
    polarizer.reset()
    time.sleep(1)

    print("polarizer.degree = 180")
    polarizer.degree = 180
    print(f">>> {polarizer.degree}\n")

    for i in range(4):
        print("polarizer.degree += 45")
        polarizer.degree += 45
        print(f">>> {polarizer.degree}\n")

    time.sleep(1)

    print("polarizer.jog_plus()")
    polarizer.jog_plus()
    time.sleep(1)
    polarizer.stop()

    print("polarizer.jog_minus()")
    polarizer.jog_minus()
    time.sleep(1)
    polarizer.stop()


if __name__ == "__main__":
    main()
