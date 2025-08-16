# src/models/result_model.py
from src.my_constants import TABLE_RESULTS
from src.models.base_model import BaseModel


class Result_Model(BaseModel):
    def __init__(self, parent=None):
        super().__init__(TABLE_RESULTS, parent)
