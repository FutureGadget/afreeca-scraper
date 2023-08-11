"""
This module contains banner printer related functions.
"""
from constants import BANNER_FILE


def show_banner():
    """
    This function prints banner defined in the BANNER_FILE
    """
    with open(BANNER_FILE, "r", encoding="utf-8") as file:
        line = file.readline()
        while line:
            print(line)
            line = file.readline()


if __name__ == "__main__":
    show_banner()
