import json
from functools import wraps

from imports import *


class State:
    driver: WebDriver

    
    
driver = State.driver = webdriver.Chrome()


url = "https://www.atptour.com/en/scores/stats-centre/live/2024/6242/MS005?tab=CourtVision"


def save_as_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Call the original function
        result = func(*args, **kwargs)

        # Prepare the filename using the function's name
        filename = f"{func.__name__}.json"

        # Save the result as a JSON file with indent=4
        with open(filename, "w") as f:
            json.dump(result, f, indent=4)

        # Return the original result
        return result

    return wrapper


def expand_all():
    try:
        State.driver.find_element(By.XPATH, r"//button[text()='Expand All (X+E)']").click()
    except NoSuchElementException:
        pass


def cookies_ok():
    try:
        State.driver.find_element(By.XPATH, r"//a[text()='Continue']").click()
    except (NoSuchElementException, ElementNotInteractableException):
        pass


def scroll_to_the_header():
    scroll_to(State.driver.find_element(By.ID, "tabCourtVision"))


def scroll_to(el: WebElement, align_to_bottom: bool = True):
    State.driver.execute_script(
        f"arguments[0].scrollIntoView({str(align_to_bottom).lower()});", el
    )




def delete_cache():
    State.driver.execute_script("window.open('')")  # Create a separate tab than the main one
    State.driver.switch_to.window(
        State.driver.window_handles[-1]
    )  # Switch window to the second tab
    time.sleep(2)
    State.driver.get("chrome://settings/clearBrowserData")  # Open your chrome settings.
    time.sleep(1)

    with open("findClearButton.js") as f:
        findClearButton = f.read()
    with open("findDeleteBrowserData.js") as f:
        findDeleteBrowserData = f.read()

    try:
        State.driver.execute_script(findClearButton).click()
    except (
        AttributeError,
        ElementNotInteractableException,
        NoSuchElementException,
        ElementClickInterceptedException,
    ):
        State.driver.execute_script(findDeleteBrowserData).click()
        time.sleep(1)
        State.driver.execute_script(findClearButton).click()

    State.driver.close()  # Close that window
    State.driver.switch_to.window(
        State.driver.window_handles[0]
    )  # Switch Selenium controls to the original tab to continue normal functionality.


def safe_get(url: str):    
    State.driver.get(url)
    time.sleep(5)

    verifyThatYouAreHuman = State.driver.find_elements(
        By.XPATH, r"//h2[contains(text(), 'you are human')]"
    )
    if verifyThatYouAreHuman:
        print("verification")
        
        try:
            delete_cache()
            State.driver.refresh()
        except Exception:
            print('HARD RELOAD')
            
            try:
                while State.driver.window_handles:
                    State.driver.switch_to.window(
                        State.driver.window_handles[-1]
                    )
                    State.driver.close()
            except Exception:
                pass
            
            del State.driver
            
            State.driver = webdriver.Chrome()
            State.driver.get(url)
            
        time.sleep(5)
    else:
        print("no verification")
    cookies_ok()


State.driver.maximize_window()
# State.driver.get(url)

# time.sleep(1)
# State.driver.fullscreen_window()
# time.sleep(3)


if __name__ == "__main__":
    driver.get('https://example.com')
    safe_get('https://google.com')
    # parse_course_vision()
