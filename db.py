import psycopg2
from datetime import datetime
import logging
import random

tables = {
    "users": ["username", "id", "is_admin"],
    "messages": ["msg_id", "user_id", "chat_id", "timestamp", "content"],
    "rides": ["ride_id", "creator_id", "ride_type", "ride_date", "ride_time", "meetup_location", "destination", "description", "pace"],
    "logs": ["level", "source", "message", "timestamp"], # not used
    "command_history": ["msg_id", "command", "timestamp"]
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
    
    def __deserialize(self, ride):
        this_ride = Ride()
        this_ride.set_id(ride[0])
        this_ride.set_type(ride[2])
        this_ride.set_date(int(float(ride[3])))
        this_ride.set_time(ride[4])
        this_ride.set_meetup(ride[5])
        this_ride.set_destination(ride[6])
        this_ride.set_pace(ride[8])
        this_ride.set_description(ride[7])
        return this_ride

    
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
    
    def get_ride(self, ride_id): # returns the ride object, or the next ride if ride_id is None
        # make sure to get the next ride *after* the current time
        if ride_id:
            self.cursor.execute(f"SELECT * FROM rides WHERE ride_id = '{ride_id}' AND ride_date > '{datetime.now().timestamp()} ORDER BY ride_date ASC LIMIT 1'")
        else:
            self.cursor.execute(f"SELECT * FROM rides WHERE ride_date > '{datetime.now().timestamp()}' ORDER BY ride_date ASC LIMIT 1")
        ride = self.cursor.fetchone()

        if not ride:
            return None

        this_ride = self.__deserialize(ride)
        return this_ride
    
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

        logger.log(logging.DEBUG, f"Got {len(result)} rides")

        for ride in result:

            this_ride = self.__deserialize(ride)
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

    def update(self, ride, ride_id, field, value):
        self.cursor.execute(f"UPDATE rides SET {field} = '{value}' WHERE ride_id = '{ride_id}'")
        self.conn.commit()

    @sanitize
    def add_message(self, msg_id, user_id, chat_id, content):
        self.cursor.execute(f"INSERT INTO messages (msg_id, user_id, chat_id, timestamp, content) VALUES ('{msg_id}', '{user_id}', '{chat_id}', '{datetime.now()}', '{content}')")
        self.conn.commit()

    def rm_message(self, msg_id): # This shouldn't ever be used, but it's here just in case
        self.cursor.execute(f"DELETE FROM messages WHERE msg_id = '{msg_id}'")
        self.conn.commit()

    @sanitize
    def add_ride(self, creator_id, ride_type, ride_date, ride_time, meetup_location, destination, pace, description):
        # random 20 digit number for ID, pray for no collisions
        ride_id = random.randint(0, 99999999999999999999)
        ride_date = int(ride_date)
        self.cursor.execute(f"INSERT INTO rides (ride_id, creator_id, ride_type, ride_date, ride_time, meetup_location, destination, pace, description) VALUES ('{ride_id}', '{creator_id}', '{ride_type}', '{ride_date}', '{ride_time}', '{meetup_location}', '{destination}', '{pace}', '{description}')")
        self.conn.commit()

    def rm_ride(self, ride_id):
        self.cursor.execute(f"DELETE FROM rides WHERE ride_id = '{ride_id}'")
        self.conn.commit()

    def update_ride(self, ride_id, field, value):
        self.cursor.execute(f"UPDATE rides SET {field} = '{value}' WHERE ride_id = '{ride_id}'")
        self.conn.commit()

    @sanitize
    def add_warning(self, user_id, reason):
        user_id = self.__sanitize(user_id)
        reason = self.__sanitize(reason)
        self.cursor.execute(f"INSERT INTO warnings (user_id, reason, timestamp) VALUES ('{user_id}', '{reason}', '{datetime.now()}')")
        self.conn.commit()

    @sanitize
    def rm_warning(self, warn_id):
        warn_id = self.__sanitize(warn_id)
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