# BMC-Tools
RDP Bitmap Cache parser.
## Input
`bmc-tools` processes `bcache*.bmc` and `cache????.bin` files found inside Windows user profiles.
## Usage
```sh
./bmc-tools.py [-h] [-o] -d DEST [-c COUNT] -s SRC [-v]
```
With the following arguments meaning:
```
  -h, --help            show this help message and exit
  -o, --old             Extract the old bitmap data found in the BMCache file.
  -d DEST, --dest DEST  Specify the directory where to store the extracted
                        bitmaps.
  -c COUNT, --count COUNT
                        Only extract the given number of bitmaps.
  -s SRC, --src SRC     Specify the BMCache file or directory to process.
  -v, --verbose         Determine the amount of information displayed.
```
## Changelog
```
25/11/2016		1.01	Compressed data handling improved.
25/11/2016		1.00c	Unused variable removed.
10/08/2016		1.00b	--dest parameter processing fixed.
01/07/2016		1.00a	cacheXXXX.bin header detection fixed.
27/06/2016		1.00	Initial release.
```
