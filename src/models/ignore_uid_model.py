# src/models/ignore_uid_model.py
from src.my_constants import TABLE_IGNORE_UID
from src.models.base_model import BaseModel


class IgnoreUID_Model(BaseModel):
    def __init__(self, parent=None):
        super().__init__(TABLE_IGNORE_UID, parent)
