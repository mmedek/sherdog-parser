"""
Forked from https://github.com/Montanaz0r
"""
import logging
import json

from typing import Any, Dict

from fighter import Fighter

# Initializes logging file.
logging.basicConfig(
    filename="sherdog.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def scrape_all_fighters() -> None:
    """
    Scrapes information about all fighters in Sherdog's database and saves them into csv or json file.
    :param filetype: string with either 'csv' or 'json' as a type of file where results will be stored
    :return: None
    """

    fighter_index = 1  # sets up and stores index of a fighter that scraper is collecting information about.
    fail_counter = 0  # amount of 'empty' indexes in a row.

    # scraper will be done after there were 10 non-existing sites (indexes) in a row.
    while (fail_counter <= 10):
        fighter_obj = Fighter(fighter_index=fighter_index, download=True)  # creating fighter's instance object.
        print(str(fighter_obj))
        if True:
            fail_counter = 0  # resetting fail counter after finding valid page(index) for a fighter.
        else:
            fail_counter += 1
        fighter_index += 1  # incrementing index.


if __name__ == "__main__":
    scrape_all_fighters()
