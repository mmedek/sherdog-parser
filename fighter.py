import requests
import datetime

from pprint import pformat
from typing import Optional, Any, List, Iterable

from bs4 import BeautifulSoup

from fight import Fight

class Fighter(object):
    """Fighter class - creates fighter instance based on fighter's Sherdog profile or a given parameters."""

    DEFAULT_INDEX: int = -1

    def __init__(
        self,
        fighter_index: int = DEFAULT_INDEX,
        download: bool = False,
        url: Optional[str] = None,
        fullname: Optional[str] = None,
        nickname: Optional[str] = None,
        birth_date: Optional[Any] = None,
        weight_kg: Optional[str] = None,
        height_cm: Optional[str] = None,
        locality: Optional[str] = None,
        nationality: Optional[str] = None,
        associations: Optional[List[str]] = None,
        weight_class: Optional[str] = None,
        style: Optional[str] = None,
    ) -> None:
        """
        Initializes a Fighter instance.
        """
        self.fighter_index = fighter_index
        self.url = url
        self.fullname = fullname
        self.nickname = nickname
        self.birth_date = birth_date
        self.weight_kg = weight_kg
        self.height_cm = height_cm
        self.locality = locality
        self.nationality = nationality
        self.associations = associations
        self.weight_class = weight_class
        self.style = style

        if download:
            soup_obj = self.scrape_stats()
            fights = Fight.get_fights(soup_obj=soup_obj, fighter_a_index=self.fighter_index)
            print(fights)

    def scrape_stats(self) -> Any:
        """
        Scrape all statistics about Fighter and fill fighter instance.
        """
        self.url = f"https://www.sherdog.com/fighter/index?id={self.fighter_index}"
        fighter_page = requests.get(self.url)
        page_content = fighter_page.content
        soup_obj = BeautifulSoup(page_content, features="html.parser")
        # fill up Fighter instance with data mentioned on Sherdog
        self.fullname = self.get_attribute_by_class(soup_obj, "fn")
        self.nickname = self.get_attribute_by_class(soup_obj, "nickname")
        self.nationality = soup_obj.find("strong", itemprop="nationality").get_text()
        self.locality = self.get_attribute_by_class(soup_obj, "locality")
        birth_date, height_cm, weight_kg = self.get_personal_stats(soup_obj)
        self.birth_date = birth_date
        self.weight_kg = weight_kg
        self.height_cm = height_cm

        self.associations = self.get_associations(soup_obj)
        self.weight_class = self.get_weight_class(soup_obj)
        self.style = self.get_style(soup_obj)

        return soup_obj

    def get_style(self, soup_obj: Any) -> Optional[str]:
        """"
        Get style from Soup object.
        :param soup_obj: Soup object representing Fighter page.
        :return: Style of fighter if exists.
        """
        style_el = (
            soup_obj
            .find("div", class_="association-class")
            .select_one("b")
        )

        if not style_el:
            return None

        return style_el.get_text()

    def get_weight_class(self, soup_obj: Any) -> Optional[str]:
        """"
        Get weight class from Soup object.
        :param soup_obj: Soup object representing Fighter page.
        :return: Weight-class of fighter if exists.
        """
        weight_class_el = (
            soup_obj
            .find("div", class_="association-class")
            .select_one("a[href*=/stats/fightfinder?weightclass]")
        )

        if not weight_class_el:
            return None

        return weight_class_el.get_text()

    def get_associations(self, soup_obj: Any) -> List[str]:
        """"
        Get associations from Soup object.
        :param soup_obj: Soup object representing Fighter page.
        :return: List of found associations.
        """
        associtions = list()
        associtions_candidates = soup_obj.find("div", class_="association-class").find_all("span", itemprop="memberOf")
        for candidate in associtions_candidates:
            associtions.append(candidate.get_text())
        return associtions

    def get_normalized_data(self, date_str: str) -> str:
        """
        Get ISO format date from date format used by Sherdog
        Apr 18, 1973 -> 1973-04-18T00:00:00
        :param date_str: date in Sherdog format
        :return: date in ISO-1 format
        """
        datetime_obj = datetime.datetime.strptime(date_str, "%b %d, %Y")
        return datetime_obj.isoformat()

    def get_personal_stats(self, soup_obj: Any) -> Iterable[Any]:
        """
        Get birth date, weight in kgs and height cms (in ugly and not error prune way)
        :param date_str: Soup object representing Fighter page.
        :return: Tuple with birth_date, height_cm, weight_cm values if exists otherwise with 
        """
        stats_table_el = soup_obj.find("div", class_="bio-holder")
        if not stats_table_el:
            return tuple([None, None, None])
        trs = stats_table_el.find_all("tr")
        # all stats in format X / Y\n and I am interested in the second value
        # first processed row is about age / birth date
        birth_date_str = trs[0].get_text()
        birth_date = None
        if "N/A" not in birth_date_str:
            birth_date = self.get_normalized_data(birth_date_str.split("/")[-1].replace("\n", "").strip())
        # second row is about height ' / height cm
        height_str = trs[1].get_text()
        height_cm = None
        if "N/A" not in height_str:
            height_cm = float(height_str.split("/")[-1].replace("\n", "").replace("cm", "").strip())
        # third row is about weight lbs / height kg
        weight_str = trs[2].get_text()
        weight_cm = None
        if "N/A" not in weight_str:
            weight_cm = float(weight_str.split("/")[-1].replace("\n", "").replace("kg", "").strip())
        return tuple([birth_date, height_cm, weight_cm])

    def get_attribute_by_class(self, soup_obj: Any, class_name: str) -> Optional[str]:
        """
        Collects and returns attribute from fighter info if exists.
        :return: Fighter attribute or None.
        """
        attr_el = soup_obj.find("span", class_=class_name)
        attr_val = None
        if attr_el:
            attr_val = attr_el.get_text()
        return attr_val

    def __repr__(self) -> str:
        return pformat(vars(self), indent=4, width=1)
