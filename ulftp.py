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

    def get_file(self, filename):
        """
        Gets the given file from /Usb0, and saves to the current local directory
        :param filename: filename, including extension
        """
        self.ftp.cwd("/Usb0")
        tf = open(filename, "wb")
        self.ftp.retrbinary("RETR {}".format(filename), tf.write)

        self.ftp.quit()

    def send(self, filepath, filename):
        """
        Sends the given file to /Usb0 root
        :param filepath: path to local file
        :param filename: remote filename
        """
        self.ftp.cwd("/Usb0")
        fp = open(filepath, 'rb')

        self.ftp.storbinary("STOR {}".format(filename), fp)

        self.ftp.quit()
