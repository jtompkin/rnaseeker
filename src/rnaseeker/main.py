#!/usr/bin/env python3
"""
-------------
+ rnaseeker +
-------------
RNA-seq scripts and libraries

author: Josh Tompkin
contact: jtompkin-dev@proton.me
source: https://github.com/jtompkin/rnaseeker

usage:
    rnaseeker [-h] [-v] <sub-program> <sub-program args>
options:
    -h, --help      show this help message and exit
    -v, --version   show program's version number and exit
available sub-programs:
    go-filter:      Filter gProfiler output and format for Revigo
    fasta-split:    Split fasta/fastq files
    fasta-filter:   Filter fasta sequences by length and 'N' content
example (show help information for fasta-split sub-program):
    rnaseeker fasta-split --help
"""
import sys

from .gene_ontology import go_filter
from .fasta import fasta_split, fasta_filter, extract_promoters
from .version import __version__


def main(arguments: list[str] | None = None) -> None:
    """Deploy given sub-program. Print version or help information if requested."""
    program_to_function = {
        'go-filter': go_filter.main,
        'fasta-split': fasta_split.main,
        'fasta-filter': fasta_filter.main,
        'extract-promoters': extract_promoters.main,
    }
    programs = '{' + ', '.join(program_to_function) + '}'
    try:
        if '-v' == sys.argv[1] or '--version' == sys.argv[1]:
            print(f'rnaseeker {__version__}')
            sys.exit(0)
        elif '-h' == sys.argv[1] or '--help' == sys.argv[1]:
            print(__doc__.strip())
            sys.exit(0)
    except IndexError:  # Only 'rnaseeker' program name was given
        sys.stderr.write(
            'usage: rnaseeker [-h] [-v] <sub-program> <sub-program args>\n'
            + f'Available sub-programs: {programs}\n'
        )
        sys.exit(1)
    # Exclude 'rnaseeker' program name
    args = sys.argv[1:]

    try:
        # Pass args to sub-program excluding sub-program name
        program_to_function[args[0]](args[1:])
    except KeyError as exc:
        raise ValueError(
            f'{args[0]} is not a valid sub-program. Valid sub-programs: {programs}'
        ) from exc


if __name__ == '__main__':
    main(sys.argv)
