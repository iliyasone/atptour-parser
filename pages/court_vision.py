from __future__ import annotations

import re

from atptour import *
from pages.court_vision_models import *


def to_camel_case(_s: str, /) -> str:
    # Split the string into words
    if not _s:
        return ""

    words = _s.split()

    # Convert the first word to lowercase and keep the rest of the words capitalized
    camel_case = words[0].lower() + "".join(word.capitalize() for word in words[1:])

    return camel_case


def format_description(input_string):
    # Remove brackets and numbers inside
    formatted_string = re.sub(r"\s*\([^)]*\)", "", input_string)
    # Capitalize each word
    capitalized_string = formatted_string.title()
    return capitalized_string.strip()


def to_real_pos(x: float, y: float, width: float, height: float, court: CourtType):
    x_real = (x / width + 0.5) * court.widthM
    y_real = (0.5 - y / height) * court.heightM

    return x_real, y_real


def sibling_of_div_text(s: str, /):
    s = s.replace("*", "")
    return driver.find_element(
        By.XPATH,
        rf"//div[contains(normalize-space(text()), '{s}')]/following-sibling::div[@class]",
    )


def scroll_to_the_court():
    scroll_to(driver.find_element(By.CLASS_NAME, "match-timeline-wrapper"))


def move_foreground(el: WebElement):
    driver.execute_script("arguments[0].parentNode.appendChild(arguments[0]);", el)


def extract_first_number(string: str, /):
    numbers = re.findall(r"-?\d+\.\d+|-?\d+", string)
    # Convert the first found number to a float and return it
    if numbers:
        return float(numbers[0])
    return None


def get_selected_group_elements():
    return driver.find_element(By.ID, "plottedBallsSelected")


def get_balls(passed_balls: set[str], court: CourtType) -> list[Ball]:
    """assume that a ball was clicked"""
    height, width = driver.find_element(
        By.XPATH, '//*[@id="CourtDoublesAlley"]'
    ).size.values()
    selected = get_selected_group_elements()

    selected_balls = selected.find_elements(By.XPATH, r".//*[local-name()='g']")
    balls: list[Ball] = []
    for ballEl in selected_balls:
        passed_balls.add(ballEl.get_attribute("class").strip())

        components = ballEl.find_elements(By.XPATH, r"./*")
        angle = None
        while len(components) > 1:
            for component in components:
                if component.get_attribute("transform") is not None:
                    angle = extract_first_number(component.get_attribute("transform"))
                    components.remove(component)
        if len(components) == 1:
            component = components[0]
            xlinkhref = component.get_attribute("xlink:href")
            typ = xlinkhref.replace("#", "").replace("Selected", "")

            x, y = component.get_attribute("x"), component.get_attribute("y")
            x, y = to_real_pos(float(x), float(y), width, height, court)
            balls.append(
                {
                    "x": x,
                    "y": y,
                    "type": typ,
                    "cls": ballEl.get_attribute("class").strip(),
                }
            )

            if angle:
                balls[-1]["rotate"] = angle

    return balls


def get_curret_score_from_pop_up():
    """assume that a ball was clicked"""

    game_scores = driver.find_element(By.CLASS_NAME, "game-scores").text.split("\n")
    set_score_1 = tuple(
        map(int, driver.find_element(By.CLASS_NAME, "set-scores-1").text.split("\n"))
    )

    try:
        set_score_2 = tuple(
            map(
                int, driver.find_element(By.CLASS_NAME, "set-scores-2").text.split("\n")
            )
        )
    except:
        set_score_2 = None, None

    currentScore: CurrentScore = {
        "player1": {
            "game_score": game_scores[0],
            "set_score_1": set_score_1[0],
            "set_score_2": set_score_2[0],
        },
        "player2": {
            "game_score": game_scores[1],
            "set_score_1": set_score_1[1],
            "set_score_2": set_score_2[1],
        },
    }

    return currentScore


def get_selected_shot(passed_balls: set[str], court: CourtType) -> Shot:
    """assume that a ball was clicked"""

    try:
        shot_description = format_description(
            driver.find_element(By.CLASS_NAME, "shot-description").text
        )
        player, typ = shot_description.lower().replace(" ", "").split("'s")
    except:
        shot_description = ""
        player = ""
        typ = format_description("NOT AVALIABLE")

    shot_description, player, typ

    shot: Shot = {"shotDescription": shot_description, "player": player, "type": typ}

    # get all attributes
    attributes = {}

    elements = driver.find_elements(
        By.XPATH, "//div[@class='header' and normalize-space(text())]"
    )
    for element in elements:
        key = to_camel_case(element.text)
        value = sibling_of_div_text(element.text).text

        if value == "NA":

            value = None
        attributes[key] = value

    shot["attributes"] = attributes
    try:
        shot["currentScore"] = get_curret_score_from_pop_up()
    except ValueError:
        shot["currentScore"] = {}
    shot["balls"] = get_balls(passed_balls, court)

    return shot


def get_all_current_shots(passed_balls: set[str] | None = None) -> list[Shot]:
    current_shots: list[Shot] = []

    court_balls = lambda: driver.find_elements(
        By.XPATH, "//*[local-name()='g' and starts-with(@class, 'court-ball-')]"
    )

    passed_balls: set[str] = passed_balls or set()
    for i in range(len(court_balls())):
        court_ball = court_balls()[i]

        cls = court_ball.get_attribute("class").strip()
        if cls in passed_balls:
            continue

        passed_balls.add(cls)

        scroll_to_the_court()

        try:
            court_ball.click()
        except ElementClickInterceptedException as e:
            move_foreground(court_ball)
            court_ball.click()

        current_shots.append(get_selected_shot(passed_balls, Court))

        try:
            get_selected_group_elements().find_element(By.XPATH, r"./*")
        except NoSuchElementException:
            court_ball.click()
            continue

        for el_to_close in get_selected_group_elements().find_elements(
            By.XPATH, r".//*[local-name()='g']"
        ):
            try:
                el_to_close.click()
                break
            except ElementClickInterceptedException:
                pass
        else:
            print("Element was not closed")

        time.sleep(0.2)
    return current_shots


def options_stable_iterator():
    start_index = -1
    while True:
        start_index += 1
        scroll_to_the_header()
        stroke_dropdown = driver.find_element(
            By.XPATH, "//div[contains(@class, 'DropdownFixWidth')]"
        )

        options_fact = lambda: stroke_dropdown.find_elements(
            By.XPATH,
            "./div[@id='RGDropDown']/div[@class='dropdown-container']/div[@class='sublink-container']/*",
        )
        options = options_fact()
        if len(options) == 0:
            stroke_dropdown.click()
            time.sleep(1)
            options = options_fact()

        if start_index < len(options):
            yield options[start_index]
        else:
            break


@save_as_json
@verify_resistant
def parse_court_vision() -> CourtVision:
    driver.implicitly_wait(1)

    driver.find_element(By.ID, "tabCourtVision").click()
    time.sleep(5)

    data: CourtVision = {"players": [], "court": Court.to_dict()}
    driver.find_element(By.XPATH, "//button[text()='2D']").click()

    player1, player2 = driver.find_elements(By.CLASS_NAME, "playerName")[:2]

    for player, playerIndex in ((player1, 1), (player2, 2)):
        print(f"player {playerIndex}")
        scroll_to_the_header()
        player.click()

        playerDict: Player = {
            "player": player.text,
            "playerIndex": playerIndex,
            "sets": [],
        }

        for current_set in (1, 2):
            print(f"player {playerIndex}, set {current_set}")
            set_: Set = {"set": current_set, "shotsTypes": []}

            scroll_to_the_header()
            time.sleep(1)
            mathes_option = driver.find_element(By.CLASS_NAME, "SetCustomDropdown")
            mathes_option.click()
            time.sleep(1)
            mathes_option.find_elements(
                By.XPATH,
                "./div[@id='RGDropDown']/div[@class='dropdown-container']/div[@class='sublink-container']/*",
            )[current_set].click()
            time.sleep(7)

            for option in options_stable_iterator():
                label = format_description(option.text)
                print(label)
                option.click()

                time.sleep(0.2)
                shots: Shots = {
                    "label": label,
                    "shots": get_all_current_shots(),
                }

                print(f"found {len(shots)} shots")
                set_["shotsTypes"].append(shots)

                playerDict["sets"].append(set_)
        data["players"].append(playerDict)
    return data
    # TODO:


if __name__ == "__main__":
    parse_court_vision()
