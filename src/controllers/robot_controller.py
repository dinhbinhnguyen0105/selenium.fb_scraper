# src/controllers/robot_controller.py
import os
from typing import List
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot
from src.my_types import TaskInfo, WorkerSignals
from src.robot.robot_manager import RobotManager


class RobotController(QObject):
    bot_finished_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.robot_controller_signals = WorkerSignals()
        self.robot_manager = RobotManager()
        # self.robot_manager.robot_manager_signals.main_progress_signal.connect(
        #     self.robot_controller_signals.main_progress_signal
        # )
        # self.robot_manager.robot_manager_signals.sub_progress_signal.connect(
        #     self.robot_controller_signals.sub_progress_signal
        # )
        self.robot_manager.robot_manager_signals.info_signal.connect(
            self.robot_controller_signals.info_signal
        )
        self.robot_manager.robot_manager_signals.succeeded_signal.connect(
            self.robot_controller_signals.succeeded_signal
        )
        # self.robot_manager.robot_manager_signals.error_signal.connect(
        #     self.robot_controller_signals.error_signal
        # )

    @pyqtSlot()
    def run_task(
        self,
        action_name: str,
        object_name_list: List[str],
        user_data_dir_list: List[str],
        target_keywords: List[str],
        ignore_keywords: List[str],
        headless: bool,
    ):
        settings_max_thread = len(user_data_dir_list)
        settings_max_retries = 0
        post_num = 200

        tasks = []
        for index, user_data_dir in enumerate(user_data_dir_list):
            if not os.path.exists(user_data_dir):
                continue
            task = TaskInfo(
                action_name=action_name,
                object_name=object_name_list[index],
                user_data_dir=user_data_dir,
                dir_name=os.path.basename(user_data_dir),
                headless=headless,
                target_keywords=target_keywords,
                ignore_keywords=ignore_keywords,
                post_num=post_num,
            )
            tasks.append(task)

        self.robot_manager.setup_threadpool(
            {
                "thread_num": settings_max_thread,
                "retry_num": settings_max_retries,
            }
        )
        self.robot_manager.add_tasks(task_list=tasks)
