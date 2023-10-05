#! /usr/bin/env python3
from sys import stderr
import argparse
import subprocess
import shutil
import csv
import os
import re


def gff_to_bed(gff_path: str, out_path: str):
    with(
        open(f'{gff_path}', 'r', encoding='UTF-8') as gff_file,
        open(out_path, 'w', encoding='UTF-8') as bed_file
    ):
        gff_reader = csv.reader(gff_file, delimiter='\t')
        bed_writer = csv.writer(bed_file, delimiter='\t',
                                quoting=csv.QUOTE_NONE, lineterminator='\n')
        for row in gff_reader:
            row_slice = [row[i] for i in (0, 3, 4, 8, 7, 6)]
            row_slice[4] = '100'
            row_slice[3] = re.sub(r'.*GeneID:|;Name.*', '', row_slice[3])
            bed_writer.writerow(row_slice)


def extract_gene_info(gff_path: str, out_path: str):
    with(
        open(gff_path, 'r', encoding='UTF-8') as gff_file,
        open(out_path, 'w', encoding='UTF-8') as out_file
    ):
        out_file.writelines([line for line in gff_file if re.search('gbkey=Gene', line)])


def extract_promoters(gff_path: str, fasta_path: str, length: int, out_directory: str):
    stderr.write('Extracting gene info...\n')
    extract_gene_info(gff_path, f'{out_directory}/genes.gff')
    stderr.write('Converting gff to bed...\n')
    gff_to_bed(f'{out_directory}/genes.gff', f'{out_directory}/genes.bed')

    # Make index for fasta file
    stderr.write('Making index of fasta file...\n')
    fasta_name = fasta_path.split('/')[-1]
    subprocess.run(
        f'samtools faidx --fai-idx {out_directory}/{fasta_name}.fai {fasta_path}'.split(),
        check=True
    )

    # Make table with chromosome sizes
    stderr.write('Creating table of chromosome sizes...\n')
    with(
        open(f'{out_directory}/{fasta_name}.fai', 'r', encoding='UTF-8') as index_file,
        open(f'{out_directory}/sizes.chr', 'w', encoding='UTF-8') as out_file
    ):
        for line in index_file:
            out_file.write('\t'.join(line.split('\t')[:2])+'\n')

    # Make bed file containing location of promoters
    stderr.write('Creating bed file containing location of promoters...\n')
    with open(f'{out_directory}/promoters.bed', 'w', encoding='UTF-8') as promoter_bed_file:
        promoter_bed_file.write(
            subprocess.run(
            (f'bedtools flank -i {out_directory}/genes.bed -g {out_directory}/sizes.chr '+
            f'-l {length} -r 0 -s').split(), check=True, capture_output=True, text=True
            ).stdout
        )

    # Extract promoter regions from fasta file
    stderr.write('Extracting promoter regions from fasta file...\n')
    subprocess.run(
        (f'bedtools getfasta -s -fi {fasta_path} -bed {out_directory}/promoters.bed '+
        f'-fo {out_directory}/promoters.fa -name').split(), check=True
    )
    if os.path.isfile(f'{fasta_name}.fai'):
        os.remove(f'{fasta_name}.fai')

    stderr.write(f'Results are in {out_directory}/promoters.fa\n')
    with open(f'{out_directory}/promoters.fa', 'r', encoding='UTF-8') as fasta_file:
        sequence_count = 0
        for line in fasta_file:
            if line.startswith('>'):
                sequence_count += 1
        stderr.write(f'Found {sequence_count} promoters\n')


def main(arguments: list[str] | None = None):
    parser = argparse.ArgumentParser('extract_promoters',
                                     description='Extract promoter regions from a fasta file '+
                                     'using a gff file annotations. Requires samtools and '+
                                     'bedtools to be in enviroment PATH.')

    parser.add_argument('-g', '--gff', dest='gff_file', required=True,
                        help='Path to gff file containing genome annotations.')
    parser.add_argument('-f', '--fasta', dest='fasta_file', required=True,
                        help='Path to fasta file containing genome sequences.')
    parser.add_argument('-l', '--length', dest='promoter_length', required=True, type=int,
                        help='Length of promoter regions to output')
    parser.add_argument('-d', '--directory', dest='directory', default='.',
                        help="Directory to place output files in. Defaults to current directory")

    args = parser.parse_args(arguments)
    if shutil.which('samtools') is None:
        raise FileNotFoundError('command not found: samtools\n'+
                                'samtools needs to be in the environment path')
    if shutil.which('bedtools') is None:
        raise FileNotFoundError('command not found: bedtools\n'+
                                'bedtools needs to be in the environment path')
    directory = args.directory.rstrip('/')
    if not os.path.isdir(directory):
        os.mkdir(directory)

    extract_promoters(args.gff_file, args.fasta_file, args.promoter_length, args.directory)


if __name__ == '__main__':
    main()
