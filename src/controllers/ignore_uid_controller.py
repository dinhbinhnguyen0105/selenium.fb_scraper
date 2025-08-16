# src/controllers/ignore_uid_controller.py
from typing import TypeAlias, Union, Any, List
from src.my_types import IgnoreUID_Type
from src.models.ignore_uid_model import IgnoreUID_Model
from src.services.ignore_uid_service import IgnoreUID_Service
from src.controllers.base_controller import BaseController


class IgnoreUID_Controller(BaseController):

    def __init__(self, table_model: IgnoreUID_Model):
        super().__init__(service=IgnoreUID_Service(), table_model=table_model)

    def delete(self, ids_to_delete: List[int]) -> bool:
        try:
            self.controller_signals.info.emit(
                f"The records {ids_to_delete} will be deleted."
            )
            if self.service.delete_multiple(ids=ids_to_delete):
                self.controller_signals.success.emit(
                    f"The records {ids_to_delete} will deleted."
                )
                self.refresh_data()
            else:
                self.controller_signals.warning.emit(
                    f"Could not delete records {ids_to_delete}"
                )
        except Exception as e:
            self.controller_signals.error.emit(
                f"An error occurred while deleting the records: {e}"
            )
