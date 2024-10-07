from __future__ import annotations

from typing import Mapping, TypedDict

from atptour import *


class StrokeSummary(TypedDict):
    strokes: list[Stroke]


class Stroke(TypedDict):
    strokeLabel: str
    player1: Hands
    player2: Hands


class Hand(TypedDict):
    backhand: int
    forehand: int


class Hands(Mapping[str, Hand]):
    winners: Hand
    forcingShots: Hand
    unforcedErrors: Hand
    ralliesContinued: Hand


handsLabes = ["winners", "forcingShots", "unforcedErrors", "ralliesContinued"]

@save_as_json
@verify_resistant
def parse_stroke_summary() -> StrokeSummary:
    time.sleep(2)
    driver.find_element(By.XPATH, r"//button[text()='Stroke Summary']").click()
    time.sleep(1)
    
    
    data: StrokeSummary = {"strokes": []}

    stats_wrapper = driver.find_element(By.CLASS_NAME, r"stats-wrapper")
    strokes = stats_wrapper.find_elements(By.XPATH, "./*")
    len(strokes)

    if "expand all" in driver.find_element(By.CLASS_NAME, "expand-all").text.lower():
        driver.find_element(By.CLASS_NAME, "expand-all").click()

    for stroke in strokes:
        strokeData: Stroke = {}
        strokeData["strokeLabel"] = stroke.find_element(
            By.XPATH, ".//div[@class='stroke-label-us']"
        ).text

        for player, i in (("player1", 1), ("player2", 3)):
            handsData: Hands = {}

            for hand, label in zip(
                stroke.find_elements(
                    By.XPATH, rf"./div/div[1]/div[1]/div[2]/div/div[3]/div[{i}]/div/*"
                ),
                handsLabes,
            ):
                backhand, forehand = map(
                    int,
                    " ".join(
                        el.text for el in hand.find_elements(By.XPATH, "./span")
                    ).split(),
                )
                handsData[label] = {"backhand": backhand, "forehand": forehand}

            strokeData[player] = handsData
        data["strokes"].append(strokeData)
    return data

if __name__ == "__main__":
    parse_stroke_summary()
