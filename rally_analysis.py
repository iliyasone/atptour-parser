from __future__ import annotations
from typing import TypedDict

from atptour import *


class RallyAnalysis(TypedDict):
    shortRally: list[Shot]
    mediumRally: list[Shot]
    longRally: list[Shot]
    
class Shot(TypedDict):
    i: int
    label: str
    player1: Point
    player2: Point
        
class Point(TypedDict):
    type: str
    count: int

def parse_rally_analysis() -> RallyAnalysis:
    driver.find_element(By.XPATH, r"//button[text()='Rally Analysis']").click()
    time.sleep(2)
    expand_all()
    time.sleep(2)
    
    data: RallyAnalysis = {}

    shortRally = driver.find_element(By.ID, "shortRally")
    mediumRally = driver.find_element(By.ID, "mediumRally")
    longRally = driver.find_element(By.ID, "longRally")

    rallies = [shortRally, mediumRally, longRally]
    ralliesLabels = ['shortRally', 'mediumRally', 'longRally']
    
    
    for rally, rally_label in zip(rallies, ralliesLabels):
        shots = rally.find_elements(By.XPATH, r"./div/div[4]/div[2]/div[2]/*")
        data[rally_label] = []
        
        for i, shot in enumerate(shots):
            shotData: Shot = {}
            
            player1, shot_label, player2 = shot.find_elements(By.XPATH, './*')
            
            shotData['i'] = i
            shotData['label'] = shot_label.find_element(By.XPATH, r"./div").text
            
            for player, playerLabel in ((player1, 'player1'), (player2, 'player2')):
                shotData[playerLabel] = []    
                
                points = player.find_elements(By.XPATH,'./div')
                for point in points:
                    count, type = point.find_element(By.XPATH, r'./div/div').text.split('\n')
                    point: Point = {'count': int(count), 'type': type}
                    shotData[playerLabel].append(point)
            
            data[rally_label].append(shotData)
    with open('rally_analysis.json', mode='w') as file:
        json.dump(data, file, indent=4)
    
    return data

if __name__ == '__main__':
    parse_rally_analysis()