#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import argparse

import sh


# Functions & classes =========================================================
def look_for_hash(filename, startswith):
    for cnt in xrange(99999999999999999):
        with open(filename, "w") as f:
            f.write(str(cnt))

        file_hash = sh.sha256sum(args.filename)

        if file_hash.startswith(startswith):
            print file_hash
            break


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""Write into file until you found the file with hash wich s\
    tarts with given character."""
    )
    parser.add_argument(
        "-s",
        "--startswith",
        required=True,
        help="String with which the hash should start."
    )
    parser.add_argument(
        "-f",
        "--filename",
        default="file.txt",
        help="Name of the file which will be checked. Default `file.txt`."
    )
    args = parser.parse_args()

    look_for_hash(
        filename=args.filename,
        startswith=args.startswith
    )
