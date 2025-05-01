# Utility Guide: PDF Reader

The PDF Reader utility allows for reading of PDF files and performing specific tasks on them.

## Table of Contents

- [Utility Guide: PDF Reader](#utility-guide-pdf-reader)
  - [Table of Contents](#table-of-contents)
  - [Functions Overview](#functions-overview)
    - [Ectract NHS No From PDF](#ectract-nhs-no-from-pdf)
      - [Required Arguments](#required-arguments)
      - [How This Function Works](#how-this-function-works)

## Functions Overview

For this utility we have the following functions/methods:

- `extract_nhs_no_from_pdf`

### Ectract NHS No From PDF

This is the main function that is called in order to process a batch.
This will call the other two functions in order to successfully process a batch.

#### Required Arguments

- `file`:
  - Type: `str`
  - This is the file path stored as a string.

#### How This Function Works

1. It starts off by storing the PDF file as a PdfReader object, this is from the `pypdf` package.
2. Then it loops thrpugh each page.
3. If it finds the string *"NHS No"* in the page, it extracts it and removes any whitespaces, then adds it to a pandas DataFrame - `nhs_no_df`
