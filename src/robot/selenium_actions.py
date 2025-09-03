import re
from time import sleep
from phonenumbers import PhoneNumberMatcher
from typing import Dict, Any, Optional, List
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    WebDriverException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from src.my_constants import LAUNCHING, SCRAPING
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
    services: Dict[str, Any],
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
    services: Dict[str, Any],
):
    wait = WebDriverWait(driver=driver, timeout=10)
    actions = ActionChains(driver=driver)
    central_scroll_script = "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});"

    def highlight(element: WebElement) -> None:
        # original_style = element.get_attribute("style")
        highlight_style = (
            "background: yellow; border: 2px solid red; transition: all 0.5s ease 0s;"
        )
        driver.execute_script(
            f"arguments[0].setAttribute('style', arguments[1]);",
            element,
            highlight_style,
        )

    def close_dialog():
        try:
            dialog_elements = driver.find_elements(By.CSS_SELECTOR, selectors.S_DIALOG)
            for dialog_element in dialog_elements:
                if dialog_element.is_displayed() and dialog_element.is_enabled():
                    close_btn_elements = dialog_element.find_elements(
                        By.CSS_SELECTOR, selectors.S_CLOSE_BUTTON
                    )
                    for close_btn_elm in close_btn_elements:
                        if close_btn_elm.is_displayed() and close_btn_elm.is_enabled():
                            close_btn_elm.click()
                            try:
                                WebDriverWait(driver, 30).until(
                                    expected_conditions.staleness_of(dialog_element)
                                )
                                return True
                            except TimeoutException:
                                return False
            return True
        except Exception:
            return False

    def get_groups(max_loading_attempts=30) -> List[str]:
        group_urls = []
        try:
            driver.get("https://www.facebook.com/groups/feed/")
            sidebar_elm = driver.find_element(
                By.CSS_SELECTOR,
                f"{selectors.S_NAVIGATION}:not({selectors.S_BANNER} {selectors.S_NAVIGATION})",
            )
            if not sidebar_elm:
                print("sidebar_elm not found!")
                return []
            loading_attempt = 0
            sleep(3)
            try:
                while (
                    WebDriverWait(sidebar_elm, 30).until(
                        expected_conditions.presence_of_element_located(
                            (By.CSS_SELECTOR, selectors.S_LOADING)
                        )
                    )
                    and loading_attempt < max_loading_attempts
                ):
                    loading_elm = WebDriverWait(sidebar_elm, 30).until(
                        expected_conditions.presence_of_element_located(
                            (By.CSS_SELECTOR, selectors.S_LOADING)
                        )
                    )
                    driver.execute_script(central_scroll_script, loading_elm)
                    loading_attempt += 1
                    sleep(2)
                    try:
                        WebDriverWait(driver, 3).until(
                            expected_conditions.staleness_of(loading_elm)
                        )
                        break
                    except Exception:
                        continue
            except NoSuchElementException:
                pass
            group_elms = sidebar_elm.find_elements(
                By.CSS_SELECTOR, "a[href^='https://www.facebook.com/groups/']"
            )
            for group_elm in group_elms:
            #     if "thuê" in group_elm.get_attribute("textContent").lower():
            #         group_urls.append(group_elm.get_attribute("href"))/
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
            driver.execute_script(central_scroll_script, author_elm)
            url_elm = author_elm.find_element(By.CSS_SELECTOR, "a")
            actions.move_to_element(url_elm).perform()
            url_elm = author_elm.find_element(By.CSS_SELECTOR, "a")
            author_info["author_name"] = url_elm.get_attribute("textContent")
            author_info["author_url"] = url_elm.get_attribute("href").split("?")[0]
            return author_info
        except NoSuchElementException:
            return author_info
        except Exception as e:
            print(str(e))
            return author_info

    def get_article_url(article_elm: WebElement) -> Optional[Dict[str, str]]:
        article_info = {"article_url": ""}
        try:
            url_elm = article_elm.find_element(By.CSS_SELECTOR, "a")
            driver.execute_script(central_scroll_script, url_elm)
            actions.move_to_element(url_elm).perform()
            WebDriverWait(driver, 10).until(
                lambda d: "posts" in url_elm.get_attribute("href").split("?")[0]
            )
            article_info["article_url"] = url_elm.get_attribute("href").split("?")[0]
            return article_info
        except TimeoutException:
            return article_info
        except Exception as e:
            print(str(e))
            return article_info

    def get_article_message(content_elm: WebElement) -> Optional[Dict[str, str]]:
        article_info = {"article_message": ""}
        try:
            driver.execute_script(central_scroll_script, content_elm)
            article_info["article_message"] = content_elm.get_attribute("textContent")
            btn_elms = content_elm.find_elements(By.CSS_SELECTOR, "div[role='button']")
            for btn_elm in btn_elms:
                if btn_elm.is_displayed() and btn_elm.is_enabled():
                    btn_elms[0].click()
                    WebDriverWait(driver, 3).until(
                        expected_conditions.staleness_of(btn_elms[0])
                    )
            article_info["article_message"] = content_elm.get_attribute("textContent")
            return article_info
        except Exception as e:
            print(str(e))
            return article_info

    def scraping(url: str):
        driver.get(url)
        if not close_dialog():
            return
        try:
            feed_elm = WebDriverWait(driver, 30).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, selectors.S_FEED)
                )
            )
            post_index = 0

            while post_index < task_info.post_num:
                print(f"{post_index}. \t", end="")
                result = Result_Type(
                    id=None,
                    article_url="",
                    article_content="",
                    author_url="",
                    author_name="",
                    contact="",
                    created_at=None,
                )

                article_elm = WebDriverWait(feed_elm, 10).until(
                    expected_conditions.presence_of_element_located(
                        (By.CSS_SELECTOR, selectors.S_ARTICLE)
                    )
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", article_elm)
                described_values = article_elm.get_attribute("aria-describedby")
                article_author_id = article_elm.get_attribute("aria-labelledby")
                (
                    article_info_id,
                    article_message_id,
                    article_content_id,
                    article_reaction_id,
                    article_comment_id,
                ) = described_values.split(" ")

                # ellipsis_elm = article_elm.find_element(By.CSS_SELECTOR, "[aria-haspopup='menu'][aria-expanded='false']")
                # article_reaction_elm = article_elm.find_element(By.CSS_SELECTOR, f"[id='{article_reaction_id}']")
                # article_comment_elm = article_elm.find_element(By.CSS_SELECTOR, f"[id='{article_comment_id}']")
                # article_content_elm = article_elm.find_element(By.CSS_SELECTOR, f"[id='{article_content_id}']")
                try:
                    author_elm = article_elm.find_element(
                        By.CSS_SELECTOR, f"[id='{article_author_id}']"
                    )
                    author_info_obj = get_author_info(author_elm=author_elm)
                    result.author_url = author_info_obj.get("author_url")
                    result.author_name = author_info_obj.get("author_name")

                    if not result.author_url:
                        raise ScrapingError("author_url is empty!")
                    uid = ""
                    if result.author_url.endswith("/"):
                        uid = result.author_url.split("/")[-2]
                    else:
                        uid = result.author_url.split("/")[-1]
                    if services["uid"].is_existed("value", uid):
                        raise ScrapingError(f"uid `{uid}` existed!")
                    else:
                        services["uid"].create(
                            IgnoreUID_Type(id=None, value=uid, created_at=None)
                        )

                    article_message_elm = article_elm.find_element(
                        By.CSS_SELECTOR, f"[id='{article_message_id}']"
                    )
                    article_message_obj = get_article_message(article_message_elm)
                    result.article_content = article_message_obj.get(
                        "article_message", ""
                    )

                    if not result.article_content:
                        raise ScrapingError("article_content is empty!")

                    phone_number = ""
                    regex_pattern = r"[^0-9\s.\-()]+"
                    for match in PhoneNumberMatcher(
                        re.sub(regex_pattern, " ", result.article_content), "VN"
                    ):
                        phone_number = re.sub(r"\D", "", match.raw_string)
                    if not phone_number:
                        raise ScrapingError("phone_number is empty!")

                    if services["phone_number"].is_existed("value", phone_number):
                        raise ScrapingError(f"phone_number `{phone_number}` existed!")
                    else:
                        services["phone_number"].create(
                            IgnorePhoneNumber_Type(
                                id=None,
                                value=phone_number,
                                created_at=None,
                            )
                        )
                    article_info_elm = article_elm.find_element(
                        By.CSS_SELECTOR, f"[id='{article_info_id}']"
                    )
                    article_info_obj = get_article_url(article_info_elm)
                    result.article_url = article_info_obj.get("article_url", "")
                    services["result"].create(result)
                    print(result)
                except ScrapingError as e:
                    driver.execute_script("arguments[0].remove();", article_elm)
                    post_index += 1
                    print(e)
                    continue
                except NoSuchElementException:
                    driver.execute_script("arguments[0].remove();", article_elm)
                    continue

                # while True:
                #     try:
                #         _ = driver.title
                #     except WebDriverException as e:
                #         return True

            return
        except Exception as e:
            print(str(e))
            return

    group_urls = get_groups()

    # print(group_urls)

    if not task_info.target_keywords:
        for group_url in group_urls:
            is_ignore_url = False
            for ignore_url in [
                "475205321869395",
            ]:
                if ignore_url in group_url:
                    is_ignore_url = True
                    break
            if is_ignore_url:
                continue
            scraping(group_url)
    else:
        for group_url in group_urls:
            is_ignore_url = False
            for ignore_url in [
                "475205321869395",
            ]:
                if ignore_url in group_url:
                    is_ignore_url = True
                    break
            if is_ignore_url:
                continue
            for keyword in task_info.target_keywords:
                _ = (
                    f"{group_url}search?q={keyword}"
                    if group_url.endswith("/")
                    else f"{group_url}/search?q={keyword}"
                )
                scraping(_)

    return True


class ScrapingError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


ACTION_MAP = {LAUNCHING: on_launching, SCRAPING: on_scraper}
