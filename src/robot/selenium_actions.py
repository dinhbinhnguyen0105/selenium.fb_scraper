from time import sleep
from typing import Dict, Any, Optional, List
from src.my_constants import LAUNCHING, SCRAPING
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
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

    def highlight(element: WebElement) -> None:
        # original_style = element.get_attribute("style")
        highlight_style = "background: yellow; border: 2px solid red; transition: all 0.5s ease 0s;"
        driver.execute_script(f"arguments[0].setAttribute('style', arguments[1]);", element, highlight_style)
        
    
    def close_dialog():
        try:
            dialog_elements = driver.find_elements(By.CSS_SELECTOR, selectors.S_DIALOG)
            for dialog_element in dialog_elements:
                if dialog_element.is_displayed() and dialog_element.is_enabled():
                    close_btn_elements = dialog_element.find_elements(By.CSS_SELECTOR, selectors.S_CLOSE_BUTTON)
                    for close_btn_elm in close_btn_elements:
                        if close_btn_elm.is_displayed() and close_btn_elm.is_enabled():
                            close_btn_elm.click()
                            try:
                                WebDriverWait(driver, 30).until(expected_conditions.staleness_of(dialog_element))
                                return True
                            except TimeoutException:
                                return False
            return True
        except Exception:
            return False
    
    def get_groups(max_loading_attempts = 30) -> List[str]:
        group_urls = []
        try:
            driver.get("https://www.facebook.com/groups/feed/")
            sidebar_elm = driver.find_element(By.CSS_SELECTOR, f"{selectors.S_NAVIGATION}:not({selectors.S_BANNER} {selectors.S_NAVIGATION})")
            if not sidebar_elm:
                print("sidebar_elm not found!")
                return []
            loading_attempt = 0
            sleep(3)
            # try:
            #     while(
            #         WebDriverWait(sidebar_elm, 30).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, selectors.S_LOADING)))
            #         and loading_attempt < max_loading_attempts
            #     ):
            #         loading_elm = WebDriverWait(sidebar_elm, 30).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, selectors.S_LOADING)))
            #         driver.execute_script("arguments[0].scrollIntoView(true);", loading_elm)
            #         loading_attempt += 1
            #         sleep(2)
            #         try:
            #             WebDriverWait(driver, 3).until(expected_conditions.staleness_of(loading_elm))
            #         except TimeoutException:
            #             pass

            # except NoSuchElementException:
            #     pass
            group_elms = sidebar_elm.find_elements(By.CSS_SELECTOR, "a[href^='https://www.facebook.com/groups/']")
            for group_elm in group_elms:
                group_urls.append(group_elm.get_attribute("href"))
            
            return group_urls
        except Exception as e:
            print(str(e))
            return group_urls

    def get_author_info(author_elm: WebElement) -> Optional[Dict[str, str]]:
        author_info = {
            "author_url": "",
            "author_name": "",
        }
        try:
            

            return author_info
        except Exception as e:
            print(str(e))
            return author_info

    def scraping(url: str):
        driver.get(url)
        if not close_dialog(): return
        try:
            feed_elm = WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, selectors.S_FEED)))
            post_index = 0

            while post_index < task_info.post_num:
                result = Result_Type(
                    id = None,
                    article_url="",
                    article_content="",
                    author_url="",
                    author_name="",
                    contact="",
                    created_at=None,
                )

                article_elm = WebDriverWait(feed_elm, 10).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, selectors.S_ARTICLE)))
                driver.execute_script("arguments[0].scrollIntoView(true);", article_elm)
                described_values = article_elm.get_attribute("aria-describedby")
                article_author_id = article_elm.get_attribute("aria-labelledby")
                article_info_id, article_message_id, article_content_id, article_reaction_id, article_comment_id = described_values.split(" ")
                
                # ellipsis_elm = article_elm.find_element(By.CSS_SELECTOR, "[aria-haspopup='menu'][aria-expanded='false']")
                # article_info_elm = article_elm.find_element(By.CSS_SELECTOR, f"[id='{article_info_id}']")
                # article_message_elm = article_elm.find_element(By.CSS_SELECTOR, f"[id='{article_message_id}']")
                # article_content_elm = article_elm.find_element(By.CSS_SELECTOR, f"[id='{article_content_id}']")
                # article_reaction_elm = article_elm.find_element(By.CSS_SELECTOR, f"[id='{article_reaction_id}']")
                # article_comment_elm = article_elm.find_element(By.CSS_SELECTOR, f"[id='{article_comment_id}']")

                author_elm = article_elm.find_element(By.CSS_SELECTOR, f"[id='{article_author_id}']")
                highlight(author_elm)

                while True:
                    try:
                        _ = driver.title
                    except WebDriverException as e:
                        return True
            

            return
        except Exception as e:
            print(str(e))
            return

    group_urls = get_groups()
    for group_url in group_urls:
        scraping(group_url)
    return True

ACTION_MAP = {
    LAUNCHING : on_launching,
    SCRAPING: on_scraper
}

