# src/app.py
from src.views.mainwindow import MainWindow
from src.databases.database import initialize_database


class Application:
    def __init__(self):
        pass

    def run(self):
        if not initialize_database():
            raise Exception("initialize database failed!")

        self.mainwindow = MainWindow()
        self.mainwindow.show()
        print("Scraper application is running ...")
