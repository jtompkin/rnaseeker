#! /usr/bin/env python3
from __future__ import annotations

import argparse

from rnaseeker.sequence import sequence_io


def filter_fasta(
        input_path: str,
        output_path: str,
        minimum_basepairs: int,
        line_length: int | None
) -> None:
    """Filter fasta sequences by length and 'N' content and write to fasta file."""
    fasta_reader = sequence_io.FastaReader(input_path)
    with fasta_reader as fasta_in:
        good_sequences = []
        for sequence in fasta_in.parse():
            if len(sequence.sequence) >= minimum_basepairs >= sequence.sequence.count('N'):
                good_sequences.append(sequence)
    fasta_writer = sequence_io.FastaWriter(output_path, line_length)
    with fasta_writer as fasta_out:
        fasta_out.write_sequences(good_sequences)


def main(arguments: list[str] | None = None):
    """Parse arguments and call function."""
    parser = argparse.ArgumentParser('fasta_filter')

    parser.add_argument('fasta_path',
                        help="Path to fasta file. Reads from standard in if `-'")
    parser.add_argument('minimum_basepairs', type=int,
                        help='Miminum size of sequence in base pairs to keep.')
    parser.add_argument('-o', '--output', dest='out_path', default='-',
                        help="Path to output fasta file. Writes to standard out if `-'. "+
                        "Defaults to `-'.")
    parser.add_argument('-l', '--line-length', dest='line_length', type=int, default=60,
                        help='Maximum line length for sequence lines in output fasta file. Give 0 '+
                        'to place entire sequence on one line. Default is 60')

    args = parser.parse_args(arguments)
    if args.line_length == 0:
        line_length = None
    else:
        line_length = args.line_length
    filter_fasta(args.fasta_path, args.out_path, args.minimum_basepairs, line_length)


if __name__ == '__main__':
    main()
