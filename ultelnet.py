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

        # Saved for debugging
        self.before = None
        self.after = None

    def open(self, args):
        """
        Opens a telnet session
        :param args: arguments to the telnet command (typically the address)
        """
        self.ult = pexpect.spawn("telnet {}".format(args))

    def enter_usb(self):
        """
        Enters the USB disk.
        Assumes that we're at the main menu.
        """
        self.down_to_string("USB DISK", 3)
        self.expect_white_text("USB DISK")

        self.ult.sendcontrol('m')
        self.ult.sendcontrol('m')
        self.expect("/Usb0/")

    def run_disk(self, image_name):
        """
        Runs a disk image
        :param image_name: name of the image to run, including extension
        """
        self.enter_usb()

        self.expect_screen_draw()
        self.down_to_string(image_name, 3)
        self.ult.sendcontrol('m')
        self.ult.send(KEY_DOWN)
        self.ult.sendcontrol('m')

        self.expect_screen_draw()
        self.ult.sendcontrol('[')
        self.consume_to_timeout()

    def setup_printer(self, dir_name):
        """
        Sets up the virtual printer
        :param dir_name: directory for print jobs (in root of Usb0), must exist
        """
        self.expect_screen_draw()
        self.enter_usb()
        self.expect_screen_draw()
        self.down_to_string(dir_name, 3)
        self.ult.sendcontrol('m')
        self.ult.sendcontrol('m')

        self.action_software_iec()

        self.expect("Set dir. here")
        self.down_to_string("Set dir. here", 10)
        self.ult.sendcontrol('m')

        self.action_software_iec()

        self.ult.sendcontrol('m')
        self.expect_screen_draw()
        self.ult.sendcontrol('m')
        self.expect_screen_draw()

        self.send_esc_sequence('[D')   # left arrow
        self.expect_screen_draw()
        self.send_esc_sequence('[D')   # left arrow
        self.send_esc_sequence('[5~')  # pgup
        self.consume_to_timeout()

    def action_software_iec(self):
        """
        Run the action menu and choose the "Software IEC" option
        """
        self.expect_screen_draw()
        self.send_esc_sequence('[15~')  # F5
        self.expect("Software IEC")
        self.down_to_string("Software IEC", 8)
        self.ult.sendcontrol('m')

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

        TODO: scroll down when string is not found

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

    def down_to_string(self, string, start_pos):
        """
        Scrolls down to the given string

        :param string: string to scroll to
        :param start_pos: starting screen line (1-based)
        """
        loc = self.find_on_screen(string)
        for _ in range(0, loc - start_pos):
            self.ult.send(KEY_DOWN)

    def send_esc_sequence(self, sequence):
        """
        Sends an escape sequence (ESC followed by a string)
        :param sequence: sequence to send after ESC
        """
        self.ult.sendcontrol('[')
        self.ult.send(sequence)

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
