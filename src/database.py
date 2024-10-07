from __future__ import annotations

from contextlib import contextmanager

import pyodbc

from .config import DatabaseSettings


@contextmanager
def connect(settings: DatabaseSettings | None = None):
    connection = pyodbc.connect((settings or DatabaseSettings.from_env()).connection_string(), timeout=5)
    try:
        yield connection
    finally:
        connection.close()


def test_connection(settings: DatabaseSettings | None = None) -> tuple[bool, str]:
    try:
        with connect(settings) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT DB_NAME()")
            return True, f"{cursor.fetchone()[0]} veritabanına bağlanıldı"
    except pyodbc.Error as exc:
        return False, f"SQL Server bağlantısı kullanılamıyor: {exc}"
