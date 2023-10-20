import pexpect
import pyte

KEY_UP = '\x1b[A'
KEY_DOWN = '\x1b[B'
KEY_RIGHT = '\x1b[C'
KEY_LEFT = '\x1b[D'

class UlTelnet:
    def __init__(self):
        self.ult = None

        self.screen = pyte.Screen(70, 24)
        self.stream = pyte.Stream(self.screen)

        self.before = None
        self.after = None

    def open(self, args):
        """
        Opens a telnet session
        :param args: arguments to the telnet command (typically the address)
        """
        self.ult = pexpect.spawn("telnet {}".format(args))

    def run_disk(self, image_name):
        """
        Runs a disk image
        :param image_name: name of the image to run, including extension
        """
        self.expect_screen_draw()
        loc = self.find_on_screen("USB DISK")
        for _ in range(0, loc - 3):
            self.ult.send(KEY_DOWN)
        self.expect_white_text("USB DISK")

        self.ult.sendcontrol('m')
        self.ult.sendcontrol('m')
        self.expect("/Usb0/")

        self.expect_screen_draw()
        loc = self.find_on_screen(image_name)
        for _ in range(0, loc - 3):
            self.ult.send(KEY_DOWN)
        self.ult.sendcontrol('m')
        self.ult.send(KEY_DOWN)
        self.ult.sendcontrol('m')

        self.expect_screen_draw()
        self.ult.sendcontrol('[')
        self.consume_to_timeout()

    def expect(self, re):
        """
        Expects the given regular expression and updates the virtual screen
        :param re: regular expression to expect
        """
        self.ult.expect(re)
        self._feed()

    def expect_screen_draw(self):
        """
        Expects a full screen draw
        """
        self.expect("\[23;1H.{60}")  # move to 23,1

    def expect_white_text(self, text):
        """
        Expects the given text to appear in white
        :param text: text to expect
        """
        self.expect(r"\[0;37;1m[\s\w]+" + text)

    def consume_to_timeout(self, timeout=1):
        """
        Consumes all text until the given timeout
        :param timeout: timeout in seconds
        """
        self.ult.expect(pexpect.TIMEOUT, timeout=1)
        self._feed()

    def find_on_screen(self, string):
        """
        Finds the given string on the virtual screen
        :param string: string to find
        :return: location of the string as a line number starting from 1
        :raises RuntimeError if the string is not found
        """
        loc = None
        for idx, line in enumerate(self.screen.display, 1):
            if string in line:
                return idx

        self._troubleshoot()
        raise RuntimeError("'{}' not found on current screen".format(string))

    def _feed(self):
        """
        Updates the virtual screen based on data captured from the Ultimate device.
        Should be called after every "expect" on the Ultimate.
        """
        self.before = self.ult.before
        self.stream.feed(self.before.decode("ISO-8859-1"))
        self.after = self.ult.after
        if self.after not in (pexpect.TIMEOUT, pexpect.EOF):
            self.stream.feed(self.after.decode("ISO-8859-1"))

    def _troubleshoot(self):
        """
        Show troubleshooting information
        """
        print("LAST 'BEFORE':")
        print(self.before)

        print("LAST 'AFTER':")
        print(self.after)

        print("VIRTUAL SCREEN:")
        for idx, line in enumerate(self.screen.display, 1):
            if line.strip():
                print("{0:2d} {1} ¶".format(idx, line))
