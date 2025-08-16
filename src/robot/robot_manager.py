import os
import json
from collections import deque
from typing import Any, List, Dict
from PyQt6.QtCore import QThreadPool, QObject, pyqtSlot
from PyQt6.QtSql import QSqlDatabase

from src.my_types import TaskInfo, WorkerSignals
# from src.robot.browser_worker import BrowserWorker
from src.robot.selenium_worker import BrowserWorker


class RobotManager(QObject):
    def __init__(self, parent=None):
        super(RobotManager, self).__init__(parent)
        self.threadpool = QThreadPool.globalInstance()
        self.pending_tasks = deque()
        self.robot_manager_signals = WorkerSignals()
        self.total_tasks_initial = 0
        self.retry_num = 0
        self.tasks_succeeded_num = 0
        self.tasks_failed_num = 0
        self.task_in_progress = {}

    def setup_threadpool(self, payload: Dict[str, Any]):
        max_thread = min(payload.get("thread_num", 1), self.threadpool.maxThreadCount())
        max_retries = payload.get("retry_num", 1)

        self.threadpool.setMaxThreadCount(max_thread)
        self.retry_num = max_retries

    @pyqtSlot(list)
    def add_tasks(self, task_list: List[TaskInfo]):
        for task in task_list:
            self.pending_tasks.append((task, self.retry_num))
        self.total_tasks_initial += len(task_list)
        self.robot_manager_signals.info_signal.emit(
            f"Add {len(task_list)} tasks; total={self.total_tasks_initial}"
        )
        self.try_start_tasks()

    @pyqtSlot()
    def try_start_tasks(self):
        while (
            self.pending_tasks
            and self.threadpool.activeThreadCount() < self.threadpool.maxThreadCount()
        ):
            task_info, retry_num = self.pending_tasks.popleft()
            worker = BrowserWorker(task_info=task_info, retry_num=retry_num)
            worker.worker_signals.succeeded_signal.connect(self.on_worker_finished)
            worker.worker_signals.error_signal.connect(self.on_worker_error)
            worker.worker_signals.main_progress_signal.connect(
                self.on_worker_main_progress
            )
            worker.worker_signals.sub_progress_signal.connect(
                self.on_worker_sub_progress
            )
            worker.worker_signals.info_signal.connect(self.on_worker_message)
            worker.worker_signals.cleanup_signal.connect(self.cleanup_connection)
            # worker.worker_signals.data_signal.connect(self.on_worker_data)
            self.task_in_progress[id(worker)] = (task_info, retry_num, worker)

            self.threadpool.start(worker)
            self.robot_manager_signals.info_signal.emit(
                f"Started task {task_info.dir_name} retry={retry_num}"
            )

    @pyqtSlot(TaskInfo, int)
    def on_worker_finished(self, task_info: TaskInfo, retry_num: int):
        worker_id = next(
            (
                key
                for key, value in self.task_in_progress.items()
                if value[0] is task_info
            ),
            None,
        )
        if worker_id is not None:
            del self.task_in_progress[worker_id]
        self.tasks_succeeded_num += 1
        self.robot_manager_signals.info_signal.emit(
            f"Task {task_info.dir_name} done. \
            {self.tasks_succeeded_num}/{self.total_tasks_initial}"
        )
        self.try_start_tasks()
        if self.tasks_succeeded_num + self.tasks_failed_num == self.total_tasks_initial:
            self.robot_manager_signals.succeeded_signal.emit(task_info, retry_num, "")
            # self.robot_manager_signals.finished_signal.emit()

    @pyqtSlot(TaskInfo, int, str)
    def on_worker_error(self, task_info: TaskInfo, retry_num: int, message: str):
        self.robot_manager_signals.info_signal.emit(
            f"Error on {task_info.dir_name}: {message}"
        )
        if retry_num > 0:
            self.pending_tasks.append((task_info, retry_num - 1))
            self.robot_manager_signals.info_signal.emit(
                f"Re-queue task {task_info.dir_name}, retries left {retry_num - 1}"
            )
        else:
            self.tasks_failed_num += 1
            self.robot_manager_signals.info_signal.emit(
                f"Task {task_info.dir_name} permanently failed."
            )
        self.try_start_tasks()

    @pyqtSlot(str, int, int)
    def on_worker_main_progress(
        self, object_name: str, total_group: int, current_group: int
    ):
        self.robot_manager_signals.main_progress_signal.emit(
            object_name, total_group, current_group
        )

    @pyqtSlot(str, int, int)
    def on_worker_sub_progress(
        self, object_name: str, total_post: int, current_post: int
    ):
        self.robot_manager_signals.sub_progress_signal.emit(
            object_name, total_post, current_post
        )

    @pyqtSlot(str)
    def on_worker_message(self, msg: str):
        self.robot_manager_signals.info_signal.emit(msg)

    @pyqtSlot(str)
    def cleanup_connection(self, connection_name):
        QSqlDatabase.removeDatabase(connection_name)
