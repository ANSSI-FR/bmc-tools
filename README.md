# BMC-Tools
RDP Bitmap Cache parser.
## Input
`bmc-tools` processes `bcache*.bmc` and `cache????.bin` files found inside Windows user profiles.
## Usage
```sh
./bmc-tools.py [-h] -s SRC -d DEST [-c COUNT] [-v] [-o] [-b] [-w WIDTH]
```
With the following arguments meaning:
```
  -h, --help              show this help message and exit
  -s SRC, --src SRC       Specify the BMCache file or directory to process.
  -d DEST, --dest DEST    Specify the directory where to store the extracted bitmaps.
  -c COUNT, --count COUNT Only extract the given number of bitmaps.
  -v, --verbose           Determine the amount of information displayed.
  -o, --old               Extract the old bitmap data found in the BMCache file.
  -b, --bitmap            Provide a collage bitmap aggregating all the tiles.
  -w WIDTH, --width WIDTH Specify the number of tiles per line of the aggregated bitmap (default=64).
```
## Changelog
```
02/03/2023		3.02	Added destination folder existence check beforehand.
01/03/2023		3.01	Fixed old Bitmaps storage and export.
10/02/2022		3.00	Now performing tile decompression.
07/12/2020		2.11	Corrected minor string printing issue under Python3.
07/12/2020		2.10	Improved collage creation under Python3.
04/12/2020		2.00	Now compatible with both Python2 and Python3.
23/11/2020		1.04	Fixed Bitmap size field.
30/04/2018		1.03	Added extra aggregated bitmap/collage output.
22/04/2018		1.02	Added support for (old?) bcache23.bmc files.
25/11/2016		1.01	Compressed data handling improved.
25/11/2016		1.00c	Unused variable removed.
10/08/2016		1.00b	--dest parameter processing fixed.
01/07/2016		1.00a	cacheXXXX.bin header detection fixed.
27/06/2016		1.00	Initial release.
```
