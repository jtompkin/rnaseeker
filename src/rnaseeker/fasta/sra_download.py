#!/usr/bin/env python3
import argparse
import sys
import os


def download_sras(start: int, end: int, include: bool = True):
    for i in range(start, end + include):
        accession = f"SRR{i}"
        print(accession)


def main(args: list[str] | None = None):
    parser = argparse.ArgumentParser(
        "sra-download", description="Download sequential SRA accessions"
    )
    parser.add_argument(
        "start", type=int, help="First SRA accession number in sequence to download"
    )
    parser.add_argument(
        "end", type=int, help="Last SRA accession number in sequence to download"
    )
    parser.add_argument(
        "--no-include",
        dest="no_include",
        action="store_false",
        help="Do not include `end' in sequence to download",
    )
    arguments = parser.parse_args(args)
    download_sras(arguments.start, arguments.end, arguments.no_include)
    sys.exit(0)


if __name__ == "__main__":
    if os.path.basename(sys.argv[0]) == os.path.basename(__file__):
        main(sys.argv[1:])
    else:
        main(sys.argv[2:])
