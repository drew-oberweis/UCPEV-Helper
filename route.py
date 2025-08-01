import pandas as pd

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
        if self.start_pin != self.start_pin:
            self.start_msg = f"Start Location: {self.start_location}"
        else:
            self.start_msg = f"Start Location: {self.start_location} ({self.start_pin})"

        if self.end_pin != self.end_pin:
            self.end_msg = f"End Location: {self.end_location}"
        else:
            self.end_msg = f"End Location: {self.end_location} ({self.end_pin})"

        route_message = f"Route Name: {self.name}\n{self.start_msg}\n{self.end_msg}\nPOI: {self.notable_location}\nDistance: {self.est_distance} miles\nGAIA Link: {self.gaia_link}\n\nRoute Description: {self.route_description}\n\n{self.extra}"

        return route_message

    # decorator function to verify that none of the inputs are NaN or empty
    def check_nan(func):
        def wrapper(self, *args, **kwargs):
            for arg in args:
                if pd.isna(arg) or arg == "" or arg != arg:
                    raise ValueError("Input cannot be NaN or empty")
            return func(self, *args, **kwargs)
        return wrapper

    #TODO: Add verifiers for relevant fields here
    @check_nan
    def set_name(self, name: str):
        self.name = name

    @check_nan
    def set_start_location(self, start_location: str):
        self.start_location = start_location

    @check_nan
    def set_start_pin(self, start_pin: str):
        self.start_pin = start_pin

    @check_nan
    def set_notable_location(self, notable_location: str):
        self.notable_location = notable_location

    @check_nan
    def set_end_location(self, end_location: str):
        self.end_location = end_location

    @check_nan
    def set_end_pin(self, end_pin: str):
        self.end_pin = end_pin

    @check_nan
    def set_est_distance(self, est_distance: str):
        self.est_distance = est_distance

    @check_nan
    def set_gaia_link(self, gaia_link: str):
        self.gaia_link = gaia_link

    @check_nan
    def set_route_description(self, route_description: str):
        self.route_description = route_description

    @check_nan
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