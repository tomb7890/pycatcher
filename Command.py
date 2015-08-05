
import argparse

args = None

def init_args():
    global args
    _parser = getparser()
    args = _parser.parse_args()

def getparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--program', dest='program',
                        action='store',help='program x')
    parser.add_argument('-d', '--debug',  action='store_true')
    parser.add_argument('-r', '--report', action='store_true' )
    parser.add_argument('--localrss', action='store_true',
                        default=False )
    return parser
