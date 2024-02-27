# mediacompare

Python script wrapper around [mediainfo](https://mediaarea.net/en/MediaInfo) to allow for side-by-side comparison of two media files.  

Outputs to three columns, "tag : value1 : value2", with the column widths auto adjusting to consume full terminal width. This is done because so many of the strings are painfully long.  

Strings that exceed the width of their column will word wrap within their column. There is a `--short` switch if you would rather truncate than wrap.  


Known issues:
   - It outputs to three columns to provide a side-by-side view, but column widths aren't pretty
   - It captures the JSON output, which isn't the human readable strings. Parsing the default output would be less easy, so we deal.
   - It doesn't account for every possible stream type, but it does handle multiple streams of the same type acceptably well.  
   - It tries to keep the fields in order, but fields in the 2nd file not present in the 1st get shuffled to the bottom rather than injected into the middle. I'm not sure how to clean that up.
     
Future ideas:
   - only print the interesting fields, drop things like 'Encoding_settings'
   - add a -t option that creates a tab-separated output instead of columns, won't need to truncate


```
usage: mediacompare.py [-h] [-v] [-s] file1 file2

Wrapper for mediainfo to compare two files side-by-side

positional arguments:
  file1          The first media file.
  file2          The second media file.

options:
  -h, --help     show this help message and exit
  -v, --verbose  Include verbose debugging output. You'll regret it.
  -s, --short    Truncate long lines instead of wrapping them.
```
