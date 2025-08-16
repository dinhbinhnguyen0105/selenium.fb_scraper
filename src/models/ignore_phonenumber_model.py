# src/models/ignore_phonenumber_model.py
from src.my_constants import TABLE_IGNORE_PHONE_NUMBER
from src.models.base_model import BaseModel


class IgnorePhoneNumber_Model(BaseModel):
    def __init__(self, parent=None):
        super().__init__(TABLE_IGNORE_PHONE_NUMBER, parent)
