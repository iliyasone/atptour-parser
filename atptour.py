from imports import *

driver = webdriver.Chrome()

driver.maximize_window()

url = 'https://www.atptour.com/en/scores/stats-centre/live/2024/6242/MS005?tab=CourtVision'


def expand_all():
    try:
        driver.find_element(By.XPATH, r"//button[text()='Expand All (X+E)']").click()
    except NoSuchElementException:
        pass


def cookies_ok():
    try:
        driver.find_element(By.XPATH, r"//a[text()='Continue']").click()
    except NoSuchElementException:
        pass

driver.get(url)
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