# RNAseeker

## RNA-seq scripts and libraries

Josh Tompkin

<jtompkin-dev@proton.me>

<https://github.com/jtompkin/rnaseeker>

### Install with pip

```bash
pip3 install rnaseeker
```

### Command line programs

- go-filter: Filter gProfiler output and format for Revigo

```bash
rnaseeker go-filter [-h] [-v] [-c TERM_COLUMN] [-d IN_DELIMITER] [-o OUT_FILE] [-p PVAL_COLUMN] [-i ID_COLUMN] [-s OUT_DELIMITER] [--no-format] [--header] [-f FILTER_TERMS] [--filter-file FILTER_PATH] gProfiler_file
```

- fasta-filter: Filter fasta sequences by length and 'N' content

```bash
rnaseeker fasta-filter [-h] [-o OUT_PATH] [-l LINE_LENGTH] fasta_path minimum_basepairs
```

- fasta-split: Split fasta/fastq files

```bash
rnaseeker fasta-split [-h] [-v] [-i INPUT] [-f {fasta,fastq}] [-s] [-p [PREFIX]] [--header-prefix [REGEX]] [-d DIRECTORY] [-e EXTENSION] number
```

### Python libraries

- sequence
  - sequence_io: Manipulate sequence files and store sequence information
