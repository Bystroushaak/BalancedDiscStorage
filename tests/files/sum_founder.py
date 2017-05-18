#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import argparse

import sh


# Functions & classes =========================================================
def _forever_gen():
    cnt = 0
    while True:
        yield cnt
        cnt += 1


def look_for_hash(filename, startswith, number):
    found = 0
    for cnt in _forever_gen():
        with open(filename, "w") as f:
            f.write(str(cnt))

        file_hash = sh.sha256sum(args.filename).split()[0]

        if file_hash.startswith(startswith):
            found += 1
            print(file_hash, cnt)

            if found == number:
                break

    if number != 1:
        sh.rm(filename)


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
    parser.add_argument(
        "-n",
        "--number",
        default=1,
        type=int,
        help="Number of hashes which should be found. Default 1."
    )
    args = parser.parse_args()

    look_for_hash(
        filename=args.filename,
        startswith=args.startswith,
        number=args.number,
    )
