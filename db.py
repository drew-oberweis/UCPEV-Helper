import psycopg2
from datetime import datetime
import logging
import random

tables = {
    "users": ["username", "id", "is_admin"],
    "messages": ["msg_id", "user_id", "chat_id", "timestamp", "content"],
    "rides": ["ride_id", "creator_id", "ride_type", "ride_date", "ride_time", "meetup_location", "destination", "description"],
    "logs": ["level", "source", "message", "timestamp"], # not used
    "command_history": ["msg_id", "command", "timestamp"]
}

from ride_convo_handlers import Ride

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
    
    def get_rides(self, creator_id=None, ride_time_after=None, limit=None):
        if creator_id:
            logger.log(logging.DEBUG, f"Getting rides for {creator_id}")
            self.cursor.execute(f"SELECT * FROM rides WHERE creator_id = '{creator_id}'")
        elif ride_time_after:
            logger.log(logging.DEBUG, f"Getting rides after {ride_time_after}")
            self.cursor.execute(f"SELECT * FROM rides WHERE ride_date > '{ride_time_after}'")
        else:
            logger.log(logging.DEBUG, "Getting all rides")
            self.cursor.execute("SELECT * FROM rides")
        result = self.cursor.fetchall()

        rides = []
        for ride in result:
            this_ride = Ride()
            this_ride.set_type(ride[1])
            this_ride.set_date(ride[2])
            this_ride.set_time(ride[3])
            this_ride.set_meetup(ride[4])
            this_ride.set_destination(ride[5])
            this_ride.set_description(ride[6])
            rides.append(this_ride)
            this_ride = None

        if(limit):
            rides = rides[:limit]

        return rides
    
    def get_warnings(self, warn_id=None, user_id=None):
        if warn_id:
            self.cursor.execute(f"SELECT * FROM warnings WHERE warn_id = '{warn_id}'")
        elif user_id:
            self.cursor.execute(f"SELECT * FROM warnings WHERE user_id = '{user_id}'")
        else:
            self.cursor.execute("SELECT * FROM warnings")
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

    def add_message(self, msg_id, user_id, chat_id, content):
        self.cursor.execute(f"INSERT INTO messages (msg_id, user_id, chat_id, timestamp, content) VALUES ('{msg_id}', '{user_id}', '{chat_id}', '{datetime.now()}', '{content}')")
        self.conn.commit()

    def rm_message(self, msg_id): # This shouldn't ever be used, but it's here just in case
        self.cursor.execute(f"DELETE FROM messages WHERE msg_id = '{msg_id}'")
        self.conn.commit()

    def add_ride(self, creator_id, ride_type, ride_date, ride_time, meetup_location, destination, description):
        # random 20 digit number for ID, pray for no collisions
        ride_id = random.randint(0, 99999999999999999999)
        self.cursor.execute(f"INSERT INTO rides (ride_id, creator_id, ride_type, ride_date, ride_time, meetup_location, destination, description) VALUES ('{ride_id}', '{creator_id}', '{ride_type}', '{ride_date}', '{ride_time}', '{meetup_location}', '{destination}', '{description}')")
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