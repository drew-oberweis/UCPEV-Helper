import datetime
import re
import logging

logger = logging.getLogger(__name__)

class Ride:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.type = ""
        self.date = ""
        self.time = ""
        self.route = ""
        self.pace = "" 
        self.description = ""
        self.id = ""
        self.organizer = ""
    
    # allow a ride to be compared to another, with the comparison being based on the ride date
    def __lt__(self, other):
        return self.date < other.date
    
    def __eq__(self, other):
        return self.date == other.date
    
    def __gt__(self, other):
        return self.date > other.date
    
    def __le__(self, other):
        return self.date <= other.date
    
    def __ge__(self, other):
        return self.date >= other.date
    
    def __ne__(self, other):
        return self.date != other.date

    def __desanitize(self, string):
        if(type(string) != str):
            return string
        if(string == None):
            return string
        return string.replace("''", "'")

    def __str__(self):
        # convert unix timestamp into mm/dd/yyyy format
        logger.log(logging.DEBUG, f"Ride date: {self.date}")
        if (self.type == "Short" or self.type == "Long"):
            return f"Ride type: {self.type}\nDate: {self.nice_date()}\nTime: \nRoute: {self.route}\nPace: {self.pace}\n\n{self.__desanitize(self.description)}"
        else:
            return f"Ride type: {self.type}\nDate: {self.nice_date()}\nTime: {self.__desanitize(self.time)}\nRoute: {self.__desanitize(self.route)}\n\n{self.__desanitize(self.description)}" # skip destination for I2S and Other rides
        
    def str_one_line(self):
        if (self.type == "Short" or self.type == "Long"):
            return f"{self.type} ride on {self.nice_date()} at {self.time} from {self.meetup_location} to {self.destination}"
        else:
            return f"{self.type} ride on {self.nice_date()} at {self.time} at {self.meetup_location}"
        
    def nice_date(self):
        logger.log(logging.DEBUG, f"Ride date: {self.date}")
        return datetime.datetime.fromtimestamp(self.date).strftime("%m/%d/%Y")

    def set_type(self, ride_type):
        if(Verifiers.verify_type(ride_type)):
            self.type = ride_type
        else:
            logger.log(logging.ERROR, f"Invalid ride type: {ride_type}")
            raise ValueError(f"Invalid ride type attempted for ride {self.id}")
    def set_date(self, ride_date):
        if(Verifiers.verify_date(ride_date)):
            # convert from mm/dd/yyyy to unix timestamp
            ride_date = int(datetime.datetime.strptime(ride_date, "%m/%d/%Y").timestamp())
            logger.log(logging.DEBUG, f"Converted date to unix timestamp: {ride_date}")
            self.date = ride_date
        else:
            logger.log(logging.ERROR, f"Invalid date: {ride_date}")
            raise ValueError(f"Invalid date attempted for ride {self.id}")
    def set_time(self, ride_time):
        self.time = ride_time
    def set_route(self, route):
        self.route = route
    def set_description(self, description):
        self.description = description
    def set_id(self, ride_id):
        self.id = ride_id
    def set_organizer(self, organizer):
        self.organizer = organizer
    def set_name(self, name):
        self.name = name
    def set_pace(self, pace): 
        if(Verifiers.verify_pace(pace)):
            self.pace = pace
        else:
            logger.log(logging.ERROR, f"Invalid pace: {pace} for ride {self.id}")
            raise ValueError(f"Invalid pace attempted for ride {self.id}")

    ride_type_options = ["Short", "Long", "I2S", "Other"]
    ride_pace_options = ["Casual", "Fast", "Both (Separate rides)"]

class Verifiers:
    def verify_pace(pace):
        return pace in Ride.ride_pace_options
    def verify_type(ride_type):
        return ride_type in Ride.ride_type_options
    def verify_date(date): # for static method
        regex_date = "^([1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/([0-9]{4})$" # TODO: unify this into utils.py or something
        if(not(re.match(regex_date, date))):
            logger.log(logging.DEBUG, f"Date {date} did not pass date validation from regex mismatch")
            return False
        logger.log(logging.DEBUG, f"Date {date} passed date validation")
        return True