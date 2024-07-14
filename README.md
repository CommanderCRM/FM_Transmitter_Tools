# FM_Transmitter_Tools

- Formatting USB drive
- Copying files to another folder or USB drive
- Giving random (UUID4) names to all files in the folder
- Re-creating files to modify their creation/modification dates
- Deleting ID3 MP3 tags

Has multithreading support which may significantly decrease execution time.

```text
usage: tools.py [-h] [-n] [-t] [-c] [-a] [-d DRIVE] [--new_name NEW_NAME] [--MT] src

MP3 management for FM transmitters

positional arguments:
  src                   Source location

options:
  -h, --help            show this help message and exit
  -n, --rename          random rename (default: None)
  -t, --remove-tags     ID3 tag removing (default: None)
  -c, --recreate        file recreation (default: None)
  -a, --all             all options (default: None)
  -d DRIVE, --drive DRIVE
                        Drive letter to be formatted (default: None)
  --new_name NEW_NAME   New drive name and new folder name (default: None)
  --MT                  multithreading (default: None)
```
