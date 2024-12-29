from __future__ import annotations

from typing import TypedDict

from atptour import *


class Tournaments(TypedDict):
    tournaments: list[Tournament]


class Tournament(TypedDict):
    name: str
    location: str
    date: str
    year: int
    matches: list[Match]


class Match(TypedDict):
    arena: str
    duration: str
    link: str
    notes: str
    isParsed: Parsed


class Parsed(TypedDict):
    stats: bool
    matchBeats: bool
    courtVision: bool
    rallyAnalysis: bool
    strokeSummary: bool


from typing import Literal

CHEVRON_TYPE = Literal["chevron ", "icon-chevron-"]
DIRECTION = Literal["down", "up"]


def toggle(chevron: CHEVRON_TYPE = "chevron ", direction: DIRECTION = "down"):

    xpath = rf"//span[@class='{chevron}{direction}']/."
    toggled = State.driver.find_elements(By.XPATH, xpath)
    while toggled:
        scroll_to(toggled[0], align_to_bottom=False)
        toggled[0].click()
        toggled = State.driver.find_elements(By.XPATH, xpath)


toggle()


def save_tournaments():
    url = "https://www.atptour.com/en/tournaments"
    State.driver.get(url)

    tournaments = []
    for el in State.driver.find_elements(By.CLASS_NAME, "non-live-cta"):
        link = el.find_element(By.XPATH, "./*").get_attribute("href")
        if link:
            tournaments.append(link)

    with open("temp/tournaments.txt", "w") as file:
        file.write("\n".join(tournaments))


def is_apt_tournament():
    logo_name = (
        State.driver.find_element(By.XPATH, r"//div[@class='badge']/*")
        .get_attribute("src")
        .split("/")[-1]
        .split(".")[0]
    )
    if logo_name.isnumeric():
        return True
    return False

def accept_cookies():
    try:
        driver.find_element(By.XPATH, r"//button[text()='Accept All Cookies']").click()
    except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
        pass


@save_as_json
def traverse():
    result: Tournaments = {"tournaments": []}

    with open("temp/tournaments.txt", "r") as file:
        tournaments = file.readlines()

    for link in tournaments:

        safe_get(link)
        accept_cookies()
        tournament_name, info = State.driver.find_element(
            By.CLASS_NAME, "schedule"
        ).text.split("\n")
        location, date = map(str.strip, info.split("|"))
        date, year = date.split(",")
        year = int(year)

        tournament: Tournament = {
            "name": tournament_name,
            "date": date,
            "location": location,
            "year": year,
            "matches": [],
        }

        if not is_apt_tournament():
            print(tournament_name, "is not apt tournament")
            continue

        # expand all
        chevrons = State.driver.find_elements(By.CLASS_NAME, "icon-chevron-down")
        for chevron in chevrons[1:]:
            try:
                scroll_to(chevron, align_to_bottom=False)
                chevron.click()
            except (ElementClickInterceptedException, ElementNotInteractableException):
                pass

        for match in State.driver.find_elements(By.CLASS_NAME, "match"):
            
            try:
                link = match.find_element(
                    By.XPATH,
                    r"./div[@class='match-footer']/div[@class='match-cta']/a[text()='Stats']",
                ).get_attribute("href")
            except NoSuchElementException:
                # if no link 
                continue
                
            
            try:
                values = match.find_element(
                    By.XPATH, r"./div[@class='match-header']"
                ).text
                arena, duration = values.split("\n")
            except NoSuchElementException:
                arena = duration = ''
            except ValueError:
                arena = values[0]
                duration = 0
                
                
            try:
                date = match.find_element(
                    By.XPATH,
                    r"./ancestor::div[contains(@class, 'atp_accordion-item')]/div[@class='atp_accordion-header']",
                ).text
            except NoSuchElementException:
                date = ''
                
            try:
                notes = match.find_element(By.XPATH, r"./div[@class='match-notes']").text
            except NoSuchElementException:
                notes = ''
                
            
            tournament["matches"].append(
                {
                    "arena": arena,
                    "duration": duration,
                    "link": link,
                    "notes": notes,
                    "isParsed": {
                        "courtVision": False,
                        "matchBeats": False,
                        "rallyAnalysis": False,
                        "stats": False,
                        "strokeSummary": False,
                    },
                }
            )
        result["tournaments"].append(tournament)
    return result


if __name__ == '__main__':
    # save_tournaments()
    traverse()
