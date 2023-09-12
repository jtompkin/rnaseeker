#! /usr/bin/env python3
import argparse

from gene_ontology import go_filter


def main():
    parser = argparse.ArgumentParser(prog='RNAseq', description='RANseq scripts and libraries')

    subparsers = parser.add_subparsers(required=True)

    parser_gofilter = subparsers.add_parser('gofilter')
    parser_gofilter.set_defaults(func=go_filter.main)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
