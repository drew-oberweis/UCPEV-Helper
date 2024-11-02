import psycopg2
from datetime import datetime
import logging

tables = {
    "users": ["db_user_id", "username", "id"],
    "messages": ["msg_id", "user_id", "chat_id", "timestamp", "content"],
    "rides": ["ride_id", "creator_id", "ride_time", "meetup_location", "destination", "description"],
    "warnings": ["warn_id", "user_id", "reason", "timestamp"],
    "logs": ["log_id", "level", "source", "message", "timestamp"]
}

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
                # make first column of each table primary key and autoincrement
                self.cursor.execute(f"ALTER TABLE {table} ADD PRIMARY KEY ({tables[table][0]})")
                self.cursor.execute(f"ALTER TABLE {table} ALTER COLUMN {tables[table][0]} SET GENERATED ALWAYS AS IDENTITY")
                self.conn.commit()


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
    
    def get_rides(self, ride_id=None, creator_id=None, ride_time_after=None):
        if ride_id:
            self.cursor.execute(f"SELECT * FROM rides WHERE ride_id = '{ride_id}'")
        elif creator_id:
            self.cursor.execute(f"SELECT * FROM rides WHERE creator_id = '{creator_id}'")
        elif ride_time_after:
            self.cursor.execute(f"SELECT * FROM rides WHERE ride_time > '{ride_time_after}'")
        else:
            self.cursor.execute("SELECT * FROM rides")
        return self.cursor.fetchall()
    
    def get_warnings(self, warn_id=None, user_id=None):
        if warn_id:
            self.cursor.execute(f"SELECT * FROM warnings WHERE warn_id = '{warn_id}'")
        elif user_id:
            self.cursor.execute(f"SELECT * FROM warnings WHERE user_id = '{user_id}'")
        else:
            self.cursor.execute("SELECT * FROM warnings")
        return self.cursor.fetchall()
    
    def add_user(self, username, user_id):
        self.cursor.execute(f"INSERT INTO users (username, id) VALUES ('{username}', '{user_id}')")
        self.conn.commit()

    def rm_user(self, user_id):
        self.cursor.execute(f"DELETE FROM users WHERE id = '{user_id}'")
        self.conn.commit()

    def add_message(self, msg_id, user_id, chat_id, content):
        self.cursor.execute(f"INSERT INTO messages (msg_id, user_id, chat_id, timestamp, content) VALUES ('{msg_id}', '{user_id}', '{chat_id}', '{datetime.now()}', '{content}')")
        self.conn.commit()

    def rm_message(self, msg_id): # This shouldn't ever be used, but it's here just in case
        self.cursor.execute(f"DELETE FROM messages WHERE msg_id = '{msg_id}'")
        self.conn.commit()

    def add_ride(self, creator_id, ride_time, meetup_location, destination, description):
        self.cursor.execute(f"INSERT INTO rides (creator_id, ride_time, meetup_location, destination, description) VALUES ('{creator_id}', '{ride_time}', '{meetup_location}', '{destination}', '{description}')")
        self.conn.commit()

    def rm_ride(self, ride_id):
        self.cursor.execute(f"DELETE FROM rides WHERE ride_id = '{ride_id}'")
        self.conn.commit()

    def add_warning(self, user_id, reason):
        self.cursor.execute(f"INSERT INTO warnings (user_id, reason, timestamp) VALUES ('{user_id}', '{reason}', '{datetime.now()}')")
        self.conn.commit()

    def rm_warning(self, warn_id):
        self.cursor.execute(f"DELETE FROM warnings WHERE warn_id = '{warn_id}'")
        self.conn.commit()

if(__name__ == "__main__"):

    # for debugging, or to manually force table verification/creation

    import dotenv # we don't normally want to import this, but it is needed to test DB connections
    import os
    dotenv.load_dotenv()

    host = os.getenv("postgres_host")
    user = os.getenv("postgres_user")
    password = os.getenv("postgres_pass")
    database = os.getenv("postgres_db")

    session = Session(host, user, password, database)
    print("Tables verified")