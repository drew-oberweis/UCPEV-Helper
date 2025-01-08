import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os
import json
import db

class Ride:
    __vehicle = None
    __rider = None
    __name = None
    __id = None

    # times are in unix timestamps
    # for whatever reason, YT stores the times 20 years in the past.
    # Resolved by adding 630720000 (20 years in seconds) to the timestamps
    __timeOffset = 630720000
    __startTime = None
    __endTime = None
    __duration = None

    __locationPoints = []
    __vehiclePoints = []

    # list of RidePoint objects
    __path = []

    # other data, direct import from JSON
    __gpsTopSpeedLongitude = None
    __gpsTopSpeedLatitude = None
    __escTopSpeedLongitude = None
    __escTopSpeedLatitude = None

    __elevationLoss = None
    __elevationGain = None

    __gpsAverageSpeed = None
    __gpsTopSpeed = None
    __escAverageSpeed = None
    __escTopSpeed = None

    __escEfficiency = None
    __escTotalDistance = None
    __gpsTotalDistance = None

    def __init__(self, path):
        raw = None
        with open(path, 'r') as f:
            raw = json.load(f)

        self.parseRide(raw)
        self.mergePoints()

    def setVehicle(self, vehicle):
        self.__vehicle = vehicle

    def setRider(self, rider):
        self.__rider = rider

    def setName(self, name):
        self.__name = name

    def setId(self, id):
        self.__id = id

    def getVehicle(self):
        return self.__vehicle
    
    def getRider(self):
        return self.__rider
    
    def getName(self):
        return self.__name
    
    def getId(self):
        return self.__id

    def mergePoints(self):
        """
        Merge the LocationPoint and VehicleDataPoint objects into one based on their time
        They do not have perfect time alignment, so we just pick the closest match
        We have WAY more VehicleDataPoints than LocationPoints

        LocationPoints have a position associated, VehicleData does not.
        Therefore, merge direction will be from VehicleDataPoint to LocationPoint
        The extra data from VehicleDataPoint might be used later, so it remains attached.
        However, we do not know the location of each VehicleDataPoint, so it can't be merged into anything
        """

        for i in self.__locationPoints:
            # find the closest VehicleDataPoint
            closest = None
            closestTime = None
            for j in self.__vehiclePoints:
                if closest == None:
                    closest = j
                    closestTime = abs(i.time - j.time)
                else:
                    if abs(i.time - j.time) < closestTime:
                        closest = j
                        closestTime = abs(i.time - j.time)

            # create a RidePoint object
            ridePoint = RidePoint()
            ridePoint.setLocationPoint(i)
            ridePoint.setVehiclePoint(closest)

            # copy data from LocationPoint
            ridePoint.lp_speed = i.speed
            ridePoint.lp_altitude = i.altitude
            ridePoint.lp_latitude = i.latitude
            ridePoint.lp_longitude = i.longitude
            ridePoint.lp_position = i.position
            ridePoint.lp_verticalAccuracy = i.verticalAccuracy
            ridePoint.lp_horizontalAccuracy = i.horizontalAccuracy
            ridePoint.lp_speedAccuracy = i.speedAccuracy

            # copy data from VehicleDataPoint
            ridePoint.vp_esc = closest.esc
            ridePoint.vp_acceleration = closest.acceleration
            ridePoint.vp_batteryPct = closest.batteryPct
            ridePoint.vp_speed = closest.speed
            ridePoint.vp_distanceTraveledInMeters = closest.distanceTraveledInMeters
            
            ridePoint.vp_whTotal = closest.whTotal
            ridePoint.vp_whChargeTotal = closest.whChargeTotal
            ridePoint.vp_whRecharged = closest.whRecharged
            ridePoint.vp_whConsumed = closest.whConsumed
            ridePoint.vp_whNet = closest.whNet
            ridePoint.vp_voltage = closest.voltage
            
            ridePoint.vp_rpm = closest.rpm
            ridePoint.vp_inputCurrent = closest.inputCurrent
            ridePoint.vp_motorCurrent = closest.motorCurrent

            ridePoint.speed = i.speed
            ridePoint.acceleration = closest.acceleration
            ridePoint.batteryPct = closest.batteryPct
            ridePoint.distance = closest.distanceTraveledInMeters

            if(ridePoint.acceleration == None):
                ridePoint.acceleration = 0

            self.__path.append(ridePoint)
    
    def parseRide(self, rideData): # rideData is a dictionary
        self.setVehicle(rideData.get('vehicle').get('name'))
        self.setRider("John Doe") # TODO: have rider name be provided
        self.setName(rideData.get('rideTitle'))
        self.setId(rideData.get('id'))
        self.__startTime = rideData.get('startedAt')
        self.__endTime = rideData.get('endedAt')
        self.__duration = self.__endTime - self.__startTime

        self.__gpsTopSpeedLongitude = rideData.get('gpsTopSpeedLongitude')
        self.__gpsTopSpeedLatitude = rideData.get('gpsTopSpeedLatitude')
        self.__escTopSpeedLongitude = rideData.get('escTopSpeedLongitude')
        self.__escTopSpeedLatitude = rideData.get('escTopSpeedLatitude')

        self.__elevationLoss = rideData.get('elevationLoss')
        self.__elevationGain = rideData.get('elevationGain')

        self.__gpsAverageSpeed = rideData.get('gpsAverageSpeed')
        self.__gpsTopSpeed = rideData.get('gpsTopSpeed')
        self.__escAverageSpeed = rideData.get('escAverageSpeed')
        self.__escTopSpeed = rideData.get('escTopSpeed')

        self.__escEfficiency = rideData.get('escEfficiency')
        self.__escTotalDistance = rideData.get('escTotalDistanceMetres')
        self.__gpsTotalDistance = rideData.get('gpsTotalDistanceMetres')

        locationData = rideData.get('locationData') # this is a list of dictionaries, each entry is a datapoint
        
        for i in locationData:
            locationPoint = LocationPoint()
            locationPoint.time = i.get('forDate')
            locationPoint.speed = i.get('speed')
            locationPoint.altitude = i.get('altitude')
            locationPoint.latitude = i.get('latitude')
            locationPoint.longitude = i.get('longitude')
            locationPoint.position = (locationPoint.latitude, locationPoint.longitude)
            locationPoint.verticalAccuracy = i.get('verticalAccuracy')
            locationPoint.horizontalAccuracy = i.get('horizontalAccuracy')
            locationPoint.speedAccuracy = i.get('speedAccuracy')

            self.__locationPoints.append(locationPoint)

        vehicleData = rideData.get('vehicleData') # this is a list of dictionaries, each entry is a datapoint

        for i in vehicleData:
            vehicleDataPoint = VehiclePoint()
            vehicleDataPoint.time = i.get('forDate')
            
            vescData = i.get('vescData')
            vehicleDataPoint.esc = vescData.get('hardware')
            vehicleDataPoint.acceleration = vescData.get('acceleration')
            vehicleDataPoint.batteryPct = vescData.get('batteryPct')
            vehicleDataPoint.speed = vescData.get('speed')
            vehicleDataPoint.distanceTraveledInMeters = vescData.get('distanceTraveledInMeters')
            
            vehicleDataPoint.whTotal = vescData.get('whTot')
            vehicleDataPoint.whChargeTotal = vescData.get('whChargeTot')
            vehicleDataPoint.whRecharged = vescData.get('whRecharged')
            vehicleDataPoint.whConsumed = vescData.get('whConsumed')
            vehicleDataPoint.whNet = vescData.get('whNet')
            vehicleDataPoint.voltage = vescData.get('voltageIn')

            vehicleDataPoint.rpm = vescData.get('correctedRpm')
            vehicleDataPoint.inputCurrent = vescData.get('currentInTot')
            vehicleDataPoint.motorCurrent = vescData.get('averageMotorCurrent')

            self.__vehiclePoints.append(vehicleDataPoint)

    def renderMap(self, filename=None, style="satellite", lineColor="speed", outputWidth=1000):
        # plot the path on a map
        # we have a list of RidePoint objects
        # we can extract the latitude and longitude from each RidePoint object
        # and plot it on a map

        # check if the ride is below the render threshold
        minPoints = 50
        if len(self.__path) < minPoints:
            raise Exception("Ride has less than " + str(minPoints) + " points, not enough to render a map")

        # first, extract the latitude and longitude from each RidePoint object
        latitudes = []
        longitudes = []
        for i in self.__path:
            latitudes.append(i.lp_latitude)
            longitudes.append(i.lp_longitude)

        # put all the data into a pandas dataframe
        data = {'latitude': latitudes, 'longitude': longitudes}
        df = pd.DataFrame(data)

        max_lat = max(latitudes)
        min_lat = min(latitudes)
        max_lon = max(longitudes)
        min_lon = min(longitudes)
        center = {"lat": (max_lat + min_lat) / 2, "lon": (max_lon + min_lon) / 2}

        padding = 0.05

        lat_padding = (max_lat - min_lat) * padding
        lon_padding = (max_lon - min_lon) * padding

        # set mapbox access token
        mapbox_access_token = "pk.eyJ1IjoiZHJldy1vYmVyd2Vpcy0yIiwiYSI6ImNtNW5tOXdlNTBjZGQya29qMmcwdTJ1Z3kifQ.L1p4f3oNTJh0hGrWEK6qLQ"

        def rescale(values): # rescale values to logarithmic scale
            log_scaled_data = np.log1p(values)  # log1p(x) computes log(1 + x)

            # Normalize after log-scaling
            normalized_data = (log_scaled_data - log_scaled_data.min()) / (log_scaled_data.max() - log_scaled_data.min())

            return normalized_data
            

        # Color scale for the line
        colors = []
        if lineColor == "speed":
            scaledValues = rescale([i.speed for i in self.__path])
            maxValue = max([i for i in scaledValues])
            minValue = min([i for i in scaledValues])
            values = [i for i in scaledValues]
            # red is min speed, green is max speed
        elif lineColor == "battery":
            maxValue = max([i.batteryPct for i in self.__path])
            minValue = min([i.batteryPct for i in self.__path])
            values = [i.batteryPct for i in self.__path]
            # red is min battery, green is max battery
        elif lineColor == "acceleration":
            maxValue = max([i.acceleration for i in self.__path])
            minValue = min([i.acceleration for i in self.__path])
            values = [i.acceleration for i in self.__path]
            # red is min acceleration, green is max acceleration

        colors = [f"hsl({(value - minValue) / (maxValue - minValue) * 120}, 100%, 50%)" for value in values]

        df['colors'] = colors

        map_layout = go.Layout(
            mapbox=dict(
                style=style,
                center=center,
                zoom=10,
                bounds={
                    "north": max_lat + lat_padding,
                    "south": min_lat - lat_padding,
                    "east": max_lon + lon_padding,
                    "west": min_lon - lon_padding
                },
                accesstoken=mapbox_access_token
            ),
            showlegend=False,  # Hide legend
            margin=dict(l=0, r=0, t=0, b=0)  # Tight layout with no extra margins
        )

        # Combine the trace and layout into a figure
        fig = go.Figure(data=[], layout=map_layout)

        for i in range(len(df) - 1):
            fig.add_trace(
                go.Scattermapbox(
                    lat=[df['latitude'][i], df['latitude'][i+1]],
                    lon=[df['longitude'][i], df['longitude'][i+1]],
                    mode='lines',
                    line=dict(width=4, color=df['colors'][i]),
                    name=f"Path_{i}"
                )
            )

        # Calculate map height and width in meters
        # This is the Haversine formula
        # https://en.wikipedia.org/wiki/Haversine_formula
        # Don't really understand *how* this works, just that it does
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371000
            phi1 = np.radians(lat1)
            phi2 = np.radians(lat2)
            delta_phi = np.radians(lat2 - lat1)
            delta_lambda = np.radians(lon2 - lon1)

            a = np.sin(delta_phi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

            meters = R * c
            return meters
        
        # calculate map height and width in meters
        width = haversine(min_lat, min_lon, min_lat, max_lon)
        height = haversine(min_lat, min_lon, max_lat, min_lon)
        ratio = width / height

        imageWidth = outputWidth # fixed width
        imageHeight = int(imageWidth / ratio) # scales height based on width and map ratio

        # Save as an image

        if filename == None:
            filename = self.getId()

        # make sure output directory exists
        if not os.path.exists("./maps"):
            os.makedirs("./maps")

        fig.write_image(f"./maps/{filename}_{lineColor}.jpg", height=imageHeight, width=imageWidth)  # Save the figure as a PNG

class LocationPoint:
    time = None
    speed = None
    altitude = None
    latitude = None
    longitude = None
    position = None # tuple of latitude and longitude
    verticalAccuracy = None
    horizontalAccuracy = None
    speedAccuracy = None

class VehiclePoint:
    time = None
    esc = None
    acceleration = None
    batteryPct = None
    speed = None
    distanceTraveledInMeters = None

    # battery
    whTotal = None
    whChargeTotal = None
    whRecharged = None
    whConsumed = None
    whNet = None
    voltage = None

    rpm = None
    inputCurrent = None
    motorCurrent = None

class RidePoint:
    __time = None
    __LocationPoint = None # source LocationPoint object
    __VehiclePoint = None # source VehicleDataPoint object

    # data from LocationPoint
    lp_speed = None
    lp_altitude = None
    lp_latitude = None
    lp_longitude = None
    lp_position = None # tuple of latitude and longitude
    lp_verticalAccuracy = None
    lp_horizontalAccuracy = None
    lp_speedAccuracy = None

    # data from VehicleDataPoint
    vp_esc = None
    vp_acceleration = None
    vp_batteryPct = None
    vp_speed = None
    vp_distanceTraveledInMeters = None

    vp_whTotal = None
    vp_whChargeTotal = None
    vp_whRecharged = None
    vp_whConsumed = None
    vp_whNet = None
    vp_voltage = None

    vp_rpm = None
    vp_inputCurrent = None
    vp_motorCurrent = None

    # combined data
    speed = None
    acceleration = None
    batteryPct = None
    distance = None


    def setLocationPoint(self, locationPoint: LocationPoint):
        self.__LocationPoint = locationPoint

    def setVehiclePoint(self, vehicleDataPoint: VehiclePoint):
        self.__VehicleDataPoint = vehicleDataPoint

    def getLocationPoint(self):
        return self.__LocationPoint
    
    def getVehicleDataPoint(self):
        return self.__VehicleDataPoint