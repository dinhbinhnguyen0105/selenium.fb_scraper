# src/models/base_model.py
from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase
from typing import List, Optional
from src import my_constants as constants


class BaseModel(QSqlTableModel):
    def __init__(self, table_name, parent=None):
        super().__init__(parent, QSqlDatabase.database(constants.DB_CONNECTION))
        self.setTable(table_name)
        # self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        if not self.select():
            print(
                f"Error selecting data from table '{table_name}': {self.lastError().text()}"
            )

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def get_ids_by_rows(self, rows: List[int]) -> List[int]:
        ids = []
        for row in rows:
            if 0 <= row <= self.rowCount():
                index = self.index(row, self.fieldIndex("id"))
                ids.append(self.data(index))
        return ids

    def get_id_by_row(self, row: int) -> Optional[int]:
        if 0 <= row < self.rowCount():
            return self.index(row, self.fieldIndex("id"))
        return None
