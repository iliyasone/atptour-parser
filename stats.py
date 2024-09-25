from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from atptour import *


class Stats(TypedDict):
    matchStats: list[StatBtn]
    YTDStats: StatBtn


class StatBtn(TypedDict):
    set: NotRequired[Literal[1, 2]]
    stats: list[StatsHeader]


class StatsHeader(TypedDict):
    header: str
    tiles: list[StatsTile]


class StatsTile(TypedDict):
    player1: str
    label: str
    player2: str


def scroll_to_header_button():
    scroll_to(driver.find_element(By.ID, "InfosysMatchCenter"))


def get_all_tiles() -> list[StatsHeader]:
    result: list[StatsHeader] = []

    for topStatsWrapper in driver.find_elements(By.CLASS_NAME, "topStatsWrapper"):
        stat_section = topStatsWrapper.find_element(
            By.XPATH, r"./div[contains(@class, 'stat-section')]"
        )

        statsTiles = stat_section.find_elements(By.XPATH, r"./*")

        statsWithHeader: StatsHeader = {"header": statsTiles[0].text, "tiles": []}

        for statTileWrapper in statsTiles[1:]:
            tile = tuple(
                el.text
                for el in statTileWrapper.find_element(By.XPATH, r"./*").find_elements(
                    By.XPATH, r"./*"
                )
            )
            statsTile: StatsTile = {
                "player1": tile[0],
                "label": tile[1],
                "player2": tile[2],
            }
            statsWithHeader["tiles"].append(statsTile)
        result.append(statsWithHeader)
    return result


def wait_loading():
    loading = (
        lambda: len(driver.find_elements(By.XPATH, "//span[text()='Loading Stats...']"))
        > 0
    )
    while loading():
        time.sleep(1)


@save_as_json
def parse_stats() -> Stats:
    stats: Stats = {"matchStats": []}

    scroll_to_header_button()
    driver.find_element(By.ID, "tabStats").click()

    wait_loading()

    driver.find_element(By.XPATH, r"//button[text()='MATCH STATS']").click()

    match = lambda: driver.find_element(By.XPATH, r"//div[@class='dd-label']")

    options = lambda: driver.find_elements(By.XPATH, r"//div[@class='dropdown-link']")

    for curr_set in (1, 2):
        match().click()
        options()[curr_set].click()

        stats["matchStats"].append({"set": curr_set, "stats": get_all_tiles()})

    driver.find_element(By.XPATH, r"//button[text()='YTD STATS']").click()

    stats["YTDStats"] = get_all_tiles()
    
    
    return stats

if __name__ == "__main__":
    parse_stats()
