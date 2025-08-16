import sys
from PyQt6.QtWidgets import QApplication
from src.app import Application


def main():
    app = QApplication(sys.argv)
    scraper_app = Application()
    scraper_app.run()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
