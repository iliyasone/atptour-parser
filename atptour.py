from imports import *

driver = webdriver.Chrome()


url = 'https://www.atptour.com/en/scores/stats-centre/live/2024/6242/MS005?tab=CourtVision'

import json
from functools import wraps

def save_as_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Call the original function
        result = func(*args, **kwargs)
        
        # Prepare the filename using the function's name
        filename = f"{func.__name__}.json"
        
        # Save the result as a JSON file with indent=4
        with open(filename, 'w') as f:
            json.dump(result, f, indent=4)
        
        # Return the original result
        return result
    
    return wrapper


def expand_all():
    try:
        driver.find_element(By.XPATH, r"//button[text()='Expand All (X+E)']").click()
    except NoSuchElementException:
        pass


def cookies_ok():
    try:
        driver.find_element(By.XPATH, r"//a[text()='Continue']").click()
    except (NoSuchElementException, ElementNotInteractableException):
        pass
    
    
driver.get(url)

driver.maximize_window()
time.sleep(1)
driver.fullscreen_window()
time.sleep(3)


cookies_ok()

def parse_course_vision():
    driver.get(url)
    time.sleep(3)
    driver.find_element(By.XPATH, "//button[text()='2D']").click()
    
    
    court_balls = driver.find_elements(By.XPATH, "//*[local-name()='g' and starts-with(@class, 'court-ball-')]")
    
    for court_ball in court_balls:
        ...
    
    
if __name__ == '__main__':
    parse_course_vision()