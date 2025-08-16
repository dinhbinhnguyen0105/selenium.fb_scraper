# src/services/ignore_phonenumber_service.py
from typing import List, Optional

from src.services.base_service import BaseService
from src.my_types import IgnorePhoneNumber_Type
from src.my_constants import DB_CONNECTION, TABLE_IGNORE_PHONE_NUMBER


class IgnorePhoneNumber_Service(BaseService):
    # CONNECTION_NAME = DB_CONNECTION
    TABLE_NAME = TABLE_IGNORE_PHONE_NUMBER

    def __init__(self, connection_name: str = DB_CONNECTION):
        super().__init__(connection_name, self.TABLE_NAME)

    def create(self, payload: IgnorePhoneNumber_Type) -> Optional[int]:
        return super().create(payload)

    def read(self, record_id: int) -> Optional[IgnorePhoneNumber_Type]:
        data = super().read(record_id=record_id)
        if data:
            return IgnorePhoneNumber_Type.from_db_row(data)
        return None

    def read_all(self, where=None, params=None) -> List[IgnorePhoneNumber_Type]:
        data = super().read_all(where, params)
        return [IgnorePhoneNumber_Type.from_db_row(item) for item in data]

    def delete(self, record_id) -> bool:
        return super().delete(record_id, "id")

    def delete_multiple(self, ids) -> bool:
        return super().delete_multiple(ids, "id")

    def update(self, record_id, payload: IgnorePhoneNumber_Type) -> bool:
        return super().update(record_id, payload, "id")
    
    def export_data_to_csv(self, file_path):
        return super().export_data_to_csv(file_path, IgnorePhoneNumber_Type)
