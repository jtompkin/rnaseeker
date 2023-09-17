#! /usr/bin/env python3
"""
----------
+ rnaseq +
----------
RNA-seq scripts and libraries
    rnaseq [-h] [-v] <sub-program> <sub-program args>
options:
    -h, --help      show this help message and exit
    -v, --version   show program's version number and exit
Available sub-programs
    go_filter: Filter gProfiler output and format for Revigo.
    fasta_split: 
    fasta_filter:
"""
from __future__ import annotations

import sys

from .gene_ontology import go_filter
from .fasta import fasta_split, fasta_filter
from .version import __version__

_VERSION = __version__


def main():
    """Deploy given sub-program. Print version or help information if requested."""
    program_to_function = {
        'go_filter': go_filter.main,
        'fasta_split': fasta_split.main,
        'fasta_filter': fasta_filter.main,
    }
    programs = '{'+', '.join(list(program_to_function))+'}'
    try:
        if '-v' == sys.argv[1] or '--version' == sys.argv[1]:
            print(f'rnaseq {_VERSION}')
            sys.exit(0)
        elif '-h' == sys.argv[1] or '--help' == sys.argv[1]:
            print(__doc__.strip())
            sys.exit(0)
    except IndexError:  # Only program name was given
        sys.stderr.write('Usage: rnaseq [-h] [-v] <sub-program> <sub-program args>\n'+
                         f'Available sub-programs: {programs}\n')
        sys.exit(1)
    # Exclude program name
    args = sys.argv[1:]

    try:
        # Pass args to sub-program excluding sub-program name
        program_to_function[args[0]](args[1:])
    except KeyError as exc:
        raise ValueError(
            f'{args[0]} is not a valid sub-program. Valid sub-programs: {programs}'
        ) from exc


if __name__ == '__main__':
    main()
