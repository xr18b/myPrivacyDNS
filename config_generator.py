#!/usr/bin/env python3

import sys
import yaml
import argparse
from os.path import exists


def get_config(filename):
    try:
        config_file = open(filename, 'r')
        try:
            return yaml.load(config_file, Loader=yaml.FullLoader)
        except yaml.YAMLError as error:
            sys.exit("Error while reading YAML data:\n" + str(error) + "\nAborting...")
    except (IOError, ValueError, EOFError) as error:
        sys.exit(error)


def get_template(filename):
    try:
        template = open(filename, 'r')
        return template.read()
    except (IOError, ValueError, EOFError) as error:
        sys.exit(error)


def get_static_mapping(config):
    # Generate the static mapping list
    RETURN_TEXT = "\n;\n; Static mappings\n;"

    processedRecords = []

    for mapping in config:

        if mapping['host'] in processedRecords:
            continue

        processedRecords.append(mapping['host'])

        if "ipv4" in mapping:
            for address in mapping['ipv4']:
                RETURN_TEXT += "\n" + mapping['host'].ljust(50) + " IN A     " + address
        else:
            sys.exit("No ipv4 specified for static mapping '%s'\nAborting..." % mapping['host'])

        if "ipv6" in mapping:
            for address in mapping['ipv6']:
                RETURN_TEXT += "\n" + mapping['host'].ljust(50) + " IN AAAA  " + address

    return RETURN_TEXT


def get_blocking_records(config):
    # Generating the static records for the blocking destination
    BLK_DST_NAME = config['destination']['name']
    RETURN_TEXT = "\n;\n; Static records for the blocking destination\n;"

    if "ipv4" in config['destination']:
        for address in config['destination']['ipv4']:
            RETURN_TEXT += "\n" + BLK_DST_NAME.ljust(50) + " IN A     " + address
    else:
        sys.exit("No ipv4 specified for blocking destination (%s)\nAborting..." % BLK_DST_NAME)

    if "ipv6" in config['destination']:
        for address in config['destination']['ipv6']:
            RETURN_TEXT += "\n" + BLK_DST_NAME.ljust(50) + " IN AAAA  " + address

    if 'domain_list' in config and config['domain_list'] is not None:
        # Generating the blocking list
        RETURN_TEXT += "\n;\n; Blocking list\n;"

        processedRecords = []

        for domain in config['domain_list']:
            if domain['name'] in processedRecords:
                continue

            processedRecords.append(domain['name'])

            RETURN_TEXT += "\n" + domain['name'].ljust(50) + " IN CNAME " + BLK_DST_NAME
            if not ("include_sub" in domain) or domain['include_sub'] is True:
                RETURN_TEXT += "\n" + "*." + domain['name'].ljust(48) + " IN CNAME " + BLK_DST_NAME

    return RETURN_TEXT


def main() -> None:
    parser = argparse.ArgumentParser(usage="%(prog)s [options]")
    parser.add_argument('config_file', # Name of the variable where value is stored
                        metavar='<config_file>', # Name of the argument in usage message
                        help='Input YAML file to generate the configuration from')

    parser.add_argument('template',
                        metavar='<template_file>',
                        help='Template to use to generate the configuration')

    parser.add_argument('-o', '--output-file',
                        dest='outfile',
                        required=False,
                        help='Specify a file to write the configuration to')

    parser.add_argument('-f', '--force',
                        dest='override',
                        required=False,
                        action="store_true",
                        help='When writing to an output file, override it if already exists')

    args = parser.parse_args()
    
    config = get_config(args.config_file)

    OUTPUT_TEXT = """;
; BIND zone file for blocking list
;
; DO NOT EDIT THIS FILE - It is managed by 'myPrivacyDNS' tools
;
"""

    OUTPUT_TEXT += get_template(args.template)

    if 'static_mapping' in config and config['static_mapping'] is not None:
        OUTPUT_TEXT += get_static_mapping(config['static_mapping'])

    if 'blocking' in config and config['blocking'] is not None:
        OUTPUT_TEXT += get_blocking_records(config['blocking'])

    if args.outfile is None:
        print(OUTPUT_TEXT)

    else:
        if exists(args.outfile) and not args.override:
            print(args.outfile + ": File already exists. Use '-f' flag to override")
            return 1

        try:
            with open(args.outfile, "w") as f:
                f.writelines(OUTPUT_TEXT)
        except PermissionError:
            print(args.outfile + ': Permission denied')
        except IsADirectoryError:
            print(args.outfile + ': Is a directory')
        except IOError as x:
            print(args.outfile + ': Unknown Error - ', x)

    return 0


if __name__ == "__main__":
    main()

