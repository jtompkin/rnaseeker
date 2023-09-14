#! /usr/bin/env python3
"""Manipulate sequence files and store sequence information."""
from typing import Generator, TextIO
import sys

class SequenceRecord():
    """Class containing sequence information"""
    def __init__(
            self,
            sequence: str,
            description: str,
            quality: str | None = None,
            encoding: str | None = None
    ) -> None:
        self.sequence = sequence
        self.description = description
        if quality is None:
            self.quality = ''
        else:
            self.quality = quality
        if encoding is None:
            self.encoding = 'phred33'
        else:
            self.encoding = encoding
        self.name = self.description[1:].split()[0]

    def get_quality_scores(self) -> list[int]:
        encoding_to_int = {
            'phred33': 33,
            '33': 33,
            'phred64': 64,
            '64': 64
        }
        return [ord(i)-encoding_to_int[self.encoding] for i in self.quality]


class _FileReader():
    def __init__(
            self,
            path: str,
            encoding: str | None = None
    ) -> None:
        self.path = path
        self.encoding = encoding
        self.seuqnce_count = 0

    def get_file(self) -> TextIO:
        """Return file object from self.path. Return sys.stdin if `-'."""
        if self.path == '-':
            return sys.stdin
        return open(self.path, 'r', encoding='UTF-8')


class FastaReader(_FileReader):
    """Read fasta files"""
    def parse(self) -> Generator[SequenceRecord, None, None]:
        """Parse fasta file and return iterator of SequenceRecord objects"""
        with self.get_file() as fasta_file:
            header = next(fasta_file, None).rstrip()
            sequence = ''
            self.seuqnce_count += 1
            for line in fasta_file:
                if line.startswith('>'):
                    yield SequenceRecord(sequence, header)
                    header = line.rstrip()
                    sequence = ''
                    self.seuqnce_count += 1
                else:
                    sequence += line.rstrip()
            yield SequenceRecord(sequence, header)

class FastqReader(_FileReader):
    """Read fastq files"""
    def parse(self) -> Generator[SequenceRecord, None, None]:
        """Parse fastq file and return iterator of SequenceRecord objects"""
        with self.get_file() as fastq_file:
            header = next(fastq_file, None).rstrip()
            sequence = ''
            quality = ''
            sequence_flag = True
            self.seuqnce_count += 1
            for line in fastq_file:
                if line.startswith('@'):
                    yield SequenceRecord(sequence, header, quality, self.encoding)
                    header = line.rstrip()
                    sequence = ''
                    quality = ''
                    sequence_flag = True
                    self.seuqnce_count += 1
                elif line.startswith('+'):
                    sequence_flag = False
                else:
                    if sequence_flag:
                        sequence += line.rstrip()
                    else:
                        quality += line.rstrip()
            yield SequenceRecord(sequence, header, quality, self.encoding)
