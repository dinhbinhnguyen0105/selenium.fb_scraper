import os
from PyQt6.QtWidgets import QWidget, QFileDialog

from src.ui.thread_container_ui import Ui_ThreadContainer


class ThreadContainer_Widget(QWidget, Ui_ThreadContainer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.selected_dir_path = ""
        self.setup_ui()
        self.setup_events()

    def setup_ui(self):
        self.select_udd_input.setDisabled(True)
        self.launch_browser_btn.setDisabled(True)
        self.progress_message.setHidden(True)
        self.main_progress.setHidden(True)
        self.main_progress_label.setHidden(True)
        self.sub_progress.setHidden(True)
        self.sub_progress_label.setHidden(True)

    def setup_events(self):
        self.select_udd_btn.clicked.connect(self.handle_open_directory)
        # self.launch_browser_btn.clicked.connect()

    def set_title(self, text: str):
        self.thread_name_label.setText(text)

    def set_main_progress(self, percent: int):
        # self.main_progress
        pass

    def set_sub_progress(self, percent: int):
        # self.sub_progress
        pass

    def set_progress_message(self, text: str):
        # self.progress_message
        pass

    def handle_open_directory(self):
        directory_path = QFileDialog.getExistingDirectory(
            self,
            "Select user_data_dir",
            "",
            QFileDialog.Option.ShowDirsOnly,
        )
        if directory_path:
            self.select_udd_input.setText(directory_path)
            self.selected_dir_path = directory_path
            self.setObjectName(os.path.basename(directory_path))
            self.launch_browser_btn.setDisabled(False)

    def handle_launch_browser(self):
        pass
