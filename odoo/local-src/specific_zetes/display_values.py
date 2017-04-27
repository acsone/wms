#!/usr/bin/python
import sys
import getopt
import requests


def main(argv):
    domains = None
    actions = None
    try:
        opts, args = getopt.getopt(argv, "hd:a:", ["domains=", "actions="])
    except getopt.GetoptError:
        print 'display_values.py -d <domains> -a <actions>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'display_values.py -i <domains> -o <actions>'
            sys.exit()
        elif opt in ("-d", "--domains"):
            domains = arg
        elif opt in ("-a", "--actions"):
            actions = arg

    data = {
        'domains': domains,
        'actions': actions,
    }

    result = requests.get('http://localhost:8069/display_values',
                          data=data)
    print result.content


if __name__ == "__main__":
    main(sys.argv[1:])
