import argparse

parser = argparse.ArgumentParser(
    description="MP3 management for FM transmitters",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "-n",
    "--rename",
    dest="actions",
    action="append_const",
    const="rename",
    help="random rename",
)
parser.add_argument(
    "-t",
    "--remove-tags",
    dest="actions",
    action="append_const",
    const="remove_tags",
    help="ID3 tag removing",
)
parser.add_argument(
    "-c",
    "--recreate",
    dest="actions",
    action="append_const",
    const="recreate",
    help="file recreation",
)
parser.add_argument(
    "-a",
    "--all",
    dest="actions",
    action="append_const",
    const="all",
    help="all options",
)
parser.add_argument(
    "--MT",
    dest="actions",
    action="append_const",
    const="MT",
    help="multithreading",
)
parser.add_argument("src", help="Source location")
