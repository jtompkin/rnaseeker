# RNAseeker
RNA-seq scripts and libraries

Josh Tompkin 2023
## Command line programs
+ go_filter: Filter gProfiler output and format for Revigo
```bash
rnaseq gofilter [-h] [-v] [-c TERM_COLUMN] [-d IN_DELIMITER] [-o OUT_FILE] [-p PVAL_COLUMN] [-i ID_COLUMN]
                [-s OUT_DELIMITER] [--no-format] [--header] [-f FILTER_TERMS] [--filter-file FILTER_PATH] gProfiler_file
```
+ fasta_filter: Filter fasta sequences by length and 'N' content and write to fasta file
```bash
rnaseq fasta_filter [-h] [-o OUT_PATH] [-l LINE_LENGTH] fasta_path minimum_basepairs
```
+ fasta_split: [UNDER CONSTRUCTION]
## Python libraries
+ sequence
  + sequence_io: Manipulate sequence files and store sequence information
