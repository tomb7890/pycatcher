import argparse

def argparser(x=None):

    p = argparse.ArgumentParser()
    p.add_argument('-v', '--verbose', action='store_true')
    p.add_argument('-p', '--program', dest='program',
                        action='store',help='program x')
    p.add_argument('-lr', '--limit-rate', dest='limitrate',
                        action='store', help='limitrate')
    p.add_argument('-d', '--debug',  action='store_true')
    p.add_argument('-r', '--report', action='store_true')
    p.add_argument('-f', '--refresh', action='store_true')
    p.add_argument('-sp', '--strict-parsing',
                        action='store_true',  default=True,
                        help = """
                        Allow blank lines to appear in header of RSS file
                        """)

    p.add_argument('-s', '--search', dest='search', action='store',help='Search iTunes for a podcast')
    p.add_argument('-x', '--subscribe', nargs=2, dest='subscribe', action='store',help='Subscribe to a podcast')
    p.add_argument('-c', '--config', dest='configfile', action='store',help='Set alternate config file ')

    if x:
        return p.parse_args(x.split())
    else:
        return p

if __name__ == '__main__':
    main()
