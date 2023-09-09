#! /usr/bin/env python3
"""Filter gProfiler output and format for Revigo"""
# go_filter
# author: Josh Tompkin
# contact: jtompkindev@gmail.com
# github: https://github.com/jtompkin/RNAseq
import sys
import csv
import argparse


def filter_terms(
        in_path: str,
        delimiter: str = ',',
        term_column: int = 1,
        header: bool = True,
        to_filter: str = '',
        filter_path: str | None = None,
) -> list[str]:
    """Filter gene ontology terms from input file"""
    if in_path == '-':
        in_file = sys.stdin
    else:
        in_file = open(in_path, 'r', encoding='UTF-8')
    if filter_path:
        with open(filter_path, 'r', encoding='UTF-8') as filter_file:
            to_filter = filter_file.readlines()
    else:
        to_filter = to_filter.split(';')
    with in_file:
        in_reader = csv.reader(in_file, delimiter=delimiter)
        if header:
            next(in_reader)
        return [row for row in in_reader if row[term_column] not in to_filter]


def write_terms(
        out_path: str,
        terms: list[str],
        delimiter: str = '\t',
        format_out: bool = True,
        id_column: int = 2,
        pval_column: int = 4
) -> None:
    """Write gene ontology terms. Optionally format output for Revigo"""
    if out_path == '-':
        out_file = sys.stdout
    else:
        out_file = open(out_path, 'w', encoding='UTF-8')
    with out_file:
        out_writer = csv.writer(out_file, delimiter=delimiter)
        if format_out:
            out_writer.writerows(
                [[row[id_column], row[pval_column]] for row in terms]
            )
        else:
            out_writer.writerows(terms)


def main():
    parser = argparse.ArgumentParser(prog='go_filter',
                                     description='Filter gProfiler output and format for revigo')

    parser.add_argument('gProfiler_file',
                        help="Path to gProfiler file to filter. Reads from standard in if `-'.")

    input_options = parser.add_argument_group('input options')
    input_options.add_argument('-c', '--term-column', dest='term_column', type=int, default=1,
                               help='Integer of column index containing gene ontology terms. '+
                               'Index starts at 0. Defaults to 1.')
    input_options.add_argument('-d', '--in-delimiter', dest='in_delimiter', default=',',
                               help="Delimiter character for input. Defaults to `,'.")

    output_options = parser.add_argument_group('output options')
    output_options.add_argument('-o', '--out', dest='out_path', default='-',
                                help="Path to output file. Writes to standard out if `-'. "+
                                "Defaults to `-'.")
    output_options.add_argument('-p', '--pval-column', dest='pval_column', type=int, default=4,
                                help='Integer index of column containing result P-value. '+
                                'Index starts at 0. Defaults to 4. Only used if formatting output.')
    output_options.add_argument('-i', '--id-column', dest='id_column', type=int, default=2,
                                help='Integer index of column containing gene ontology ids. '+
                                'Index starts at 0. Defaults to 2. Only used if formatting output.')
    output_options.add_argument('--no-format', dest='format_out', action='store_false',
                                help='Do not format output for Revigo. Output will be '+
                                'formatted like gProfiler.')
    output_options.add_argument('-s', '--out-delimieter', dest='out_delimiter', default='\t',
                                help='Delimiter character for output. Defaults to tab.')

    filter_options = parser.add_argument_group('filter options')
    filter_options.add_argument('-f', '--filter', dest='filter_terms',
                                default="biological_process;molecular_function;cellular_component",
                                help='String containing gene ontology terms to filter from input '+
                                'file. Separate terms with a semicolon (;).')
    filter_options.add_argument('--filter-file', dest='filter_path',
                                help='Path to file containing gene ontology terms to filter. '+
                                "One gene ontology term per line. Not compatible with -f.")

    args = parser.parse_args()

    filtered_terms = filter_terms(args.gProfiler_file,
                                  delimiter=args.in_delimiter,
                                  header=True,
                                  to_filter=args.filter_terms,
                                  filter_path=args.filter_path)
    write_terms(args.out_path,
                terms=filtered_terms,
                delimiter=args.out_delimiter,
                format_out=args.format_out,
                id_column=args.id_column,
                pval_column=args.pval_column)


if __name__ == '__main__':
    main()
