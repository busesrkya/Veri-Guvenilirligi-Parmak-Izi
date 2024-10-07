from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class DatabaseSettings:
    server: str = "localhost"
    database: str = "DataReliabilityDB"
    driver: str = "ODBC Driver 18 for SQL Server"
    trusted_connection: str = "yes"
    trust_server_certificate: str = "yes"
    username: str | None = None
    password: str | None = None

    @classmethod
    def from_env(cls) -> "DatabaseSettings":
        load_dotenv()
        return cls(
            server=os.getenv("DB_SERVER", "localhost"),
            database=os.getenv("DB_NAME", "DataReliabilityDB"),
            driver=os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
            trusted_connection=os.getenv("DB_TRUSTED_CONNECTION", "yes"),
            trust_server_certificate=os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes"),
            username=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
        )

    def connection_string(self) -> str:
        parts = [
            f"DRIVER={{{self.driver}}}",
            f"SERVER={self.server}",
            f"DATABASE={self.database}",
            f"TrustServerCertificate={self.trust_server_certificate}",
        ]
        if self.username and self.password:
            parts.extend([f"UID={self.username}", f"PWD={self.password}"])
        else:
            parts.append(f"Trusted_Connection={self.trusted_connection}")
        return ";".join(parts)


DEFAULT_WEIGHTS = {
    "completeness": 1.0,
    "validity": 1.0,
    "consistency": 1.0,
    "uniqueness": 1.0,
    "context_stability": 1.0,
    "temporal_stability": 1.0,
}

DEFAULT_RANGES = {
    "temperature": (-40.0, 180.0),
    "pressure": (0.0, 20.0),
    "vibration": (0.0, 30.0),
    "humidity": (0.0, 100.0),
    "operating_speed": (0.0, 6000.0),
    "machine_load": (0.0, 120.0),
}
