from time import sleep
from typing import Dict, Any, Optional, List
from src.my_constants import LAUNCHING, SCRAPING
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import (
    WebDriverException, NoSuchElementException, TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


from src.robot import selectors
from src.my_types import (
    TaskInfo,
    WorkerSignals,
    IgnoreUID_Type,
    IgnorePhoneNumber_Type,
    Result_Type,
)
from src.services.result_service import Result_Service
from src.services.ignore_phonenumber_service import IgnorePhoneNumber_Service
from src.services.ignore_uid_service import IgnoreUID_Service

def on_launching(
        driver: WebDriver,
        task_info: TaskInfo,
        signals: WorkerSignals,
        services: Dict[str, Any]
):
    while True:
        try:
            _ = driver.title
        except WebDriverException as e:
            return True

def on_scraper(
        driver: WebDriver,
        task_info: TaskInfo,
        signals: WorkerSignals,
        services: Dict[str, Any]
):
    wait = WebDriverWait(driver=driver, timeout=10)
    
    def close_dialog():
        try:
            dialog_elements = driver.find_elements(By.CSS_SELECTOR, selectors.S_DIALOG)
            for dialog_element in dialog_elements:
                if dialog_element.is_displayed() and dialog_element.is_enabled():
                    close_btn_elements = dialog_element.find_elements(By.CSS_SELECTOR, selectors.S_CLOSE_BUTTON)
                    for close_btn_elm in close_btn_elements:
                        if close_btn_elm.is_displayed() and close_btn_elm.is_enabled():
                            close_btn_elm.click()
                            return True
            return True
        except Exception:
            return False
    
    def get_groups(max_loading_attempts = 30) -> List[str]:
        group_urls = []
        try:
            driver.get("https://www.facebook.com/groups/feed/")
            # signals.info_signal.emit("Successfully navigated to general groups page.")        
            sidebar_elm = driver.find_element(By.CSS_SELECTOR, f"{selectors.S_NAVIGATION}:not({selectors.S_BANNER} {selectors.S_NAVIGATION})")
            if not sidebar_elm:
                print("sidebar_elm not found!")
                return []
            loading_attempt = 0
            sleep(3)
            try:
                while(
                    WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, selectors.S_LOADING)))
                    and loading_attempt < max_loading_attempts
                ):
                    loading_elm = WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, selectors.S_LOADING)))
                    driver.execute_script("arguments[0].scrollIntoView(true);", loading_elm)
                    loading_attempt += 1
                    sleep(2)
                    # try:
                    #     WebDriverWait(driver, 3).until(expected_conditions.staleness_of(loading_elm))
                    # except TimeoutException:
                    #     print("passed!")
                    #     pass

            except NoSuchElementException:
                pass
            group_elms = sidebar_elm.find_elements(By.CSS_SELECTOR, "a[href^='https://www.facebook.com/groups/']")
            for group_elm in group_elms:
                group_urls.append(group_elm.get_attribute("href"))
            
            return group_urls
        except Exception as e:
            print(str(e))
            return group_urls


    print(get_groups())
        
    return True

ACTION_MAP = {
    LAUNCHING : on_launching,
    SCRAPING: on_scraper
}

"div[role='navigation']:not(div[role='banner']div[role='navigation'])"
