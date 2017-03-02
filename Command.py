import argparse


class Args:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state

    def parse(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbose', action='store_true')
        parser.add_argument('-p', '--program', dest='program',
                            action='store',help='program x')
        parser.add_argument('-lr', '--limit-rate', dest='limitrate',
                            action='store', help='limitrate')
        parser.add_argument('-d', '--debug',  action='store_true')
        parser.add_argument('-r', '--report', action='store_true')
        parser.add_argument('-f', '--refresh', action='store_true')
        parser.add_argument('--localrss',
                            action='store_true',  default=False )
        self.parser = parser.parse_args(args)
