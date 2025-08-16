# src/services/result_service.py
from src.services.base_service import BaseService
from src.my_types import Result_Type
from typing import Optional, List, Any
from src.my_constants import DB_CONNECTION, TABLE_RESULTS


class Result_Service(BaseService):
    TABLE_NAME = TABLE_RESULTS

    def __init__(self, connection_name: str = DB_CONNECTION):
        super().__init__(connection_name, self.TABLE_NAME)

    def create(self, payload: Result_Type) -> Optional[int]:
        return super().create(payload)

    def read(self, record_id: Any) -> Optional[Result_Type]:
        row = super().read(record_id)
        return Result_Type.from_db_row(row) if row else None

    def read_all(self) -> List[Result_Type]:
        rows = super().read_all()
        return [Result_Type.from_db_row(row) for row in rows]

    def update(self, payload: Result_Type) -> bool:
        return super().update(payload)

    def delete(self, record_id: Any) -> bool:
        return super().delete(record_id)

    def delete_multiple(self, ids: List[Any]) -> bool:
        return super().delete_multiple(ids)

    def export_data_to_csv(self, file_path):
        return super().export_data_to_csv(file_path, Result_Type)