# src/controllers/ignore_uid_controller.py
from typing import TypeAlias, Union, Any, List
from src.my_types import IgnorePhoneNumber_Type
from src.models.ignore_phonenumber_model import IgnorePhoneNumber_Model
from src.services.ignore_phonenumber_service import IgnorePhoneNumber_Service
from src.controllers.base_controller import BaseController


class IgnorePhoneNumber_Controller(BaseController):

    def __init__(self, table_model: IgnorePhoneNumber_Model):
        super().__init__(service=IgnorePhoneNumber_Service(), table_model=table_model)

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
