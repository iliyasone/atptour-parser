from __future__ import annotations

from typing import Literal, TypedDict, Optional

from atptour import *

class Games(TypedDict):
    games: list[Games]

class Game(TypedDict):
    id: str
    whoServes: str
    serves: list[Serve]

    duration: str
    setScore: tuple[int, int]

class Serve(TypedDict):
    type: Literal['1','2', 'A', 'A (2)', 'D']
    info: str
    speed: str
    gameScore: tuple[str, str]
    rallyLength: Optional[int]

def click_serve_button():
    serve_button = driver.find_elements(By.CLASS_NAME, 'dropdown-item')[-1]
    serve_button.click()

def _get_options():
    return driver.find_element(By.CLASS_NAME, "sublink-container").find_elements(By.XPATH, './*')

def both() -> list[Games]:    
    games: list[Game] = []
    for game_block in driver.find_elements(By.CLASS_NAME, 'game-block'):
        scroll_to(game_block, align_to_bottom=False)
        duration = game_block.find_element(By.XPATH,
                        r"./*[contains(@class, 'Card-wrapper')]" 
                        r"//span[@class='duration dur-black']"
                        ).text

        setScore = game_block.find_element(By.XPATH, 
                            r"./*[contains(@class, 'Card-wrapper')]"
                            r"/div[contains(@class, 'score-container')]").text.split('\n')

        game: Game = {
            'id' : game_block.get_attribute('id'),
            # 'whoServes': player1
            'serves': [],

            
            'duration': duration,
            'setScore': setScore,
            }

        gs = game_block.find_elements(By.XPATH, 
                r"./*[contains(@class, 'game-wrapper')]"
                r"/*[local-name()='g']"
                # r"[contains(@class, 'serve-speed-graph-wrapper')]"
                # r"/*[local-name()='g']"
                # r"[contains(@class, 'serve-spd')]"
                )
        

        
        for g in gs:
            game_score = g.text.split('\n')
            
            ActionChains(driver).move_to_element(g).perform()

            serve: Serve = {'gameScore': 
                            list(filter(
                lambda item: 
                    item.isdigit() or item == 'Game',
                game_score)
                )}

            try:
                rally_length = driver.find_element(By.XPATH, 
                                r"//span[contains(text(), 'Rally length')]/.."
                                r"/span[@class='mb-data-value']").text
                try:
                    info = driver.find_element(By.CLASS_NAME, 'Info').text
                except NoSuchElementException:
                    info = ''

                
                serve['rallyLength'] =rally_length
                serve['info'] = info
            except NoSuchElementException:
                try:
                    serve['speed'] = driver.find_element(By.CLASS_NAME, 'KphSpeed').text
                    serve['type'] = 'A'
                except NoSuchElementException:
                    # Break point convert
                    continue
            game['serves'].append(serve)

        games.append(game)
    return games

    # [g.get_attribute('id') for g in gs]

def join_with_player_data(
        player: str, 
        player_number: Literal[1, 2], 
        games: list[Games]
        ) -> None:
    
    click_serve_button() # open options
    _get_options()[player_number].click() # click to the player name
    

    for game_block in driver.find_elements(By.CLASS_NAME, 'game-block'):
        scroll_to(game_block, align_to_bottom=False)
        id = game_block.get_attribute('id')
        circles = game_block.find_elements(By.XPATH, 
            r"./*[contains(@class, 'game-wrapper')]"
            r"/*[local-name()='g']"
            r"[contains(@class, 'serve-speed-graph-wrapper')]"
            r"/*[local-name()='g']"
            r"[contains(@class, 'serve-spd')]"
            )
        
        for game in games:
            if id == game["id"]:
                break
        else: #nonbreak
            raise ValueError(f"Didn't find game {id} in both player view")
        
        for g, serve in zip(circles, game["serves"]):
            ActionChains(driver).move_to_element(g).perform()
            type, speed = g.text, driver.find_element(By.CLASS_NAME, 'KphSpeed').text
            
            if 'type' in serve and serve['type'] != type:
                print(id, type, serve['type'])
                serve['type'] = f"{serve['type']} ({type})"
            else:
                serve['type'] = type
            serve["speed"] = speed
        
        game["whoServes"] = player
        
    click_serve_button() # return to both


@save_as_json
def parse_matchbeats() -> Games:
    driver.find_element(By.XPATH, r"//button[text()='MatchBeats']").click()

    games = both()

    player1, _, player2, _ = driver.find_element(By.CLASS_NAME, 'player-name-block').text.split('\n')

    for player, playerNumb in ((player1, 1), (player2, 2)):
        join_with_player_data(player1, playerNumb, games)

    return {'games' : games}

def test():
    safe_get(url)
    parse_matchbeats()

if __name__ == '__main__':
    test()