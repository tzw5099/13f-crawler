## Challenge / Problem

Write code in Python that parses fund holdings pulled from EDGAR, given a ticker or CIK.

This program generates tab-delimited text (with a header row) from the latest 13F filing.

## Setup

```sh
pip install -r requirements.txt
# edit crawler.py to set the desired ticker/cik and output file
```

### Tests

Tests are located at `test/tests.py`. Tests may take a few minutes to run, as they process from start to finish
many CIKs.

**Note** tests may not run on Windows, as they access the `/tmp` directory.

## Instructions

Standalone usage is easy: edit `crawler.py` to set the desired ticker/cik and output file, and then run `python3 crawler.py`.

Programmatic usage is also easy! Some API details are below, but the code is relatively short - check it out!

### API

- `Holding` (class)

POPO (is that a thing? it should be a thing) which can return itself as an array, and a method for the headers of the output file

  - `constructor`: instantiate a new Holding object from a the fields of an `infoTable` entry
  - `to_array()`: return the Holding object as an array, in the order of...
  - **static** `get_headers()`: return an array of the headers, matching the order of `to_array()`

- `find_13f_report(ticker)`

for a given ticker or cik, search Edgar for the latest 13F filing and return the contents (`str`) of the complete document.

**errors** throws `ValueError` on error

- `parse_13f_doc(report)`

given the downloaded 13f report, create and return a Holding object for each info table entry

- `write_holding_array_to_file(holding_array, output_path)`

given an array of Holding objects, write the tsv to the provided output file

- `generate_report_for_ticker(ticker, output_path)`

interface for downloading, processing and writing the 13f report to the specified output file

## Thoughts and concerns

> Let us know your thoughts on how to deal with different formats.

In examining 10 companies and their most recent 13F reports, I did not find significant variation between filing formats.

I did discover cases in which some XML tags on the `infoTable` element were missing instead of blank, however this was already
resolved by the `_get_string_or_empty_string()` method implementation.

If there were significant differences in filing formats, I would implement branching in `parse_13f_doc()` to first
 identify the format and then apply the correct parser.

For minor or erratic differences, depending on the expected output, I would implement the same solution as here:
missing fields are blank strings in the TSV report.

## License

Copyright 2017 Tristan Kernan

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

