# src/controllers/result_controller.py
import webbrowser
from typing import List
from src.models.result_model import Result_Model
from src.services.result_service import Result_Service
from src.controllers.base_controller import BaseController


class Result_Controller(BaseController):
    def __init__(self, table_model: Result_Model):
        super().__init__(service=Result_Service(), table_model=table_model)

    def handle_open_browser(self, url_string: str):
        if not (url_string.startswith("http://") or url_string.startswith("https://")):
            return
        try:
            webbrowser.open_new_tab(url_string)
        except webbrowser.Error as e:
            self.controller_signals.error(
                f"[Browser Error] Couldn't open the browser: {e}\nPlease check your default browser settings."
            )
        except Exception as e:
            self.controller_signals.error(f"[Unknown Error] An error occurred: {e}.")

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
