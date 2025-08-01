import os.path
import logging

import pandas as pd
import ride
import route

from tabulate import tabulate

logger = logging.getLogger(__name__)

# sheet info, this should probably be in a config file but its 1am and I don't care
sheet_id = '1elIIh9jrFYl2tBIUDy3sIHrNXBirY2wh7naDZacp0SY'
routes_gid = '0'
rides_gid = '1259448335'
cleaned_gid = '360455255'
routes_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json&gid={routes_gid}'
rides_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json&gid={rides_gid}'
cleaned_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json&gid={cleaned_gid}'

def __pull_sheets(page=None): # 1-3 is valid, if page is none, return all pages
    
    sheet_id = '1elIIh9jrFYl2tBIUDy3sIHrNXBirY2wh7naDZacp0SY'
    routes_gid = '0'
    rides_gid = '1259448335'
    cleaned_gid = '360455255'
    routes_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={routes_gid}'
    rides_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={rides_gid}'
    cleaned_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={cleaned_gid}'

    # TODO: Implement caching because this can be slow

    output = None

    if(page == 1):
        logger.debug("Page 1 requested, returning routes")
        output = pd.read_csv(routes_url)
        # logger.debug(f"Routes data: {output.head()}")
    elif(page == 2):
        logger.debug("Page 2 requested, returning rides")
        output = pd.read_csv(rides_url)
        # logger.debug(f"Rides data: {output.head()}")
    elif(page == 3):
        logger.debug("Page 3 requested, returning cleaned rides")
        output = pd.read_csv(cleaned_url)
        # logger.debug(f"Cleaned rides data: {output.head()}")
    elif(page == None):
        # Return all sheets as a dictionary
        logger.debug("No page requested, returning all sheets")
        output = {
            'routes': pd.read_csv(routes_url),
            'rides': pd.read_csv(rides_url),
            'cleaned': pd.read_csv(cleaned_url)
        }
        # logger.debug(f"All sheets data: {output}")

    # print column names for debugging
    debug_print = output.columns.tolist()
    logger.debug(f"COLUMNS: {debug_print}")

    return output

def get_upcoming_rides() -> list[ride.Ride]:
        
    rides_df = __pull_sheets(3) # 3 is cleaned rides, we only care about that here

    rides = ride.get_rides_from_df(rides_df)

    if len(rides) == 0:
        raise IndexError("No upcoming rides found.")
        
    return rides

def get_route(name) -> pd.DataFrame:
    
    routes_df = __pull_sheets(1) # 1 is routes
    routes = route.get_routes_from_df(routes_df)

    for r in routes:
        if r.route == name:
            return r

    return None