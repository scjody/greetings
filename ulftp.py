from ftplib import FTP
from os.path import splitext
from tempfile import NamedTemporaryFile

class UlFtp:
    def __init__(self):
        self.ftp = None

    def open(self, addr):
        self.ftp = FTP(addr)
        self.ftp.login()

    def get_latest(self, dir=None):
        """
        Gets the latest printer file from the U2 to a tempfile in the given directory

        :param dir: directory to save files to (None to use a default temp directory)

        :return: path to the tempfile
        """
        tf = NamedTemporaryFile(suffix=".png", delete=False, dir=dir)
        self.ftp.cwd("/Usb0")

        latest_n = 0
        latest_filename = None
        for filename, facts in self.ftp.mlsd():
            if filename.startswith("printer-"):
                try:
                    n = int(splitext(filename)[0].split("-")[1])
                except ValueError:
                    continue

                if n > latest_n:
                    latest_n = n
                    latest_filename = filename

        print("  retrieving {} to {}".format(latest_filename, tf.name))
        self.ftp.retrbinary("RETR {}".format(latest_filename), tf.write)

        self.ftp.quit()

        return tf.name
