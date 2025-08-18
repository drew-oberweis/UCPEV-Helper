from telegram import Location
import logging


logger = logging.getLogger(__name__)

class LocPoint:

    def __init__(self, latitude: float, longitude: float, timestamp: float):
        self.latitude = latitude
        self.longitude = longitude
        self.user = None
        self.timestamp = timestamp
        self.speed = 0
        self.heading = None

    def __repr__(self) -> str:
        return f"LocPoint(latitude={self.latitude}, longitude={self.longitude}, speed={self.speed})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LocPoint):
            return False
        return self.latitude == other.latitude and self.longitude == other.longitude

    def set_lat(self, latitude: float) -> None:
        self.latitude = latitude

    def set_lon(self, longitude: float) -> None:
        self.longitude = longitude

    def set_speed(self, speed: int) -> None:
        self.speed = speed

    def set_user(self, user: str) -> None:
        self.user = user

    def set_timestamp(self, timestamp: float) -> None:
        self.timestamp = timestamp

    def set_heading(self, heading: int) -> None:
        self.heading = heading

    def get_lat(self) -> float:
        return self.latitude

    def get_lon(self) -> float:
        return self.longitude

    def get_speed(self) -> int:
        return self.speed

    def get_user(self) -> str:
        return self.user

    def get_timestamp(self) -> float:
        return self.timestamp

    def get_heading(self) -> int:
        return self.heading