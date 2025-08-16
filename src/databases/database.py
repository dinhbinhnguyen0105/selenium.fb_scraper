# src/databases/database.py
import os
from PyQt6.QtSql import QSqlDatabase, QSqlQuery

from src.databases import db_sqls as SQLs
from src import my_constants as constants


def initialize_database():
    if QSqlDatabase.contains(constants.DB_CONNECTION):
        db = QSqlDatabase.database(constants.DB_CONNECTION)
    else:
        db = QSqlDatabase.addDatabase("QSQLITE", constants.DB_CONNECTION)

    os.makedirs(constants.DB_CONTAINER_PATH, exist_ok=True)
    db_path = os.path.abspath(os.path.join(constants.DB_CONTAINER_PATH, "db.db"))
    db.setDatabaseName(db_path)
    if not db.open():
        print(os.path.abspath(db_path))
        raise Exception(
            f"An error occurred while opening the database: {db.lastError().text()}"
        )
    query = QSqlQuery(db)
    query.exec("PRAGMA foreign_keys = ON;")
    query.exec("PRAGMA journal_mode=WAL;")

    if not db.transaction():
        raise Exception("Could not start transaction.")
    try:
        for sql in [SQLs.IGNORE_PHONE_NUMBER, SQLs.IGNORE_UID, SQLs.RESULT]:
            if not query.exec(sql):
                raise Exception(
                    f"An error occurred while creating table: {query.lastError().text()}"
                )
        if not db.commit():
            raise Exception(
                f"Failed to commit database transaction: {db.lastError().text()}"
            )
        return True
    except Exception as e:
        if db.isValid() and db.isOpen() and db.transaction():
            db.rollback()
        raise Exception(f"Failed to initialize database: {str(e)}")
