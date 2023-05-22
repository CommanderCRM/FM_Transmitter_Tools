# FM_Transmitter_Tools
* Giving random (UUID4) names to all files in the folder
* Re-creating files to modify their creation/modification dates
* Deleting ID3 MP3 tags

Has multithreading support which may significantly increase execution time.

```
usage: tools.py [-h] [-n] [-t] [-c] [-a] [--MT] src

MP3 management for FM transmitters

positional arguments:
  src                Source location

options:
  -h, --help         show this help message and exit
  -n, --rename       random rename (default: None)
  -t, --remove-tags  ID3 tag removing (default: None)
  -c, --recreate     file recreation (default: None)
  -a, --all          all options (default: None)
  --MT               multithreading (default: None)
```
