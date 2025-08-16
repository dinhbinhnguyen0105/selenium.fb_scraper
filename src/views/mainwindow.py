from typing import List
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

from src.ui.mainwindow_ui import Ui_MainWindow
from src.views.thread_container_w import ThreadContainer_Widget
from src.views.dialog_data import Data_Dialog
from src.my_constants import DATA_TABLES, LAUNCHING, SCRAPING
from src.controllers.robot_controller import RobotController


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Scraper")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setup_ui()
        self.setup_events()

        self.robot_controller = RobotController(self)
        self.thread_num = 0
        self.list_thread_widget: List[ThreadContainer_Widget] = []

    def setup_ui(self):
        self.thread_num_input.setValue(0)
        regex = QRegularExpression("^[a-zA-Z0-9 &,]+$")
        validator = QRegularExpressionValidator(regex)
        self.group_key_input.setValidator(validator)
        self.ignore_group_key_input.setValidator(validator)
        self.group_key_input.setText("thuê, sang")
        self.ignore_group_key_input.setText("trọ")

        self.data_open_btn.setDisabled(True)
        for name, value in DATA_TABLES.items():
            self.data_combobox.addItem(name, value)

    def setup_events(self):
        self.data_combobox.currentIndexChanged.connect(self.on_data_combobox_changed)
        self.data_open_btn.clicked.connect(self.on_data_open)
        self.thread_num_input.valueChanged.connect(self.handle_change_thread)
        self.runbot_btn.clicked.connect(self.handle_run_bot)

    def on_data_open(self):
        data_dialog = Data_Dialog(self)
        data_dialog.set_table_model(
            self.data_combobox.itemData(self.data_combobox.currentIndex())
        )
        data_dialog.exec()

    def on_data_combobox_changed(self, index: int):
        if self.data_combobox.itemData(index):
            self.data_open_btn.setEnabled(True)

    def handle_change_thread(self):
        current_thread_num = self.thread_num_input.value()
        spread = current_thread_num - self.thread_num
        if spread > 0:  # add thread
            while spread != 0:
                thread_container_widget = ThreadContainer_Widget(self)
                thread_container_widget.set_title(
                    f"Thread {len(self.list_thread_widget ) + 1}:"
                )
                thread_container_widget.select_udd_input.setText(
                    # "/Users/ndb/Dev/python/scraper.data/browsers/100089985627418_DinhBinh_Nguyen"
                    "/Volumes/KINGSTON/Dev/python/python.scraper-v2/repositories/browsers/uid_username"
                )
                thread_container_widget.launch_browser_btn.clicked.connect(
                    lambda: self.handle_launch_browser(thread_container_widget)
                )
                self.threads_container_layout.addWidget(thread_container_widget)
                self.list_thread_widget.append(thread_container_widget)
                spread -= 1
        elif spread < 0:  # remove thread
            while spread != 0:
                last_thread_widget = self.list_thread_widget.pop()
                self.threads_container_layout.removeWidget(last_thread_widget)
                last_thread_widget.deleteLater()
                spread += 1
        else:
            pass
        self.thread_num = current_thread_num

    def handle_launch_browser(self, current_widget: ThreadContainer_Widget):
        user_data_dir_list = [current_widget.selected_dir_path]
        object_name_list = [current_widget.objectName()]
        target_group_keywords = [
            keyword.strip() for keyword in self.group_key_input.text().split(",")
        ]
        ignore_group_keywords = [
            keyword.strip() for keyword in self.ignore_group_key_input.text().split(",")
        ]
        self.robot_controller.run_task(
            action_name=LAUNCHING,
            object_name_list=object_name_list,
            user_data_dir_list=user_data_dir_list,
            target_keywords=target_group_keywords,
            ignore_keywords=ignore_group_keywords,
            headless=False,
        )

        current_widget.launch_browser_btn.setDisabled(True)
        self.robot_controller.robot_controller_signals.info_signal.connect(
            self.on_log_message
        )
        self.robot_controller.robot_controller_signals.succeeded_signal.connect(
            lambda: current_widget.launch_browser_btn.setDisabled(False)
        )

    def handle_run_bot(self):
        user_data_dir_list = [
            thread_widget.select_udd_input.text()
            for thread_widget in self.list_thread_widget
        ]
        object_name_list = [
            thread_widget.objectName() for thread_widget in self.list_thread_widget
        ]
        target_group_keywords = [
            keyword.strip()
            for keyword in self.group_key_input.text().split(",")
            if keyword.strip() != ""
        ]
        ignore_group_keywords = [
            keyword.strip()
            for keyword in self.ignore_group_key_input.text().split(",")
            if keyword.strip() != ""
        ]
        self.robot_controller.run_task(
            action_name=SCRAPING,
            object_name_list=object_name_list,
            user_data_dir_list=user_data_dir_list,
            target_keywords=target_group_keywords,
            ignore_keywords=ignore_group_keywords,
            headless=False,
        )
        self.runbot_btn.setDisabled(True)
        self.runbot_btn.setText("Running ..")

    def on_log_message(self, msg: str):
        print("[Info] ", msg)
