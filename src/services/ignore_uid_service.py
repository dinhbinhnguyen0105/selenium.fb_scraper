# src/services/ignore_uid_service.py
from typing import Optional, List, Any
from src.services.base_service import BaseService
from src.my_types import IgnoreUID_Type
from src.my_constants import DB_CONNECTION, TABLE_IGNORE_UID


class IgnoreUID_Service(BaseService):
    TABLE_NAME = TABLE_IGNORE_UID

    def __init__(self, connection_name: str = DB_CONNECTION):
        super().__init__(connection_name, self.TABLE_NAME)

    def create(self, payload: IgnoreUID_Type) -> Optional[int]:
        return super().create(payload)

    def read(self, record_id: Any) -> Optional[IgnoreUID_Type]:
        row = super().read(record_id)
        return IgnoreUID_Type.from_db_row(row) if row else None

    def read_all(self) -> List[IgnoreUID_Type]:
        rows = super().read_all()
        return [IgnoreUID_Type.from_db_row(row) for row in rows]

    def update(self, payload: IgnoreUID_Type) -> bool:
        return super().update(payload)

    def delete(self, record_id: Any) -> bool:
        return super().delete(record_id)

    def delete_multiple(self, ids: List[Any]) -> bool:
        return super().delete_multiple(ids)
    
    def export_data_to_csv(self, file_path):
        return super().export_data_to_csv(file_path, IgnoreUID_Type)

