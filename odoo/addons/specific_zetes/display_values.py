#!/usr/bin/python
import getopt
import sys

import requests


def main(argv):
    """
    !!! This script is use only for tests !!!!
    This script will create a request on locahost:8069/display_values
    to display the format of a request.
    I created this method only to easily retrieve a structure of request
    without create a GET request.

    Usage: display_values.py -d <domains> -a <actions>
    -d | --domains : A list (separated by comma) of domains (assignment, ...)
    -a | --actions : A list (separated by comma) of actions (requ,resu)

    Example:
    display_values.py --domains=catchweight,assignment
    :param argv:
    :return:
    """
    domains = None
    actions = None
    try:
        # Format args
        opts, args = getopt.getopt(argv, "hd:a:", ["domains=", "actions="])
    except getopt.GetoptError:
        print "display_values.py -d <domains> -a <actions>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print "display_values.py -i <domains> -o <actions>"
            sys.exit()
        elif opt in ("-d", "--domains"):
            domains = arg
        elif opt in ("-a", "--actions"):
            actions = arg

    data = {"domains": domains, "actions": actions}

    result = requests.get("http://localhost:8069/display_values", data=data)
    print result.content


if __name__ == "__main__":
    main(sys.argv[1:])
