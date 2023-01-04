"""
Forked from https://github.com/Montanaz0r
"""
import json
import logging
import traceback

from fighter import Fighter
from fight import Fight
from proxy import Proxies

from bs4 import BeautifulSoup
import requests

# Initializes logging file.
logging.basicConfig(
    filename="sherdog.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

MAX_FIGHTS = 100


def scrape_all_organizations(organization_filename, events_filename) -> None:
    organization_index = 17000
    fail_cnt = 0
    with open(organization_filename, "a") as organization_file:
        with open(events_filename, "a") as events_file:
            # when downloading specific fighter fails more then 5 times interrupt scrapping
            while (organization_index <= 20000) and (fail_cnt <= 900):
                try:
                    invalid = False
                    # fake data for the first run
                    trs = [i for i in range(100)]
                    index = 1
                    while len(trs) == MAX_FIGHTS:
                        page = requests.get(
                            f"https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-{organization_index}/recent-events/{index}"
                        )
                        soup = BeautifulSoup(page.content, features="html.parser")

                        section_title_el = soup.find("div", class_="tiled_bg latest_features")
                        if not section_title_el:
                            trs = [0]
                            invalid = True
                            break
                        if "ERROR 404" in section_title_el.get_text():
                            trs = [0]
                            invalid = True
                            continue

                        organization_fullname = soup.find("section").find_all("div", itemprop="name")[0].get_text()
                        recent_event_el = soup.find("div", id="recent_tab")

                        trs = recent_event_el.find_all("tr")[1:]
                        for tr in trs:
                            fight_date = tr.find("meta", itemprop="startDate").get("content", "")
                            url = tr.find("a", itemprop="url").get("href", "")
                            event_index = int(url.split("-")[-1])
                            event_name = tr.find("span", itemprop="name").get_text()
                            location = tr.find("td", itemprop="location").get_text().strip()
                            # event index
                            json.dump(
                                {
                                    "fight_date": fight_date,
                                    "url": url,
                                    "event_name": event_name,
                                    "location": location,
                                    "event_index": event_index,
                                    "organization_index": organization_index,
                                },
                                events_file,
                            )
                            events_file.write("\n")
                        index += 1
                    if not invalid:
                        # save fighter and fights to selected JSONs
                        json.dump(
                            {"organization_index": organization_index, "fullname": organization_fullname},
                            organization_file,
                        )
                        organization_file.write("\n")
                        print(f"Processed organization with the index = {organization_index}")
                    organization_index += 1
                except Exception:
                    print(
                        f"Scrapping of document {organization_index} failed with the following message:\n{traceback.format_exc()}"
                    )
                    # find different working proxy
                    proxy_session = None
                    if fail_cnt % 3 == 0:
                        print(f"Skip fighter with index {organization_index}")
                        organization_index += 1
                    fail_cnt += 1


def scrape_all_fighters(scrape_fighters_cnt: int, fighters_filename: str, fights_filename: str) -> None:
    """
    Scrapes information about all fighters in Sherdog's database and saves them into csv or json file.
    :param filetype: string with either 'csv' or 'json' as a type of file where results will be stored
    :return: None
    """
    # proxies = Proxies()
    # proxy_session = proxies.get_proxy()
    proxy_session = None
    fighter_index = 472993
    fail_cnt = 0
    with open(fighters_filename, "a") as fighter_file:
        with open(fights_filename, "a") as fights_file:
            # when downloading specific fighter fails more then 5 times interrupt scrapping
            while (fighter_index <= 500000) and (fail_cnt <= 900):
                try:
                    # get fighter on a given index
                    fighter_obj = Fighter(proxy_session=proxy_session, fighter_index=fighter_index, download=True)
                    if fighter_obj.valid:
                        # get fights of a given fighter
                        fights = Fight.get_fights(
                            soup_obj=fighter_obj.soup_obj, fighter_a_index=fighter_obj.fighter_index
                        )
                        # save fighter and fights to selected JSONs
                        json.dump(fighter_obj.to_dict(), fighter_file)
                        fighter_file.write("\n")
                        for fight in fights:
                            json.dump(fight.to_dict(), fights_file)
                            fights_file.write("\n")
                    fail_cnt = 0
                    fighter_index += 1
                    print(f"Processed fighter with the index = {fighter_index}")
                except Exception:
                    print(
                        f"Scrapping of document {fighter_index} failed with the following message:\n{traceback.format_exc()}"
                    )
                    # find different working proxy
                    proxy_session = None
                    if fail_cnt % 3 == 0:
                        print(f"Skip fighter with index {fighter_index}")
                        fighter_index += 1
                    fail_cnt += 1


if __name__ == "__main__":
    """
    scrape_all_fighters(
        scrape_fighters_cnt=1000, fighters_filename="data/fighters.jsonl", fights_filename="data/fights.jsonl"
    )
    """
    scrape_all_organizations(organization_filename="data/organizations.jsonl", events_filename="data/events.jsonl")
