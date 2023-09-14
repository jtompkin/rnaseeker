#! /usr/bin/env python3
import argparse
import os

from ..sequence import sequence_io


def split_file(
        input_path: str,
        directory: str = '.',
        prefix: str | None = None
) -> None:
    directory = directory.rstrip('/')
    if not os.path.isdir(directory):
        os.mkdir(directory)
    fasta_reader = sequence_io.FastaReader(input_path)


def pos_int(argument) -> int:
    """Test if argument is a positive integer."""
    try:
        argument = int(argument)
    except ValueError as exc:
        raise argparse.ArgumentError(
            None, f"argument -n/--number: Invalid positive integer value: {argument}") from exc
    if argument <= 0:
        raise argparse.ArgumentError(
            None, f"argument -n/--number: Invalid positive integer value: {argument}")
    return argument


def main(args: list[str] | None = None):
    parser = argparse.ArgumentParser(prog='fasta_split', description='Split fatsa/fastq files.')

    input_options = parser.add_argument_group('input options')
    input_options.add_argument('input_file',
                               help="Path to fasta/fastq file. Reads from standard input if `-'")
    input_options.add_argument('-f', '--input-format', dest='input_format',
                               choices=['fasta', 'fastq'], default='fasta',
                               help="File format of input file. Either `fasta' or `fastaq'. "+
                               "Default is `fasta'")

    split_options = parser.add_argument_group('split options')
    split_options.add_argument('number', type=pos_int,
                               help='Number of files to split input file into, or number of '+
                               'sequences to place in each file if -s is provided')
    split_options.add_argument('-s', '--sequence-number', action='store_true',
                               help='If provided, given number represents the number of sequences '+
                               'to place into each split file')

    output_options = parser.add_argument_group('output options')
    output_options.add_argument('-p', '--prefix', dest='prefix',
                                help="Prefix for naming split files. Default is `split', or "+
                                'sequence header if one sequence is put in each file')
    output_options.add_argument('-d', '--directory', dest='directory', default='.',
                                help="Directory to place split files in. Default is `.'")

    args = parser.parse_args(args)
    split_file(args.input_file, args.directory, args.prefix)


if __name__ == '__main__':
    main()
