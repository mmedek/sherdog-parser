import datetime

from pprint import pformat
from typing import Any, Optional, List, Dict


class Fight(object):
    """Fight class - creates fight instance with data about the fight - winner, referee, etc."""

    FIGHT_TYPES = ["FIGHT HISTORY - PRO", "FIGHT HISTORY - PRO EXHIBITION", "FIGHT HISTORY - AMATEUR"]

    def __init__(
        self,
        fighter_a_index: int = -1,
        fighter_b_index: int = -1,
        event_index: int = -1,
        date: Optional[str] = None,
        referee: Optional[str] = None,
        general_decision: Optional[str] = None,
        specific_decision: Optional[str] = None,
        round: int = -1,
        specific_time: int = -1,
        title_fight: bool = False,
        weight_class: Optional[str] = None,
        fight_type: str = None,
        result: Optional[str] = None,
    ) -> None:

        self.fighter_a_index = fighter_a_index
        self.fighter_b_index = fighter_b_index
        self.date = date
        self.event_index = event_index
        self.referee = referee
        self.general_decision = general_decision
        self.specific_decision = specific_decision
        self.specific_time = specific_time
        self.round = round
        self.title_fight = title_fight
        self.weight_class = weight_class
        self.fight_type = fight_type
        self.result = result

    @staticmethod
    def convert_to_seconds(str_time: str) -> int:
        try:
            minutes_seconds_arr = str_time.split(":")
            if len(minutes_seconds_arr) < 2:
                return -1
            seconds = int(minutes_seconds_arr[0]) * 60
            seconds += int(minutes_seconds_arr[1])
        except:
            # N/A
            return -1
        return seconds

    @staticmethod
    def get_fight_from_row(tds: List[Any]) -> Any:
        result = tds[0].get_text()
        # get opponent index from <a href="/fighter/Mabelly-Lima-187177">Mabelly Lima</a>
        opponent_index = tds[1].a["href"].split("-")[-1]
        event_index = tds[2].a["href"].split("-")[-1]
        date_str_el = tds[2].find("span", class_="sub_line")
        date_str = None
        if date_str_el:
            try:
                date_str = datetime.datetime.strptime(date_str_el.get_text(), "%b / %d / %Y")
            except:
                print(f"Failed to get date of fights from {date_str_el.get_text()}")
        win_by = tds[3].find("b").get_text().split("(")[0].strip()
        # get reason of fight stoppage from <td class="winby"><b>KO (Punches)</b><br/><span class="sub_line"></span></td>
        win_by_specific_el = tds[3].find("b")
        win_by_specific_str = None
        if "(" in win_by_specific_el.get_text():
            win_by_specific_str = win_by_specific_el.get_text().split("(")[-1].replace(")", "").strip()
        win_by_specific = win_by_specific_str
        # <a href="/referee/Dan-Miragliotta-21">Dan Miragliotta</a>
        referee = None
        if tds[3].span.get_text():
            referee = tds[3].span.get_text()
        round_ = int(tds[4].get_text())
        time = Fight.convert_to_seconds(tds[5].get_text())

        return Fight(
            fighter_b_index=int(opponent_index),
            date=date_str.isoformat() if date_str else None,
            event_index=int(event_index),
            referee=referee,
            general_decision=win_by,
            specific_decision=None if win_by_specific == "N/A" else win_by_specific,
            round=-1 if round_ == "0" else int(round_),
            specific_time=time,
            result=result,
        )

    @staticmethod
    def get_fights(soup_obj: Any, fighter_a_index: int) -> List[Any]:

        fights = list()
        section_els = soup_obj.find_all("section")[1:]
        for section in section_els:
            for fight_type in Fight.FIGHT_TYPES:
                fight_type_str = fight_type.split("-")[-1].strip()
                if fight_type in section.get_text():
                    trs = section.find_all("tr")[1:]
                    for tr in trs:
                        tds = tr.find_all("td")
                        fight = Fight.get_fight_from_row(tds)
                        fight.fight_type = fight_type_str
                        fight.fighter_a_index = fighter_a_index
                        fights.append(fight)
        return fights

    def __repr__(self) -> str:
        return pformat(vars(self), indent=4, width=1)

    def to_dict(self) -> Dict[str, Optional[Any]]:
        """
        Build Dictionary from Fight object.
        :return: dictionary with parameters of Fight object.
        """
        return {
            "fighterIndexA": self.fighter_a_index,
            "fighterIndexB": self.fighter_b_index,
            "eventIndex": self.event_index,
            "date": self.date,
            "weightClass": self.weight_class,
            "fightType": self.fight_type,
            "referee": self.referee,
            "result": self.result,
            "generalDecision": self.general_decision,
            "specificDecision": self.specific_decision,
            "specificTime": self.specific_time,
            "round": self.round,
            "titleFight": self.title_fight,
        }
