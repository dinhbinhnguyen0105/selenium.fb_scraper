# src/my_types.py
from PyQt6.QtCore import pyqtSignal, QObject
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class IgnoreUID_Type:
    id: Optional[int]
    value: str
    created_at: Optional[str]

    @staticmethod
    def from_db_row(row_data: Dict[str, Any]) -> "IgnoreUID_Type":
        return IgnoreUID_Type(
            id=row_data.get("id"),
            value=row_data.get("value"),
            created_at=row_data.get("created_at"),
        )


@dataclass
class IgnorePhoneNumber_Type:
    id: Optional[int]
    value: str
    created_at: Optional[str]

    @staticmethod
    def from_db_row(row_data: Dict[str, Any]) -> "IgnorePhoneNumber_Type":
        return IgnorePhoneNumber_Type(
            id=row_data.get("id"),
            value=row_data.get("value"),
            created_at=row_data.get("created_at"),
        )


@dataclass
class Result_Type:
    id: Optional[int]
    article_url: str
    article_content: str
    author_url: str
    author_name: str
    contact: str
    created_at: Optional[str]

    @staticmethod
    def from_db_row(row_data: Dict[str, Any]) -> "Result_Type":
        return Result_Type(
            id=row_data.get("id"),
            article_url=row_data.get("article_url"),
            article_content=row_data.get("article_content"),
            author_url=row_data.get("author_url"),
            author_name=row_data.get("author_name"),
            contact=row_data.get("contact"),
            created_at=row_data.get("created_at"),
        )


@dataclass
class TaskInfo:
    action_name: str
    object_name: str
    dir_name: str
    user_data_dir: str
    headless: str
    target_keywords: List[str]
    ignore_keywords: List[str]
    post_num: int


class ControllerSignals(QObject):
    error = pyqtSignal(str)
    info = pyqtSignal(str)
    warning = pyqtSignal(str)
    success = pyqtSignal()


class WorkerSignals(QObject):
    main_progress_signal = pyqtSignal(str, int, int)
    sub_progress_signal = pyqtSignal(str, int, int)
    error_signal = pyqtSignal(TaskInfo, int, str)  # task_info, retry_num, err_msg
    succeeded_signal = pyqtSignal(
        TaskInfo, int, str
    )  # task_info, retry_num, Optional[connection_name]
    info_signal = pyqtSignal(str)
    data_signal = pyqtSignal(str, list)
    cleanup_signal = pyqtSignal(str)
