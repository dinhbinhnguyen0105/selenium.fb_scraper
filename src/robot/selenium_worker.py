from uuid import uuid4
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from PyQt6.QtCore import QRunnable
from src.my_types import WorkerSignals, TaskInfo
from src.services.result_service import Result_Service
from src.services.ignore_phonenumber_service import IgnorePhoneNumber_Service
from src.services.ignore_uid_service import IgnoreUID_Service
from src.robot.selenium_actions import ACTION_MAP

class BrowserWorker(QRunnable):
    def __init__(self, task_info:TaskInfo, retry_num: int):
        super().__init__()
        self.task_info = task_info
        self.retry_num = retry_num
        self.worker_signals = WorkerSignals()

        self.setAutoDelete(True)
    
    def run(self):
        connection_name = f"worker_{uuid4()}"
        action_function = ACTION_MAP.get(self.task_info.action_name, None)
        if not action_function:
            return False
        try:
            result_service = Result_Service(connection_name=connection_name)
            ignore_phonenumber_service = IgnorePhoneNumber_Service(
                connection_name=connection_name
            )
            ignore_uid_service = IgnoreUID_Service(connection_name=connection_name)

            options = Options()
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument(f"user-data-dir={self.task_info.user_data_dir}")
            options.add_argument("--disable-blink-features=AutomationControlled")

            services = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(options=options, service=services)
            driver.set_page_load_timeout(60)
            try:
                action_function(
                    driver=driver,
                    task_info=self.task_info,
                    signals=self.worker_signals,
                    services={
                        "uid": ignore_uid_service,
                        "phone_number": ignore_phonenumber_service,
                        "result": result_service,
                    }
                )
            except Exception as e:
                print(e)
            finally:
                if driver.service.is_connectable():
                    driver.quit()

        except Exception as e:
            print(e)