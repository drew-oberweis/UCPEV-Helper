import psycopg2
from datetime import datetime
import logging

import environment_handler

logger = logging.getLogger(__name__)

tables = {
    "location_points": [
        {"name": "latitude", "type": "FLOAT"},
        {"name": "longitude", "type": "FLOAT"},
        {"name": "speed", "type": "INTEGER"},
        {"name": "user_id", "type": "VARCHAR(255)"},
        {"name": "timestamp", "type": "INTEGER"},
        {"name": "heading", "type": "INTEGER"},
    ]
}

class Session:
    def __init__(self):
        self.name, self.user, self.password, self.host, self.port, = environment_handler.get_database_config()

        self.connection = psycopg2.connect(
            dbname=self.name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        self.cursor = self.connection.cursor()

        self.create_tables()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def create_tables(self):
        for table_name, columns in tables.items():
            column_defs = ", ".join([f"{col['name']} {col['type']}" for col in columns])
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs});"
            self.cursor.execute(create_table_query)
        self.connection.commit()

    def __sanitize_input(self, data):
        if not data:
            return None
        if type(data) != str:
            return str(data).strip()
        data = data.replace("'", "''")  # Escape single quotes
        return data.strip()

    def sanitize_input(func):
        def wrapper(self, *args, **kwargs):
            sanitized_args = [self.__sanitize_input(arg) for arg in args]
            sanitized_kwargs = {k: self.__sanitize_input(v) for k, v in kwargs.items()}
            return func(self, *sanitized_args, **sanitized_kwargs)
        return wrapper

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            self.connection.rollback()

    def insert_location_point(self, latitude, longitude, speed, user_id, timestamp, heading):
        query = """
        INSERT INTO location_points (latitude, longitude, speed, user_id, timestamp, heading)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        params = (latitude, longitude, speed, user_id, timestamp, heading)
        self.execute_query(query, params)
