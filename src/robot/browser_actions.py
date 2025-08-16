import re, traceback
from time import sleep
from datetime import datetime
from typing import Dict, Any, Optional
from phonenumbers import PhoneNumberMatcher
from PyQt6.QtCore import QObject, pyqtSignal
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Locator

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
from src.my_constants import LAUNCHING, SCRAPING


def on_launching(
    page: Page, task_info: TaskInfo, signals: WorkerSignals, services: Dict[str, Any]
):
    signals.info_signal.emit(f"{task_info.dir_name} Launching ...")
    page.wait_for_event("close", timeout=0)
    signals.info_signal.emit(f"{task_info.dir_name} Closed!")
    return True


def on_scraper(
    page: Page, task_info: TaskInfo, signals: WorkerSignals, services: Dict[str, Any]
):

    def close_dialog():
        try:
            dialog_locators = page.locator(selectors.S_DIALOG)
            for dialog_locator in dialog_locators.all():
                if dialog_locator.is_visible() and dialog_locator.is_enabled():
                    close_button_locators = dialog_locator.locator(
                        selectors.S_CLOSE_BUTTON
                    )
                    sleep(3)
                    close_button_locators.last.click(timeout=60_000)
                    dialog_locator.wait_for(state="detached", timeout=60_000)
            return True
        except PlaywrightTimeoutError:
            return False

    def find_nearest_ancestor(element: Locator, selector):
        current_element = element
        while current_element:
            elm = current_element.locator(selector).first
        return None

    def get_groups(max_loading_attempts=30):
        try:
            page.goto("https://www.facebook.com/groups/feed/", timeout=60_000)
            signals.info_signal.emit("Successfully navigated to general groups page.")
        except PlaywrightTimeoutError as e:
            return

        signals.info_signal.emit(
            "Waiting for group sidebar to load (if loading icon is present)."
        )
        sidebar_locator = page.locator(
            f"{selectors.S_NAVIGATION}:not({selectors.S_BANNER} {selectors.S_NAVIGATION})"
        )

        group_locators = sidebar_locator.first.locator(
            "a[href^='https://www.facebook.com/groups/']"
        )

        loading_attempt = 0
        while (
            sidebar_locator.first.locator(selectors.S_LOADING).count()
            and loading_attempt < max_loading_attempts
        ):
            loading_attempt += 1
            signals.info_signal.emit("Loading indicator detected in sidebar")
            _loading_element = sidebar_locator.first.locator(selectors.S_LOADING)
            try:
                _loading_element.first.scroll_into_view_if_needed(timeout=60_000)
                sleep(3)
                signals.info_signal.emit("Loading indicator scrolled into view.")
            except PlaywrightTimeoutError as e:
                signals.info_signal.emit(
                    "ERROR: Timeout while scrolling loading indicator. Details: {str(e)}. Exiting wait loop."
                )
                break
            except Exception as ex:
                signals.info_signal.emit(
                    f"ERROR: An unexpected error occurred while scrolling loading indicator. Details: {str(ex)}. Exiting wait loop."
                )
                break
        if loading_attempt >= max_loading_attempts:
            signals.info_signal.emit(
                f"WARNING: Exceeded maximum loading wait attempts ({max_loading_attempts}). Continuing without full sidebar load confirmation."
            )
        else:
            signals.info_signal.emit(
                "Group sidebar loaded or no loading indicator found."
            )

        group_locators = sidebar_locator.first.locator(
            "a[href^='https://www.facebook.com/groups/']"
        )
        group_urls = []
        for i in range(group_locators.count()):
            _href = group_locators.nth(i).get_attribute("href")
            _textcontent = group_locators.nth(i).text_content().lower()
            if _href:
                if task_info.target_keywords:
                    for target_keyword in task_info.target_keywords:
                        if target_keyword in _textcontent:
                            group_urls.append(_href)
                            break
                else:
                    group_urls.append(_href)

        signals.info_signal.emit(f"Found {len(group_urls)} group URLs.")
        if not group_urls:
            signals.info_signal.emit(
                "WARNING: No group URLs could be retrieved. No groups to post in."
            )
            return []
        return group_urls

    def scraping(url: str):
        def get_author_info(author_locator: Locator) -> Optional[Dict[str, str]]:
            try:
                author_locator.first.wait_for(state="attached", timeout=10_000)
                author_locator.scroll_into_view_if_needed()
                author_locator.highlight()
                article_user_url_locator = author_locator.first.locator("a")
                article_user_url_locator.first.hover()
                sleep(0.5)
                author_url = article_user_url_locator.first.get_attribute(
                    "href",
                    timeout=1_000,
                ).split("?")[0]
                author_name = article_user_url_locator.first.text_content(
                    timeout=10_000
                )
                author_url: str = (
                    author_url[0:-1] if author_url.endswith("/") else author_url
                )

                uid = author_url.split("/")[-1]
                _is_uid_existed = services["uid"].is_existed("value", uid)
                if not _is_uid_existed:
                    services["uid"].create(
                        IgnoreUID_Type(
                            id=None,
                            value=uid,
                            created_at=None,
                        )
                    )
                    if not author_url.startswith("http"):
                        author_url = "https://www.facebook.com/" + author_url
                    return {
                        "author_url": author_url,
                        "author_name": author_name,
                    }
                else:
                    pass
                    # print(f"Ignore UID: {uid}")
                    return False
            except Exception as e:
                return False

        def get_article_url(article_info_locator: Locator) -> Optional[str]:
            try:
                article_info_locator.first.wait_for(state="attached", timeout=10_000)
                article_info_locator.first.scroll_into_view_if_needed()
                article_info_locator.first.highlight()

                article_url_locator = article_info_locator.first.locator("a")
                for i in range(10):
                    article_url_locator.first.hover()
                    sleep(1)
                    if not article_url_locator.first.get_attribute("target"):
                        break
                    article_info_locator.first.hover()
                article_url = article_url_locator.first.get_attribute("href").split(
                    "?"
                )[0]
                article_url: str = (
                    article_url[0:-1] if article_url.endswith("/") else article_url
                )
                return article_url
            except Exception as e:
                print(e)
                return False

        def get_article_content(
            article_content_locator: Locator,
        ) -> Optional[str]:
            try:
                article_content_locator.first.wait_for(state="visible", timeout=10_000)
                article_content_locator.first.scroll_into_view_if_needed()
                article_content_locator.first.highlight()
                content = article_content_locator.text_content()
                new_content = ""
                button_locator = article_content_locator.first.locator(
                    "div[role='button']"
                )
                if button_locator.count():
                    button_locator.first.wait_for(state="attached", timeout=10_000)
                    button_locator.first.click()
                    for i in range(10):
                        new_content = article_content_locator.text_content()
                        if content != new_content:
                            content = new_content
                            break
                        sleep(1)
                return content
            except Exception as e:
                print(e)
                return False

        page.goto(url=url, timeout=60_000)
        close_dialog()
        feed_locators = page.locator(selectors.S_FEED)
        try:
            feed_locators.first.wait_for(state="attached", timeout=60_000)
        except PlaywrightTimeoutError:
            return False
        feed_locator: Locator = feed_locators.first
        if not feed_locator:
            return False

        try:
            post_index = 0
            while post_index < task_info.post_num:
                result = Result_Type(
                    id=None,
                    article_url="",
                    article_content="",
                    author_url="",
                    author_name="",
                    contact="",
                    created_at=None,
                )
                article_locators = feed_locator.locator(selectors.S_ARTICLE)
                article_locators.first.scroll_into_view_if_needed()
                describedby_values = article_locators.first.get_attribute(
                    "aria-describedby"
                )
                article_user_id = article_locators.first.get_attribute(
                    "aria-labelledby"
                )
                (
                    article_info_id,
                    article_message_id,
                    article_content_id,
                    article_reaction_id,
                    article_comment_id,
                ) = describedby_values.split(" ")

                ellipsis_locator = article_locators.first.locator(
                    "[aria-haspopup='menu'][aria-expanded='false']"
                )

                author_locator = article_locators.first.locator(
                    f"[id='{article_user_id}']"
                )
                article_info_locator = article_locators.first.locator(
                    f"[id='{article_info_id}']"
                )
                article_message_locator = article_locators.first.locator(
                    f"[id='{article_message_id}']"
                )
                article_content_locator = article_locators.first.locator(
                    f"[id='{article_content_id}']"
                )
                article_reaction_locator = article_locators.first.locator(
                    f"[id='{article_reaction_id}']"
                )
                article_comment_locator = article_locators.first.locator(
                    f"[id='{article_comment_id}']"
                )

                try:
                    article_info = {}
                    # TODO get article_content
                    article_info["content"] = get_article_content(
                        article_message_locator
                    )
                    if not article_info["content"]:
                        article_locators.first.evaluate("elm => elm.remove()")
                        signals.sub_progress_signal.emit(
                            task_info.object_name, task_info.post_num, post_index
                        )
                        continue

                    # TODO get contact
                    article_info["contact"] = ""
                    regex_pattern = r"[^0-9\s.\-()]+" 
                    for match in PhoneNumberMatcher(
                        re.sub(regex_pattern, " ", article_info["content"]), "VN"
                    ):
                        article_info["contact"] = re.sub(r"\D" , "", match.raw_string)
                    
                    # TODO get article_url
                    article_info["article_url"] = get_article_url(article_info_locator)
                    if not article_info["article_url"]:
                        article_locators.first.evaluate("elm => elm.remove()")
                        signals.sub_progress_signal.emit(
                            task_info.object_name, task_info.post_num, post_index
                        )
                        continue

                    if not services["phone_number"].is_existed(
                        "value", article_info["contact"]
                    ):
                        if article_info["contact"]:
                            services["phone_number"].create(
                                IgnorePhoneNumber_Type(
                                    id=None,
                                    value=article_info["contact"],
                                    created_at=None,
                                )
                            )
                    else:
                        article_locators.first.evaluate("elm => elm.remove()")
                        continue
                        # print(f"Ignore phone number: {article_info['contact']}")
                    # TODO get author_info
                    author_info = get_author_info(author_locator)
                    if not author_info:
                        article_locators = feed_locator.locator(selectors.S_ARTICLE)
                        article_locators.first.evaluate("elm => elm.remove()")
                        signals.sub_progress_signal.emit(
                            task_info.object_name, task_info.post_num, post_index
                        )
                        continue
                    result.author_url = author_info.get("author_url")
                    result.author_name = author_info.get("author_name")
                    result.article_url = article_info["article_url"]
                    result.article_content = article_info["content"]
                    result.contact = article_info["contact"]

                    services["result"].create(result)
                    print(f"New result: {result.author_name} - {result.contact}: {result.article_content[:100]} ...")

                    # ellipsis_locator.first.hover(timeout=60_000)
                    # ellipsis_locator.first.highlight()
                    article_locators.first.evaluate("elm => elm.remove()")
                    signals.sub_progress_signal.emit(
                        task_info.object_name, task_info.post_num, post_index
                    )

                    post_index += 1
                    if post_index > task_info.post_num:
                        break

                except PlaywrightTimeoutError as e:
                    print(e)

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            return False

    list_group_url = get_groups(20)

    for group_url in list_group_url:
        scraping(group_url)


ACTION_MAP = {
    LAUNCHING: on_launching,
    SCRAPING: on_scraper,
}
