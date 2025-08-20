import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Route:
    def __init__(self):
        self.name = ""
        self.start_location = ""
        self.start_pin = ""
        self.notable_location = ""
        self.end_location = ""
        self.end_pin = ""
        self.est_distance = ""
        self.gaia_link = ""
        self.route_description = ""
        self.extra = ""

    def __str__(self):

        # return empty string if route is "Other Event" to avoid cluttering the output
        if self.name == "Other Event":
            return ""

        if self.start_pin != self.start_pin:
            self.start_msg = f"Start Location: {self.start_location}"
        else:
            self.start_msg = f"Start Location: {self.start_location} ({self.start_pin})"

        if self.end_pin != self.end_pin:
            self.end_msg = f"End Location: {self.end_location}"
        else:
            self.end_msg = f"End Location: {self.end_location} ({self.end_pin})"

        notable_msg = ""
        est_distance_msg = ""
        gaia_link_msg = ""
        extra_msg = ""

        if self.notable_location == self.notable_location: #non NaN
            notable_msg = f"\nNotable Location: {self.notable_location}"

        if self.est_distance == self.est_distance: #non NaN
            est_distance_msg = f"\n{self.est_distance} miles"

        if self.gaia_link == self.gaia_link: #non NaN
            gaia_link_msg = f"\nGAIA Link: {self.gaia_link}"

        if self.extra == self.extra: #non NaN
            extra_msg = f"\n{self.extra}"

        route_message = f"Route Name: {self.name}\n{self.start_msg}\n{self.end_msg}{notable_msg}{est_distance_msg}{gaia_link_msg}\n\nRoute Description: {self.route_description}\n\n{extra_msg}"

        return route_message

    #TODO: Add verifiers for relevant fields here
    def set_name(self, name: str):
        self.name = name
    def set_start_location(self, start_location: str):
        self.start_location = start_location
    def set_start_pin(self, start_pin: str):
        self.start_pin = start_pin
    def set_notable_location(self, notable_location: str):
        self.notable_location = notable_location
    def set_end_location(self, end_location: str):
        self.end_location = end_location
    def set_end_pin(self, end_pin: str):
        self.end_pin = end_pin
    def set_est_distance(self, est_distance: str):
        self.est_distance = est_distance
    def set_gaia_link(self, gaia_link: str):
        self.gaia_link = gaia_link
    def set_route_description(self, route_description: str):
        self.route_description = route_description
    def set_extra(self, extra: str):
        self.extra = extra


def get_routes_from_df(routes_df: pd.DataFrame) -> list[Route]:
    routes = []
    for index, row in routes_df.iterrows():
        route = Route()
        route.set_name(row['Name'])
        route.set_start_location(row['Start Location'])
        route.set_start_pin(row['Start Location Pin'])
        route.set_notable_location(row['Notable Location'])
        route.set_end_location(row['End Location'])
        route.set_end_pin(row['End Location Pin'])
        route.set_est_distance(row['Est. Distance'])
        route.set_gaia_link(row['Gaia Link'])
        route.set_route_description(row['Route Description'])
        route.set_extra(row['Extra'])
        routes.append(route)
    return routes