#!/usr/bin/env python3
"""
Parse a simple list of domains and check which one is not being blocked by the DNS
"""

import os
import sys
import socket
import argparse


def get_domains(filename) -> list:
    if os.path.exists(filename):
        try:
            domains_file = open(filename, 'r')
            _domains = [j.rstrip() for j in domains_file.readlines()]
            return [j.replace(' ', '') for j in _domains]
        except (IOError, ValueError, EOFError) as error:
            sys.exit(error)
    else:
        sys.exit("{filename}: File not found")


def main() -> None:
    parser = argparse.ArgumentParser(usage="%(prog)s [options]")
    parser.add_argument('domains_file',
                        metavar='<domains_file>',
                        help='Input file containing the domains to check (one \
                              domain per line)')

    parser.add_argument('--show-failures',
                        dest='show_failures',
                        required=False,
                        action="store_true",
                        help='Do not print domain which failed to resolve')

    args = parser.parse_args()

    _domains = get_domains(args.domains_file)

    for domain in _domains:
        if len(domain) == 0 or domain[0] == '#':
            continue

        try:
            if socket.gethostbyname(domain) != '127.0.0.1':
                print(f"'{domain}' not blocked")
        except socket.gaierror:
            if args.show_failures:
                print(f"'{domain}': resolution failed")
        except:
            print(f"An error occured while resolving '{domain}'")


if __name__ == "__main__":
    main()
