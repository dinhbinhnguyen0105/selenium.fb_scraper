from typing import Union, TypeAlias, Optional, List
from PyQt6.QtWidgets import (
    QDialog,
    QMenu,
    QTableView,
    QPushButton,
    QMessageBox,
    QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSlot, QModelIndex, QPoint
from PyQt6.QtGui import QAction
from src.ui.dialog_data_ui import Ui_Dialog_Data
from src.models.ignore_phonenumber_model import IgnorePhoneNumber_Model
from src.controllers.ignore_phonenumber_controller import IgnorePhoneNumber_Controller
from src.models.ignore_uid_model import IgnoreUID_Model
from src.controllers.ignore_uid_controller import IgnoreUID_Controller
from src.models.result_model import Result_Model
from src.controllers.result_controller import Result_Controller
from src.my_constants import DATA_TABLES

Model_Type: TypeAlias = Union[IgnorePhoneNumber_Model, IgnoreUID_Model, Result_Model]
Controler_Type: TypeAlias = Union[
    IgnorePhoneNumber_Controller, IgnoreUID_Controller, Result_Controller
]


class Data_Dialog(QDialog, Ui_Dialog_Data):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.controller: Optional[Controler_Type] = None
        self.table_name: Optional[str] = None
        self.table_model: Optional[Model_Type] = None
        self.import_btn: Optional[QPushButton] = None
        self.export_btn: Optional[QPushButton] = None
        self.tableView.setWordWrap(True)
        self.tableView.setTextElideMode(Qt.TextElideMode.ElideNone)

    def set_table_model(self, table_name: str):
        self.table_name = table_name
        if self.table_name == DATA_TABLES["Ignore phone"]:
            self.table_model = IgnorePhoneNumber_Model()
            self.controller = IgnorePhoneNumber_Controller(self.table_model)
        elif self.table_name == DATA_TABLES["Ignore uid"]:
            self.table_model = IgnoreUID_Model()
            self.controller = IgnoreUID_Controller(self.table_model)
        elif self.table_name == DATA_TABLES["Results"]:
            self.table_model = Result_Model()
            self.controller = Result_Controller(self.table_model)
        else:
            raise ValueError(f"Invalid table name '{self.table_name}'")
        self.table_model.select()
        self.tableView.setModel(self.table_model)
        self.import_btn = QPushButton("Import")
        self.export_btn = QPushButton("Export")
        self.import_btn.clicked.connect(self.on_import_clicked)
        self.export_btn.clicked.connect(self.on_export_clicked)
        self.layout().addWidget(self.import_btn)
        self.layout().addWidget(self.export_btn)
        self.config_table()

    def config_table(self):
        self.tableView.resizeRowsToContents()
        self.tableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        article_content = self.table_model.fieldIndex("article_content")
        if article_content:
            # self.tableView.resizeColumnToContents(article_content)
            self.tableView.setColumnWidth(article_content, 600)
            self.tableView.resizeRowsToContents()
        if self.table_name == DATA_TABLES["Results"]:
            self.tableView.doubleClicked.connect(self.on_url_double_clicked)
        self.tableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.show_context_menu)

    @pyqtSlot(QPoint)
    def show_context_menu(self, pos: QPoint):
        index = self.tableView.indexAt(pos)
        if not index.isValid():
            return
        id_column = self.table_model.fieldIndex("id")
        selected_indexes = self.tableView.selectionModel().selectedRows(id_column)
        list_id = [self.table_model.data(idx) for idx in selected_indexes]
        global_pos = self.tableView.mapToGlobal(pos)
        menu = QMenu(self.tableView)
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(
            lambda _, list_id=list_id: self.controller.delete(list_id)
        )
        menu.addAction(delete_action)
        menu.popup(global_pos)
    
    @pyqtSlot(list)
    def on_delete(self, list_id: List[int]):
        self.controller.delete(list_id)
        self.controller.refresh_data()

    @pyqtSlot(QModelIndex)
    def on_url_double_clicked(self, index: QModelIndex):
        column_article_url_index = self.table_model.fieldIndex("article_url")
        column_author_url_index = self.table_model.fieldIndex("author_url")
        column_contact_index = self.table_model.fieldIndex("contact")
        if (
            index.column() == column_article_url_index
            or index.column() == column_author_url_index
        ):
            url_string = self.table_model.data(index)
            self.controller.handle_open_browser(url_string)
        elif index.column() == column_contact_index:
            url_string = (
                f"https://www.facebook.com/search/top/?q={self.table_model.data(index)}"
            )
            self.controller.handle_open_browser(url_string)
        else:
            return

    @pyqtSlot()
    def on_import_clicked(self):
        if not self.controller:
            QMessageBox.warning(self, "Error", "Controller not initialized.")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File to Import",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            if hasattr(self.controller, 'service') and callable(getattr(self.controller.service, 'import_data_from_csv', None)):
                success = self.controller.service.import_data_from_csv(file_path)
                if success:
                    QMessageBox.information(self, "Success", "Data imported successfully.")
                    self.table_model.select()
                else:
                    QMessageBox.warning(self, "Error", "An error occurred during data import. Please check the console.")
                    QMessageBox.warning(self, "Error", "Could not determine data type for this table.")
            else:
                QMessageBox.warning(self, "Error", "Controller does not support data import functionality.")

    @pyqtSlot()
    def on_export_clicked(self):
        if not self.controller:
            QMessageBox.warning(self, "Error", "Controller not initialized.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Data to CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            if hasattr(self.controller, 'service') and callable(getattr(self.controller.service, 'export_data_to_csv', None)):
                success = self.controller.service.export_data_to_csv(file_path)
                if success:
                    QMessageBox.information(self, "Success", "Data exported successfully.")
                else:
                    QMessageBox.warning(self, "Error", "An error occurred during data export. Please check the console.")
            else:
                QMessageBox.warning(self, "Error", "Controller does not support data export functionality.")