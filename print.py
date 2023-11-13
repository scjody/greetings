import subprocess

from ulftp import UlFtp
from ultelnet import UlTelnet


def print_latest():
    ADDR = "c64"

    tel = UlTelnet()
    tel.open(ADDR)
    ftp = UlFtp()
    ftp.open(ADDR)

    print("crawling into virtual printer...")
    tel.flush_printer()

    print("getting printer file...")
    path = ftp.get_latest_printer_file("/Users/scjody/Downloads/prints")

    subprocess.run(["imgcat", path])

    print("folding space and time...")
    # TODO: transform image

    print("printing with laser eyes...")
    # TODO: print!

    tel.quit()

