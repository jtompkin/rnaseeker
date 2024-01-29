#!/usr/bin/env python3
from __future__ import annotations
from typing import Literal
import argparse
import sys
import os
import re

from rnaseeker.sequence import sequence_io as seqio
from rnaseeker.version import __version__


def get_io_types(
    format: str,
) -> tuple[
    type[seqio.FastaReader] | type[seqio.FastqReader],
    type[seqio.FastaWriter] | type[seqio.FastqWriter],
]:
    if format == 'fasta':
        return seqio.FastaReader, seqio.FastaWriter
    if format == 'fastq':
        return seqio.FastqReader, seqio.FastqWriter
    raise ValueError(
        f"Invalid format for input file: {format}. Must be either 'fasta' or 'fastq'"
    )


def get_header_prefix(header_regex: str, sequence: seqio.SequenceRecord) -> str:
    if header_regex == '':
        return sequence.name
    match = re.search(header_regex, sequence.description)
    if match:
        return match.group(0)
    return sequence.name


def get_file_prefix(prefix: str, input_path: str) -> str:
    if prefix == '/':
        file_name = input_path.split('/')[-1]
        match = re.search(r'\..*', file_name)
        if match:
            return file_name[0 : match.start()] + '-'
        return file_name + '-'
    return prefix


def split_file(
    split_number: int,
    input_path: str = '-',
    input_format: Literal['fasta'] | Literal['fastq'] = 'fasta',
    is_sequence_number: bool = False,
    directory: str = '.',
    prefix: str = 'split-',
    header_regex: str | None = None,
    extension: str | None = None,
) -> None:
    """Split sequence file."""
    if header_regex is not None:
        assert (
            is_sequence_number and split_number == 1
        ), "Cannot use header regular expression if '-s' is not provided and split number is not 1"
    directory = directory.rstrip('/')
    if not os.path.isdir(directory):
        os.mkdir(directory)
    split_file_count = 1
    reader_type, writer_type = get_io_types(input_format)
    if extension is None:
        extension = {seqio.FastaReader: 'fa', seqio.FastqReader: 'fq'}[reader_type]
    extension = extension.lstrip('.')
    with reader_type(input_path, encoding='') as file_reader:
        file_reader.reader.set_sequence_count()
        if is_sequence_number:
            # Hacky ceiling division
            total_files = -(file_reader.reader.sequence_count // -split_number)
            sequences_quotient, sequences_remainder = split_number, 0
        else:
            total_files = split_number
            sequences_quotient, sequences_remainder = divmod(
                file_reader.reader.sequence_count, total_files
            )
        if total_files > 200:
            # fmt: off
            if input(
                f'Operation will create {total_files} files. Continue? (y/N) '
            ).lower() != 'y':
                sys.exit(0)

        digits = len(str(total_files))
        seqs_in_this_file = sequences_quotient + (sequences_remainder > 0)
        sequences_remainder -= 1
        file_prefix = get_file_prefix(prefix, input_path)
        to_write: list[seqio.SequenceRecord] = []
        for sequence in file_reader.parse():
            if len(to_write) < seqs_in_this_file:
                to_write.append(sequence)
            else:
                if header_regex is not None:
                    file_prefix = get_header_prefix(header_regex, sequence)
                    out_path = f'{directory}/{file_prefix}.{extension}'
                else:
                    out_path = f'{directory}/{file_prefix}{split_file_count:0{digits}d}.{extension}'
                with writer_type(out_path) as file_writer:
                    file_writer.write_sequences(to_write)
                seqs_in_this_file = sequences_quotient + (sequences_remainder > 0)
                sequences_remainder -= 1
                to_write = [sequence]
                split_file_count += 1
        # TODO: refactor so don't have to repeat this
        if to_write:
            if header_regex is not None:
                file_prefix = get_header_prefix(header_regex, to_write[0])
                out_path = f'{directory}/{file_prefix}.{extension}'
            else:
                out_path = f'{directory}/{file_prefix}{split_file_count}.fa'
            with writer_type(out_path, 80) as file_writer:
                file_writer.write_sequences(to_write)


def pos_non_zero_int(argument: str) -> int:
    """Test if argument is a non-zero positive integer."""
    test_arg = int(argument)
    if test_arg <= 0:
        raise argparse.ArgumentTypeError("'number' must be a non-zero positive integer")
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
        version=f'rnaseeker: {parser.prog} {__version__}',
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
        default='split-',
        const='/',
        nargs='?',
        help='Prefix for naming split files. Provide without argument to use name of input file. '
        + "Default is `split-'",
    )
    output_options.add_argument(
        '--header-prefix',
        dest='header_regex',
        metavar='REGEX',
        const='',
        nargs='?',
        help='Prefix split files based on given regular expression applied to each sequence header. '
        + 'Provide without a regular expression to use first word of each sequence header. '
        + "Incompatable with '-p'. Only provide if '-s' is given and number is 1. EXPERIMENTAL",
    )
    output_options.add_argument(
        '-d',
        '--directory',
        default='.',
        help="Directory to place split files in. Default is `.' (current working directory)",
    )
    output_options.add_argument(
        '-e',
        '--extension',
        help="File extension to use. Defaults to `fa' for fasta input and `fq' for fastq input",
    )

    args = parser.parse_args(arguments)
    split_file(
        args.number,
        args.input,
        args.input_format,
        args.is_sequence_number,
        args.directory,
        args.prefix,
        args.header_regex,
    )


if __name__ == '__main__':
    main()
