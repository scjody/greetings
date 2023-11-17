import os
import subprocess

from PIL import Image

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
    bn = os.path.basename(path)
    new_fn = "/Users/scjody/Downloads/prints/transformed/{}".format(bn)
    transform(path, new_fn)

    print("printing with lasers...")
    subprocess.run(["lpr", new_fn])

    ftp.quit()
    tel.quit()


def transform(fn, new_fn):
    im = Image.open(fn)
    print(fn)

    if has_non_white_pixel_in_region(im, 0, 2150, im.size[0], im.size[1]):
        print("  print shop detected, cropping")
        box = (31, 263, 1951, 2233)
    elif has_non_white_pixel_in_region(im, 0, 0, im.size[0], 250):
        print("  print master detected, cropping")
        box = (39, 200, 1943, 2140)
    else:
        print("  i don't know what this is, cropping cautiously")
        box = (31, 209, 1951, 2233)

    cropped = im.crop(box)
    stretched = cropped.resize((cropped.width, 2500))
    stretched.save(new_fn)


def has_non_white_pixel_in_region(image, left, top, right, bottom):
    for y in range(top, bottom):
        for x in range(left, right):
            pixel = image.getpixel((x, y))
            if pixel != 0:
                return True
    return False
