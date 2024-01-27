#!/usr/bin/env python3
from __future__ import annotations
from typing import Literal
import argparse
import sys
import os

from rnaseeker.sequence import sequence_io
from rnaseeker.version import __version__


def get_reader_type(
    format: str,
) -> tuple[
    type[sequence_io.FastaReader] | type[sequence_io.FastqReader],
    type[sequence_io.FastaWriter] | type[sequence_io.FastqWriter],
]:
    if format == 'fasta':
        return sequence_io.FastaReader, sequence_io.FastaWriter
    elif format == 'fastq':
        return sequence_io.FastqReader, sequence_io.FastqWriter
    raise ValueError(
        f"Invalid format for input file: {format}. Must be either 'fasta' or 'fastq'"
    )


def split_file(
    split_number: int,
    input_path: str = '-',
    input_format: Literal['fasta'] | Literal['fastq'] = 'fasta',
    is_sequence_number: bool = False,
    directory: str = '.',
    prefix: str | None = None,
) -> None:
    """Split sequence file."""
    directory = directory.rstrip('/')
    if not os.path.isdir(directory):
        os.mkdir(directory)
    split_file_count = 1
    reader_type, writer_type = get_reader_type(input_format)
    with reader_type(input_path) as file_reader:
        file_reader.count_sequences()
        if is_sequence_number:
            # Hacky ceiling division
            total_files = -(file_reader.sequence_count // -split_number)
            sequences_per_file, remainder = split_number, 0
        else:
            total_files = split_number
            sequences_per_file, remainder = divmod(
                file_reader.sequence_count, total_files
            )
        digits = len(str(total_files))
        seqs_in_this_file = sequences_per_file + (remainder >= 0)
        remainder -= 1
        to_write: list[sequence_io.SequenceRecord] = []
        for sequence in file_reader.parse():
            if len(to_write) < seqs_in_this_file:
                to_write.append(sequence)
            else:
                out_path = f'{directory}/{prefix}-{split_file_count:0{digits}d}.fa'
                with writer_type(out_path) as file_writer:
                    file_writer.write_sequences(to_write)
                seqs_in_this_file = sequences_per_file + (remainder >= 0)
                remainder -= 1
                to_write = []
                split_file_count += 1
        if to_write:
            out_path = f'{directory}/{prefix}-{split_file_count}.fa'
            with writer_type(out_path) as file_writer:
                file_writer.write_sequences(to_write)


def pos_non_zero_int(argument: str) -> int:
    """Test if argument is a non-zero positive integer."""
    test_arg = int(argument)
    if test_arg <= 0:
        raise argparse.ArgumentTypeError('Enter non-zero positive integer')
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
        '-i',
        '--input',
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
        default='split',
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
        args.number,
        args.input,
        args.input_format,
        args.is_sequence_number,
        args.directory,
        args.prefix,
    )


if __name__ == '__main__':
    main(sys.argv)
