# src/controllers/base_controller.py
from typing import TypeAlias, Union
from src.my_types import ControllerSignals
from src.services.ignore_phonenumber_service import IgnorePhoneNumber_Service
from src.services.ignore_uid_service import IgnoreUID_Service
from src.services.result_service import Result_Service
from src.models.result_model import Result_Model
from src.models.ignore_phonenumber_model import IgnorePhoneNumber_Model
from src.models.ignore_uid_model import IgnoreUID_Model

Service_Type: TypeAlias = Union[
    IgnorePhoneNumber_Service,
    IgnoreUID_Service,
    Result_Service,
]
Model_Type: TypeAlias = Union[
    Result_Model,
    IgnorePhoneNumber_Model,
    IgnoreUID_Model,
]


class BaseController:
    def __init__(self, service: Service_Type, table_model: Model_Type):
        self.table_model = table_model
        self.service = service
        self.controller_signals = ControllerSignals()

    def refresh_data(self):
        self.table_model.select()
        self.controller_signals.info.emit(
            f"Data '{self.table_model.tableName()}' has been refreshed."
        )
