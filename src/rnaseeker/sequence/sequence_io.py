#! /usr/bin/env python3
"""Manipulate sequence files and store sequence information."""
from __future__ import annotations

from typing import Generator, Iterable
import sys


class SequenceRecord:
    """Store and manipulate sequence information."""

    def __init__(
        self,
        sequence: str,
        description: str,
        quality: str | None = None,
        encoding: str | None = None,
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
        """Calculate quality scores from quality string.

        Returns:
            list[int]: All quality scores as integers
        """
        encoding_to_int = {'phred33': 33, '33': 33, 'phred64': 64, '64': 64}
        return [ord(i) - encoding_to_int[self.encoding] for i in self.quality]

    def transcribe(self, reverse: bool = False) -> SequenceRecord:
        """Transcribe sequence. [UNDER CONSTRUCTION]

        Args:
            reverse (bool, optional): Whether to reverse transcribe
            RNA sequence to DNA. Defaults to False.

        Returns:
            SequenceRecord: Object containing transcribed sequence
        """
        if reverse:
            return SequenceRecord('', '')
        return SequenceRecord('', '')


class _FileReader:
    def __init__(self, path: str, encoding: str | None = None) -> None:
        self.path = path
        self.encoding = encoding
        self.sequence_count = 0

    def __enter__(self):
        if self.path == '-':
            self._stream = sys.stdin
        else:
            self._stream = open(self.path, 'r', encoding='UTF-8')
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._stream.close()


class FastaReader(_FileReader):
    """Read fasta files"""
    def parse(self) -> Generator[SequenceRecord, None, None]:
        """Parse entire fasta file for sequences.

        Raises:
            AttributeError: File stream is not opened

        Yields:
            Generator[SequenceRecord, None, None]: Iterator containing sequences 
        records from file
        """
        try:
            header = self._stream.readline().rstrip()
        except AttributeError as exception:
            raise AttributeError(
                "Need to open file stream by running inside of 'with' block."
            ) from exception
        sequence = ''
        self.sequence_count += 1
        for line in self._stream:
            if line.startswith('>'):
                yield SequenceRecord(sequence, header)
                header = line.rstrip()
                sequence = ''
                self.sequence_count += 1
            else:
                sequence += line.rstrip()
        yield SequenceRecord(sequence, header)

    def _read_sequence(self) -> SequenceRecord:
        """Parse fasta file and return next sequence as a
        SequenceRecord object. [UNDER CONSTRUCTION]"""
        return SequenceRecord('', '')


class FastqReader(_FileReader):
    """Read fastq files"""
    def parse(self) -> Generator[SequenceRecord, None, None]:
        """Parse fastq file and return iterator of SequenceRecord objects."""
        try:
            header = self._stream.readline().rstrip()
        except AttributeError as exception:
            raise AttributeError(
                "Need to open file stream by running inside of 'with' block."
            ) from exception
        header = self._stream.readline().rstrip()
        sequence = ''
        quality = ''
        sequence_flag = True
        self.sequence_count += 1
        for line in self._stream:
            if line.startswith('>'):  # Header line
                yield SequenceRecord(sequence, header, quality, self.encoding)
                header = line.rstrip()
                sequence = ''
                quality = ''
                self.sequence_count += 1
            elif line.startswith('+'):  # Spacer line
                sequence_flag = False
            else:
                if sequence_flag:
                    sequence += line.rstrip()
                else:
                    quality += line.rstrip()


class _FileWriter:
    def __init__(self, path: str, line_length: int | None = 60) -> None:
        self.path = path
        self.line_length = line_length
        self.sequences_written = 0
        self._stream = None

    def __enter__(self):
        if self.path == '-':
            self._stream = sys.stdout
        else:
            self._stream = open(self.path, 'w', encoding='UTF-8')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._stream.close()


class FastaWriter(_FileWriter):
    """Write fasta files."""

    def write_sequence(self, sequence: SequenceRecord) -> None:
        """Write single SeqRecord object to file."""
        if self._stream is None:
            raise AttributeError(
                "Need to open file stream by running inside of 'with' block."
            )
        if self.line_length is None:
            sequence_split = [sequence.sequence + '\n']
        else:
            sequence_split = [
                sequence.sequence[i : i + self.line_length] + '\n'
                for i in range(0, len(sequence.sequence), self.line_length)
            ]
        self._stream.writelines([sequence.description + '\n'] + sequence_split)
        self.sequences_written += 1

    def write_sequences(self, sequences: Iterable[SequenceRecord]) -> None:
        """Write multiple SeqRecord objects to file."""
        if self._stream is None:
            raise AttributeError(
                "Need to open file stream by running inside of 'with' block."
            )
        for sequence in sequences:
            if self.line_length is None:
                sequence_split = [sequence.sequence + '\n']
            else:
                sequence_split = [
                    sequence.sequence[i : i + self.line_length] + '\n'
                    for i in range(0, len(sequence.sequence), self.line_length)
                ]
            self._stream.writelines([sequence.description + '\n'] + sequence_split)
            self.sequences_written += 1
