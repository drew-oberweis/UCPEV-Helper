import psycopg2
from datetime import datetime
import logging
import random

tables = {
    "users": ["username", "id", "is_admin"],
    "messages": ["msg_id", "user_id", "chat_id", "timestamp", "content"],
    "logs": ["level", "source", "message", "timestamp"], # not used
    "command_history": ["msg_id", "command", "timestamp"],
}

from ride import Ride

logger = logging.getLogger(__name__)

class DB_Credentials:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

class Session:
    def __init__(self, creds: DB_Credentials):
        
        self.conn = psycopg2.connect(
            host=creds.host,
            user=creds.user,
            password=creds.password,
            database=creds.database
        )

        self.cursor = self.conn.cursor()
        self.__verify_tables()
        

    def __verify_tables(self):
        # Check if tables exist, create them if they don't
        for table in tables:
            self.cursor.execute(f"SELECT to_regclass('public.{table}')")
            if not self.cursor.fetchone()[0]:
                self.cursor.execute(f"CREATE TABLE {table} ({', '.join([f'{i} VARCHAR(255)' for i in tables[table]])})")
                self.conn.commit()

    def __sanitize(self, string):
        if(type(string) != str):
            return string
        if(string == None):
            return string
        return string.replace("'", "''")
    
    def sanitize(func):
        def wrapper(self, *args, **kwargs):
            args = [self.__sanitize(i) for i in args]
            kwargs = {k: self.__sanitize(v) for k, v in kwargs.items()}
            return func(self, *args, **kwargs)
        return wrapper

    def execute(self, command):
        result = self.cursor.execute(command)
        self.conn.commit()
        return result
    
    def write_log(self, level, source, message):
        self.cursor.execute(f"INSERT INTO logs (level, source, message, timestamp) VALUES ('{level}', '{source}', '{message}', '{datetime.now()}')")
        self.conn.commit()
    
    def get_users(self, user_id=None, username=None):
        if user_id:
            self.cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
        elif username:
            self.cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
        else:
            self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()
    
    def get_messages(self, msg_id=None, user_id=None, chat_id=None):
        if msg_id:
            self.cursor.execute(f"SELECT * FROM messages WHERE msg_id = '{msg_id}'")
        elif user_id:
            self.cursor.execute(f"SELECT * FROM messages WHERE user_id = '{user_id}'")
        elif chat_id:
            self.cursor.execute(f"SELECT * FROM messages WHERE chat_id = '{chat_id}'")
        else:
            self.cursor.execute("SELECT * FROM messages")
        return self.cursor.fetchall()
    
    def add_user(self, username, user_id, is_admin=False):
        self.cursor.execute(f"INSERT INTO users (username, id, is_admin) VALUES ('{username}', '{user_id}', '{is_admin}')")
        self.conn.commit()

    def rm_user(self, user_id):
        self.cursor.execute(f"DELETE FROM users WHERE id = '{user_id}'")
        self.conn.commit()

    def get_user(self, user_id):
        self.cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
        user = self.cursor.fetchone()
        return user
    
    def update_user(self, user_id, username, is_admin=False): # update username by ID
        self.cursor.execute(f"UPDATE users SET username = '{username}' WHERE id = '{user_id}'")
        self.cursor.execute(f"UPDATE users SET is_admin = '{is_admin}' WHERE id = '{user_id}'")
        self.conn.commit()

    @sanitize
    def add_message(self, msg_id, user_id, chat_id, content):
        self.cursor.execute(f"INSERT INTO messages (msg_id, user_id, chat_id, timestamp, content) VALUES ('{msg_id}', '{user_id}', '{chat_id}', '{datetime.now()}', '{content}')")
        self.conn.commit()

    def rm_message(self, msg_id): # This shouldn't ever be used, but it's here just in case
        self.cursor.execute(f"DELETE FROM messages WHERE msg_id = '{msg_id}'")
        self.conn.commit()