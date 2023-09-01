import sys


class Logs2File(object):
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout

    def __del__(self):
        self.close()

    def write(self, data):
        self.stdout.write(data)
        self.file.write(data)

    def flush(self):
        self.stdout.flush()
        self.file.flush()

    def close(self):
        if sys.stdout is self:
            sys.stdout = self.stdout
        self.file.close()
