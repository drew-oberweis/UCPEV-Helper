import datetime
import re
import logging

logger = logging.getLogger(__name__)

class Ride:
    def __init__(self):
        self.id = ""
        self.type = ""
        self.date = ""
        self.time = ""
        self.meetup_location = ""
        self.destination = ""
        self.pace = "" 
        self.description = ""
        self.id = ""
    
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
            return f"Ride type: {self.type}\nDate: {self.nice_date()}\nTime: {self.__desanitize(self.time)}\nMeetup: {self.__desanitize(self.meetup_location)}\nDestination: {self.__desanitize(self.destination)}\nPace: {self.pace}\n\n{self.__desanitize(self.description)}"
        else:
            return f"Ride type: {self.type}\nDate: {self.nice_date()}\nTime: {self.__desanitize(self.time)}\nMeetup: {self.__desanitize(self.meetup_location)}\n\n{self.__desanitize(self.description)}" # skip destination for I2S and Other rides
        
    def str_one_line(self):
        if (self.type == "Short" or self.type == "Long"):
            return f"{self.type} ride on {self.nice_date()} at {self.time} from {self.meetup_location} to {self.destination}"
        else:
            return f"{self.type} ride on {self.nice_date()} at {self.time} at {self.meetup_location}"
        
    def nice_date(self):
        return datetime.datetime.fromtimestamp(self.date).strftime("%m/%d/%Y")

    def set_type(self, ride_type):
        self.type = ride_type
    def set_date(self, ride_date):
        if type(ride_date) == int:
            self.date = ride_date
        else:
            raise ValueError("Ride date must be an integer")
    def set_time(self, ride_time):
        self.time = ride_time
    def set_meetup(self, meetup_location):
        self.meetup_location = meetup_location
    def set_destination(self, destination):
        self.destination = destination
    def set_description(self, description):
        self.description = description
    def set_id(self, ride_id):
        self.id = ride_id
    def set_pace(self, pace): 
        if (pace not in self.ride_pace_options):
            raise ValueError("Invalid pace")
        self.pace = pace

    ride_type_options = ["Short", "Long", "I2S", "Other"]
    ride_pace_options = ["Casual", "Fast", "Both (Separate rides)"]