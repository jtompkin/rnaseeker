#!/usr/bin/env python3
from __future__ import annotations
import argparse
import sys
import os

from rnaseeker.sequence import sequence_io
from rnaseeker.version import __version__


def split_file(
    split_number: int,
    input_path: str = '-',
    is_sequence_number: bool = False,
    directory: str = '.',
    prefix: str | None = None,
) -> None:
    """Split sequence file."""
    directory = directory.rstrip('/')
    if not os.path.isdir(directory):
        os.mkdir(directory)
    # split_file_count = 0
    with sequence_io.FastaReader(input_path) as fasta_reader:
        for sequence in fasta_reader.parse():
            print(sequence.name)
            print(fasta_reader.sequence_count)


def pos_non_zero_int(argument: str) -> int:
    """Test if argument is a non-zero positive integer."""
    test_arg = int(argument)
    if test_arg <= 0:
        raise argparse.ArgumentTypeError()
    return test_arg


def main(arguments: list[str] | None = None) -> None:
    """Parse arguments and call funcion."""
    parser = argparse.ArgumentParser(
        prog='fasta_split', description='Split fatsa/fastq files.'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'rnaseq: {parser.prog} {__version__}',
    )
    input_options = parser.add_argument_group('input options')
    input_options.add_argument(
        'input_file',
        default='-',
        help="Path to fasta/fastq file. Reads from standard input if `-'. "
        + "Defaults to `-'",
    )
    input_options.add_argument(
        '-f',
        '--input-format',
        dest='input_format',
        choices=['fasta', 'fastq'],
        default='fasta',
        help="File format of input file. Either `fasta' or `fastaq'. "
        + "Default is `fasta'",
    )
    split_options = parser.add_argument_group('split options')
    split_options.add_argument(
        'number',
        type=pos_non_zero_int,
        help='Number of files to split input file into, or number of '
        + 'sequences to place in each file if -s is provided',
    )
    split_options.add_argument(
        '-s',
        '--sequence-number',
        dest='is_sequence_number',
        action='store_true',
        help='If provided, given number represents the number of sequences '
        + 'to place into each split file',
    )
    output_options = parser.add_argument_group('output options')
    output_options.add_argument(
        '-p',
        '--prefix',
        help="Prefix for naming split files. Default is `split', or "
        + 'sequence header if one sequence is put in each file',
    )
    output_options.add_argument(
        '-d',
        '--directory',
        default='.',
        help="Directory to place split files in. Default is `.' (current working directory)",
    )

    args = parser.parse_args(arguments)
    split_file(
        args.number, args.input, args.is_sequence_number, args.directory, args.prefix
    )


if __name__ == '__main__':
    main(sys.argv)
