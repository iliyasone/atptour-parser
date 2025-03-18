import json
from functools import wraps

from imports import *


class State:
    driver: WebDriver


class AtptourException(Exception):
    pass

def get_driver() -> WebDriver:
    # import undetected_chromedriver as uc

    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Start in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    if platform.system() == 'Linux':
        chrome_options.add_argument("--no-sandbox")  # Needed for Linux environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome resource constraints
    chrome_options.add_argument("--window-size=1920,1080") 
    chrome_options.add_argument("--log-level=1")

    # chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    #                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 "
    #                             "Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


    return driver
    
State.driver = driver = get_driver()

if platform.system() == 'Linux':
    # jupyter console
    # does not proprely send KeyboardInterrupt
    # so we will do it ourself
    import signal

    def signal_handler(sig, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, signal_handler)


url = "https://www.atptour.com/en/scores/stats-centre/live/2024/6242/MS005?tab=CourtVision"


def save_as_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Call the original function
        result = func(*args, **kwargs)

        # Prepare the filename using the function's name
        filename = f"temp/{func.__name__}.json"

        # Save the result as a JSON file with indent=4
        with open(filename, "w") as f:
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


def scroll_to_the_header():
    scroll_to(driver.find_element(By.ID, "tabCourtVision"))


def scroll_to(el: WebElement, align_to_bottom: bool = True):
    driver.execute_script(
        f"arguments[0].scrollIntoView({str(align_to_bottom).lower()});", el
    )




def delete_cache():
    driver.execute_script("window.open('')")  # Create a separate tab than the main one
    driver.switch_to.window(
        driver.window_handles[-1]
    )  # Switch window to the second tab
    time.sleep(2)
    driver.get("chrome://settings/clearBrowserData")  # Open your chrome settings.
    time.sleep(1)

    with open("scripts/findClearButton.js") as f:
        findClearButton = f.read()
    with open("scripts/findDeleteBrowserData.js") as f:
        findDeleteBrowserData = f.read()

    try:
        driver.execute_script(findClearButton).click()
    except (
        AttributeError,
        ElementNotInteractableException,
        NoSuchElementException,
        ElementClickInterceptedException,
    ):
        driver.execute_script(findDeleteBrowserData).click()
        time.sleep(1)
        driver.execute_script(findClearButton).click()

    driver.close()  # Close that window
    driver.switch_to.window(
        driver.window_handles[0]
    )  # Switch Selenium controls to the original tab to continue normal functionality.

def accept_cookies():
    try:
        driver.find_element(By.XPATH, r"//button[text()='Accept All Cookies']").click()
    except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
        pass
    time.sleep(2)


def overcome_verification():
    verifyThatYouAreHuman = driver.find_elements(
        By.XPATH, r"//*[contains(text(), 'you are human')]"
    )
    if verifyThatYouAreHuman:
        logger.debug("verification")
        
        try:
            delete_cache()
            driver.refresh()
        except Exception:
            logger.warning('HARD RELOAD')
            
            new_driver = get_driver()
            try:
                while driver.window_handles:
                    driver.switch_to.window(
                        driver.window_handles[-1]
                    )
                    driver.close()
            except Exception:
                pass
            
            driver.__dict__ = new_driver.__dict__
            driver.get(url)
            cookies_ok()
            
        time.sleep(5)
    else:
        logger.debug("no verification")

def safe_get(url: str):    
    driver.get(url)
    time.sleep(5)
    overcome_verification()
    cookies_ok()

def verify_resistant(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        overcome_verification()
        result = func(*args, **kwargs)
        return result

    return wrapper



driver.maximize_window()
# driver.get(url)

# time.sleep(1)
# driver.fullscreen_window()
# time.sleep(3)


if __name__ == "__main__":
    driver.get('https://example.com')
    safe_get('https://google.com')
    # parse_course_vision()
