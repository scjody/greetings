from ultelnet import UlTelnet


def load_print_shop():
    tel = UlTelnet()
    tel.open("c64")
    print("setting up printer...")
    tel.setup_printer("prints")
    print("loading print shop...")
    tel.run_disk("print shop.d64")

    tel.quit()


def load_print_master():
    tel = UlTelnet()
    tel.open("c64")

    print("setting up printer...")
    tel.setup_printer("prints")

    print("loading print master...")
    tel.mount_disk_on_b("print master-d2.d64")

    tel.quit()
    tel.open("c64")

    tel.expect_screen_draw()
    print("Press SPACE to continue loading when you see the scrolly text")
    tel.run_disk("print master-d1.d64")

    tel.quit()