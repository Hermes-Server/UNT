####################################################################
## File:                                                          ##
##     processData.py                                             ##
## Purpose:                                                       ##
##     Handle validation and database requests                    ##
## Author:                                                        ##
##     Ravichandran Subramanian                                   ##
## Versions:                                                      ##
##     Version      Comment                 Changed by   Date     ##
##     1.0.0        Initial                 Ravi Sub     20220504 ##
##     1.0.1        Minor fixes             Ravi Sub     20220602 ##
##              Initialize constraintID to zero length string     ##
##              Check for string length before testing last       ##
##                  in uss_base_url                               ##
##     1.0.2        Minor fixes             Ravi Sub     20220602 ##
##              Made subscriptons optional in constraints         ##
##     1.0.3        Minor fixes             Ravi Sub     20220602 ##
##              Fixed bug                                         ##
## Copyright:                                                     ##
##     (c) Hermes Autonomous Air Mobility 2022                    ##
####################################################################
""" Validate JSON contents and perform database operations """
# Process subscription
# RaviS What is the meaning of subscriptions when operational_intent or constraint is not present?
# RaviS Why are subscriptions not part of GET?
# RaviS Does OperationalIntent in winded response get a new version/ovn?
import json
import re
from connections import mysql
import numbers
import base64

# Property types
PropertyTypes = {
    "TOP_OF_CLIMB",
    "TOP_OF_DESCENT",
    "CROSSOVER_ALTITUDE",
    "TRANSITION_ALTITUDE_OR_LEVEL",
    "TCP_VERTICAL",
    "TCP_SPEED",
    "TCP_LATERAL",
    "DEPARTURE_RUNWAY_END",
    "START_TAKEOFF_ROLL",
    "END_LANDING_ROLL",
    "WHEELS_OFF",
    "WHEELS_ON",
    "ENTRY_RESTRICTED_OR_RESERVED_AIRSPACE",
    "EXIT_RESTRICTED_OR_RESERVED_AIRSPACE",
    "CROSSING_CONSTRAINED_AIRSPACE",
    "EXIT_CONSTRAINED_AIRSPACE",
    "INITIAL_PREDICTION_POINT",
    "END_PREDICTION_POINT",
    "HOLD_ENTRY",
    "HOLD_EXIT",
    "BEGIN_STAY",
    "END_STAY",
    "START_EXPECT_VECTORS",
    "END_EXPECT_VECTORS",
    "CONSTRAINT_POINT",
    "FIR_BOUBDARY_CROSSING_POINT",
    "RUNWAY_THRESHOLD",
    "PRESCRIBED_EET_POINT",
    "ENTRY_CONSTRAINED_AIRSPACE",
    "AIRPORT_REFERENCE_LOCATION",
    "WAYPOINT",
    }

# Point types
PointTypes = {
    "Vertiport",
    "Track",
    "Navigational",
    "Final",
    "Transition",
    "Non_ASDS",
    }

# Speed types
SpeedTypes = {
    "Vertiport",
    "Enroute",
    "Final",
    "Transition",
    "Non_ASDS",
    }

# Match for valid UUID format
def checkUUID(string):
    match = re.search(
        "^[0-9a-fA-F]{8}\\-"
        "[0-9a-fA-F]{4}\\-"
        "4[0-9a-fA-F]{3}\\-"
        "[8-b][0-9a-fA-F]{3}\\-[0-9a-fA-F]{12}$",
        string
    )
    return match
# End - def checkUUID(string):

# Match for valid RFC3339 datetime format
def checkDateTime(string):
    match = re.search(
        "^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d*)?Z", string
    )
    return match
# End - def checkDateTime(string):


class processData(object):
    HA_Values = {
        "HAUnknown",
        "HA10NMPlus",
        "HA10NM",
        "HA4NM",
        "HA2NM",
        "HA1NM",
        "HA05NM",
        "HA03NM",
        "HA01NM",
        "HA005NM",
        "HA30m",
        "HA10m",
        "HA3m",
        "HA1m",
    }
    VA_Values = {
        "VAUnknown",
        "VA150mPlus",
        "VA150m",
        "VA45m",
        "VA25m",
        "VA10m",
        "VA3m",
        "VA1m",
    }

    def __init__(self):
        self.connection = mysql.connect()
        self.cursor = self.connection.cursor()
    # End - def __init__(self):

    # Check OperationalIntent Reference
    def checkOperationalIntentReference(self, reference):
        invalid = ""
        if "id" in reference.keys():
            id = reference["id"]
            if not checkUUID(id):
                invalid += "id format is invalid, "
            # End - if not checkUUID(id):
        else:
            invalid += "id key not found, "
        # End - if "id" in reference.keys():
        if "manager" in reference.keys():
            manager = reference["manager"]
        else:
            invalid += "reference.manager key not found, "
        # End - if "manager" in reference.keys():
        if "uss_availability" in reference.keys():
            uss_availability = reference["uss_availability"]
            if not uss_availability in {"Unknown", "Normal", "Down"}:
                invalid += "reference.uss_availability is invalid, "
            # End - if not uss_availability in {"Unknown", "Normal", "Down"}:
        else:
            invalid += "reference.uss_availability key not found, "
        #End - if "uss_availability" in reference.keys():
        if "version" in reference.keys():
            version = reference["version"]
            if not isinstance(version, int):
                invalid += "reference.version must be integer, "
            # End - if not isinstance(version, int):
        else:
            invalid += "reference.version key not found, "
        # End - if "version" in reference.keys():
        if "state" in reference.keys():
            state = reference["state"]
            if not state in { "Accepted", "Activated", "Nonconforming", "Contingent"}:
                invalid += "reference.state is invalid, "
            # End - if not state in { "Accepted", "Activated", "Nonconforming", "Contingent"}:
        else:
            invalid += "reference.state key not found, "
        # End - if "state" in reference.keys():
        ovn = ""  # Optional
        if "ovn" in reference.keys():
            ovn = reference["ovn"]
            if (len(ovn) < 16) or (len(ovn) > 128):
                invalid += "reference.ovn incorrect length, "
            # End - if (len(ovn) < 16) or (len(ovn) > 128):
        # End - if "ovn" in reference.keys():
        if "time_start" in reference.keys():
            time_start = reference["time_start"]
            if "format" in time_start.keys():
                time_start_format = time_start["format"]
                if not time_start_format == "RFC3339":
                    invalid += "reference.time_start.format wrong, "
                # End - if not time_start_format == "RFC3339":
            else:
                invalid += "reference.time_start.format key not found, "
            # End - if "format" in time_start.keys():
            if "value" in time_start.keys():
                time_start_value = time_start["value"]
                if not checkDateTime(time_start_value):
                    invalid += "reference.time_start.value is invalid, "
                # End - if not checkDateTime(time_start_value):
            else:
                invalid += "reference.time_start.value key not found, "
            # End - if "value" in time_end.keys():
        else:
            invalid += "reference.time_start key not found, "
        # End - if "time_start" in reference.keys():
        if "time_end" in reference.keys():
            time_end = reference["time_end"]
            if "format" in time_end.keys():
                time_end_format = time_end["format"]
                if not time_end_format == "RFC3339":
                    invalid += "reference.time_end.format wrong, "
                # End - if not time_end_format == "RFC3339":
            else:
                invalid += "reference.tine_end.format key not found, "
            # End - if "format" in time_end.keys():
            if "value" in time_end.keys():
                time_end_value = time_end["value"]
                if not checkDateTime(time_end_value):
                    invalid += "reference.time_end.value is invalid, "
                # End - if not checkDateTime(time_end_value):
            else:
                invalid += "reference.time_end.value key not found, "
            # End - if "value" in time_end.keys():
        else:
            invalid += "reference.time_end key not found, "
        # End - if "time_end" in reference.keys():
        if "uss_base_url" in reference.keys():
            uss_base_url = reference["uss_base_url"]
            if len(uss_base_url) > 0:
                if uss_base_url[len(uss_base_url) - 1] == "/":
                    invalid += "reference.uss_base_url has trailing /, "
                # End - if uss_base_url[len(uss_base_url) - 1] == "/":
            # End - if len(uss_base_url) > 0:
        else:
            invalid += "reference.uss_base_url key not found, "
        # End - if "uss_base_url" in reference.keys():
        if "subscription_id" in reference.keys():
            subscription_id = reference["subscription_id"]
            if not checkUUID(subscription_id):
                invalid += "reference.subscription_id format is invalid, "
            # End - if not checkUUID(subscription_id):
        else:
            invalid += "reference.subscription_id key not found, "
        # End - if "subscription_id" in reference.keys():

        referenceData = {}
        # If Reference has no errors, return fields in a dictionary
        if invalid == "":
            referenceData = {
                "id": id,
                "manager": manager,
                "uss_availability": uss_availability,
                "version": version,
                "state": state,
                "ovn": ovn,
                "time_start_value": time_start_value,
                "time_start_format": time_start_format,
                "time_end_value": time_end_value,
                "time_end_format": time_end_format,
                "uss_base_url": uss_base_url,
                "subscription_id": subscription_id,
            }
        # End - if invalid == "":

        result = {"invalid": invalid, "referenceData": referenceData}
        return result
    # End - def checkOperationalIntentReference(self, reference):

    # Check Constraint Reference
    def checkConstraintReference(self, reference):
        invalid = ""
        if "id" in reference.keys():
            id = reference["id"]
            if not checkUUID(id):
                invalid += "id format is invalid, "
            # End - if not checkUUID(id):
        else:
            invalid += "id key not found, "
        # End - if "id" in reference.keys():
        if "manager" in reference.keys():
            manager = reference["manager"]
        else:
            invalid += "reference.manager key not found, "
        # End - if "manager" in reference.keys():
        if "uss_availability" in reference.keys():
            uss_availability = reference["uss_availability"]
            if not uss_availability in {"Unknown", "Normal", "Down"}:
                invalid += "reference.uss_availability is invalid, "
            # End - if not uss_availability in {"Unknown", "Normal", "Down"}:
        else:
            invalid += "reference.uss_availability key not found, "
        # End - if "uss_availability" in reference.keys():
        if "version" in reference.keys():
            version = reference["version"]
            if not isinstance(version, int):
                invalid += "reference.version must be integer, "
            # End - if not isinstance(version, int):
        else:
            invalid += "reference.version key not found, "
        # End - if "version" in reference.keys():
        ovn = ""  # Optional
        if "ovn" in reference.keys():
            ovn = reference["ovn"]
            if (len(ovn) < 16) or (len(ovn) > 128):
                invalid += "reference.ovn incorrect length, "
            # End - if (len(ovn) < 16) or (len(ovn) > 128):
        # End - if "ovn" in reference.keys():
        if "time_start" in reference.keys():
            time_start = reference["time_start"]
            if "format" in time_start.keys():
                time_start_format = time_start["format"]
                if not time_start_format == "RFC3339":
                    invalid += "reference.time_start.format wrong, "
                # End - if not time_start_format == "RFC3339":
            else:
                invalid += "reference.time_start.format key not found, "
            # End - if "format" in time_start.keys():
            if "value" in time_start.keys():
                time_start_value = time_start["value"]
                if not checkDateTime(time_start_value):
                    invalid += "reference.time_start.value is invalid, "
                # End - if not checkDateTime(time_start_value):
            else:
                invalid += "reference.time_start.value key not found, "
            # End - if "value" in time_start.keys():
        else:
            invalid += "reference.time_start key not found, "
        # End - if "time_start" in reference.keys():
        if "time_end" in reference.keys():
            time_end = reference["time_end"]
            if "format" in time_end.keys():
                time_end_format = time_end["format"]
                if not time_end_format == "RFC3339":
                    invalid += "reference.time_end.format wrong, "
                # End - if not time_end_format == "RFC3339":
            else:
                invalid += "reference.tine_end.format key not found, "
            # End - if "format" in time_end.keys():
            if "value" in time_end.keys():
                time_end_value = time_end["value"]
                if not checkDateTime(time_end_value):
                    invalid += "reference.time_end.value is invalid, "
                # End - if not checkDateTime(time_end_value):
            else:
                invalid += "reference.time_end.value key not found, "
            # End - if "value" in time_end.keys():
        else:
            invalid += "reference.time_end key not found, "
        # End - if "time_end" in reference.keys():
        if "uss_base_url" in reference.keys():
            uss_base_url = reference["uss_base_url"]
            if len(uss_base_url) > 0:
                if uss_base_url[len(uss_base_url) - 1] == "/":
                    invalid += "reference.uss_base_url has trailing /, "
                # End - if uss_base_url[len(uss_base_url) - 1] == "/":
            # End - if len(uss_base_url) > 0:
        else:
            invalid += "reference.uss_base_url key not found, "
        # End - if "uss_base_url" in reference.keys():

        referenceData = {}
        # If Reference has no errors, return fields in a dictionary
        if invalid == "":
            referenceData = {
                "id": id,
                "manager": manager,
                "uss_availability": uss_availability,
                "version": version,
                "ovn": ovn,
                "time_start_value": time_start_value,
                "time_start_format": time_start_format,
                "time_end_value": time_end_value,
                "time_end_format": time_end_format,
                "uss_base_url": uss_base_url,
            }
        # End - if invalid == "":

        result = {"invalid": invalid, "referenceData": referenceData}
        return result
    # End - def checkConstraintReference(self, reference):

    # Check Trajectory
    def checkTrajectory(self, trajectory):
        invalid = ""
        trajectoryData = []
        npoints = len(trajectory)
        if (npoints < 2) or (npoints > 1000):
            invalid += "trajectory must contain 2 to 1000 points, "
        else:
            point_count = 0
            npoints = len(trajectory)
            for TrajectoryPoint4D in trajectory:
                point_designator = ""  # Optional
                if "point_designator" in TrajectoryPoint4D.keys():
                    point_designator = TrajectoryPoint4D["point_designator"]
                # End - if "point_designator" in TrajectoryPoint4D.keys():
                if "lat_lng_point" in TrajectoryPoint4D.keys():
                    lat_lng_point = TrajectoryPoint4D["lat_lng_point"]
                    if "lat" in lat_lng_point.keys():
                        lat = lat_lng_point["lat"]
                        if isinstance(lat, numbers.Number):
                            if (lat < -90) or (lat > 90):
                                invalid += "trajectory.lat_lng_point.lat out of range, "
                            # End - if (lat < -90) or (lat > 90):
                        else:
                            invalid += "trajectory.lat_lng_point.lat must be numeric, "
                        # End - if isinstance(lat, numbers.Number):
                    else:
                        invalid += "trajectory.lat_lng_point.lat key not found, "
                    # End - if "lat" in lat_lng_point.keys():
                    if "lng" in lat_lng_point.keys():
                        lng = lat_lng_point["lng"]
                        if isinstance(lng, numbers.Number):
                            if (lng < -180) or (lng > 180):
                                invalid += "trajectory.lat_lng_point.lng out of range, "
                            # End - if (lng < -180) or (lng > 180):
                        else:
                            invalid += "trajectory.lat_lng_point.lng must be numeric, "
                        # End - if isinstance(lng, numbers.Number):
                    else:
                        invalid += "trajectory.lat_lng_point.lng key not found, "
                    # End - if "lng" in lat_lng_point.keys():
                else:
                    invalid += "lat_lng_point key not found, "
                # End - if "lat_lng_point" in TrajectoryPoint4D.keys():
                if "altitude" in TrajectoryPoint4D.keys():
                    altitude = TrajectoryPoint4D["altitude"]
                    if "value" in altitude.keys():
                        altitude_value = altitude["value"]
                        if isinstance(altitude_value, numbers.Number):
                            if (altitude_value < -8000) or (altitude_value > 100000):
                                invalid += "trajectory.altitude.value out of range, "
                            # End - if (altitude_value < -8000) or (altitude_value > 100000):
                        else:
                            invalid += "trajectory.altitude.value must be numeric, "
                        # End - if isinstance(altitude_value, numbers.Number):
                    else:
                        invalid += "trajectory.altitude.value key not found, "
                    # End - if "value" in altitude.keys():
                    if "reference" in altitude.keys():
                        altitude_reference = altitude["reference"]
                        if not altitude_reference == "W84":
                            invalid += "trajectory.altitude.reference invalid, "
                        # End - if not altitude_reference == "W84":
                    else:
                        invalid += "trajectory.altitude.reference key not found, "
                    # End - if "reference" in altitude.keys():
                    if "units" in altitude.keys():
                        altitude_units = altitude["units"]
                        if not altitude_units == "M":
                            invalid += "trajectory.altitude.units invalid, "
                        # End - if not altitude_units == "M":
                    else:
                        invalid += "trajectory.altitude.units key not found, "
                    # End - if "units" in altitude.keys():
                else:
                    invalid += "trajectory.altitude key not found, "
                # End - if "altitude" in TrajectoryPoint4D.keys():
                if "time" in TrajectoryPoint4D.keys():
                    time = TrajectoryPoint4D["time"]
                    if "format" in time.keys():
                        time_format = time["format"]
                        if not time_format == "RFC3339":
                            invalid += "trajectory.time.format wrong, "
                        # End - if not time_format == "RFC3339":
                    else:
                        invalid += "trajectory.time.format key not found, "
                    # End - if "format" in time.keys():
                    if "value" in time.keys():
                        time_value = time["value"]
                        if not checkDateTime(time_value):
                            invalid += "trajectory.time.value invalid, "
                        # End - if not checkDateTime(time_value):
                    else:
                        invalid += "trajectory.time.value key not found, "
                    # End - if "value" in time.keys():
                else:
                    invalid += "trajectory.time key not found, "
                # End - if "time" in TrajectoryPoint4D.keys():
                if "speed" in TrajectoryPoint4D.keys():
                    velocity = TrajectoryPoint4D["speed"]
                    if "speed" in velocity.keys():
                        speed = velocity["speed"]
                        if not isinstance(speed, numbers.Number):
                            invalid += "trajectory.speed.speed must be numeric, "
                        # End - if not isinstance(speed, numbers.Number):
                    else:
                        invalid += "trajectory.speed.speed key not found, "
                    # End - if "speed" in velocity.keys():
                    if "units_speed" in velocity.keys():
                        units_speed = velocity["units_speed"]
                        if not units_speed in {"MetersPerSecond", "Knots"}:
                            invalid += "trajectory.speed.units_speed invalid, "
                        # End - if not units_speed in {"MetersPerSecond", "Knots"}:
                    else:
                        invalid += "trajectory.speed.units_speed key not found, "
                    # End - if "units_speed" in velocity.keys():
                    track = 0  # Optional
                    if "track" in velocity.keys():
                        track = velocity["track"]
                        if isinstance(track, numbers.Number):
                            if (track < 0) or (track > 360):
                                invalid += "trajectory.speed.track out of range, "
                            # End - if (track < 0) or (track > 360):
                        else:
                            invalid += "trajectory.speed.track must be numeric, "
                        # End - if isinstance(track, numbers.Number):
                    # End - if "track" in velocity.keys():
                    speed_type = "GROUND"  # Optional
                    if "speed_type" in velocity.keys():
                        speed_type = velocity["speed_type"]
                        if not speed_type in {"GROUND", "AIR"}:
                            invalid += "trajectory.speed.speed_type invalid, "
                        # End - if not speed_type in {"GROUND", "AIR"}:
                    # End - if "speed_type" in velocity.keys():
                else:
                    invalid += "trajectory.speed key not found, "
                # End - if "speed" in TrajectoryPoint4D.keys():
                if "trajectory_property_array" in TrajectoryPoint4D.keys():
                    trajectory_property_array = TrajectoryPoint4D[
                        "trajectory_property_array"
                    ]
                    nprops = len(trajectory_property_array)
                    if (nprops < 1) or (nprops > 4):
                        invalid += "trajectory.trajectory_property_array x must contain 1 to 4 properties, "
                    else:
                        properties = []
                        found_airport_reference_location = False
                        found_wheels_off = False
                        found_wheels_on = False
                        for TrajectoryProperty in trajectory_property_array:
                            if("property_type" in TrajectoryProperty.keys()):
                                property_type = TrajectoryProperty["property_type"]
                                if property_type == "AIRPORT_REFERENCE_LOCATION":
                                    found_airport_reference_location = True
                                # End - if property_type == "AIRPORT_REFERENCE_LOCATION":
                                if property_type == "WHEELS_OFF":
                                    found_wheels_off = True
                                # End - if property_type == "WHEELS_OFF":
                                if property_type == "WHEELS_ON":
                                    found_wheels_on = True
                                # End - if property_type == "WHEELS_ON":
                                if (property_type in PropertyTypes):
                                    properties.append(property_type)
                                else:
                                    invalid += "trajectory.trajectory_property_array.property_type invalid, "
                                # End - if (property_type in PropertyTypes):
                            else:
                                invalid += "trajectory.trajectory_property_array.property_type key not found, "
                            # End - if("property_type" in TrajectoryProperty.keys()):
                        # End - for TrajectoryProperty in trajectory_property_array:
                        if point_count == 0:
                            if not (found_airport_reference_location and found_wheels_off):
                                invalid += "trajectory.trajectory_property_array.property_type first point does not have airport_reference_location and wheels_off, " 
                            # End - if not (found_airport_reference_location and found_wheels_off):
                        # End - if point_count == 0:
                        if point_count == npoints - 1:
                            if not (found_airport_reference_location and found_wheels_on):
                                invalid += "trajectory.trajectory_property_array.property_type last point does not have airport_reference_location and wheels_on, " 
                            # End - if not (found_airport_reference_location and found_wheels_off):
                        # End - if point_count == npoints - 1:
                    # End - if (nprops < 1) or (nprops > 4):
                else:
                    invalid += "trajectory.trajectory_property_array key not found, "
                # End - if "trajectory_property_array" in TrajectoryPoint4D.keys():

                # If Trajectory has no errors, return fields in a dictionary
                if invalid == "":
                    trajectory_item = {
                        "point_designator": point_designator,
                        "lat": lat,
                        "lng": lng,
                        "altitude_value": altitude_value,
                        "altitude_reference": altitude_reference,
                        "altitude_units": altitude_units,
                        "time_format": time_format,
                        "time_value": time_value,
                        "speed": speed,
                        "units_speed": units_speed,
                        "track": track,
                        "speed_type": speed_type,
                        "properties": properties,
                    }
                    trajectoryData.append(trajectory_item)
                # End - if invalid == "":
                point_count += 1
            # End - for TrajectoryPoint4D in trajectory:
        # End - if (npoints < 2) or (npoints > 1000):
        result = {"invalid": invalid, "trajectoryData": trajectoryData}
        return result
    # End - def checkTrajectory(self, trajectory):

    # Check OperationalIntentDetails
    def checkOperationalIntentDetails(self, details):
        invalid = ""
        aircraft_registration = ""  # Optional
        if "aircraft_registration" in details.keys():
            aircraft_registration = details["aircraft_registration"]
            found = re.search("^[A-Z0-9]{1,7}$", aircraft_registration)
            if not found:
                invalid += "operational_intent.details.aircraft_registration invalid format, "
            # End - if not found:
        # End - if "aircraft_registration" in details.keys():
        operator_name = ""  # Optional
        if "operator_name" in details.keys():
            operator_name = details["operator_name"]
            found = re.search("^[A-Z]{3}$", operator_name)
            if not found:
                invalid += "operational_intent.details.operator_name invalid format, "
            # End - if not found:
        # End - if "operator_name" in details.keys():
        if "trajectory" in details.keys():
            trajectory = details["trajectory"]
            trajectoryResult = self.checkTrajectory(trajectory)
            invalid += trajectoryResult["invalid"]
        else:
            invalid += "operational_intent.details.trajectory key not found, "
        # End - if "trajectory" in details.keys():

        detailsData = {}
        # If Details has no errors, return fields in a dictionary
        if invalid == "":
            detailsData = {
                "aircraft_registration": aircraft_registration,
                "operator_name": operator_name,
                "trajectory": trajectoryResult["trajectoryData"],
            }
        # End - if invalid == "":

        result = {"invalid": invalid, "detailsData": detailsData}
        return result
    # End - def checkOperationalIntentDetails(self, details):

    # POST OperationalIntent
    def postOperationalIntent(self, struct):
        invalid = ""
        if "operational_intent_id" in struct.keys():
            operationalIntentID = struct["operational_intent_id"]
            if not checkUUID(operationalIntentID):
                invalid += "operational_intent_id format is invalid, "
            # End - if not checkUUID(operationalIntentID):
        else:
            invalid += "operational_intent_id key not found, "
        # End - if "operational_intent_id" in struct.keys():
        if "operational_intent" in struct.keys():
            operationalIntent = struct["operational_intent"]
            if "reference" in operationalIntent.keys():
                reference = operationalIntent["reference"]
                referenceResult = self.checkOperationalIntentReference(reference)
                invalid += referenceResult["invalid"]

                if "id" in referenceResult["referenceData"]:
                    if not (referenceResult['referenceData']['id'] == operationalIntentID):
                        invalid += "Reference.id does not match operational_intent_id, "
                    # End - if not (referenceResult["id"] == operationalIntentID):
                else:
                    invalid += "Reference.id does not match operational_intent_id, "
                # End - if "id" in referenceResult["referenceData"]:
            else:
                invalid += "operational_intent.reference key not found, "
            # End - if "reference" in operationalIntent.keys():
            if "details" in operationalIntent.keys():
                details = operationalIntent["details"]
                detailsResult = self.checkOperationalIntentDetails(details)
                invalid += detailsResult["invalid"]
            else:
                invalid += "operational_intent.details key not found, "
            # End - if "details" in operationalIntent.keys():
        else:
            # Remove Operational Intent
            # Get Reference information for highest version number
            sqlQuery = ("SELECT "
                        "operationalIntentID, "
                        "active "
                        "FROM OperationalIntentReference WHERE operationalIntentID = %s")
            bindData = operationalIntentID
            self.cursor.execute(sqlQuery, bindData)
            records = self.cursor.fetchall()
            if len(records) > 0:
                oi_active = records[0][1]
                if not oi_active:
                    invalid += "Operational intent is not active, "
                    status = 404
                else:
                    sqlQuery = ("UPDATE OperationalIntentReference "
                                "SET active = 0 "
                                "WHERE operationalIntentID = %s")
                    bindData = operationalIntentID
                    self.cursor.execute(sqlQuery, bindData)
                    records = self.cursor.fetchall()
                    self.connection.commit()
                    status = 204
                # End - if not oi_active:
            else:
                invalid += "Invalid operational intent, "
                status = 404
            # End - if len(records) > 0:
            result = {"status": status, "invalid": invalid}
            print("Invalid: " + str(invalid), flush = True)
            return result
        # End - if "operational_intent" in struct.keys():

        if "subscriptions" in struct.keys():
            subscriptions = struct["subscriptions"]
            subscription_ids = []
            notification_indices = []
            if len(subscriptions) == 0:
                invalid += "There are no subscriptions, "
            # End - if len(subscriptions) == 0:
            for subscription in subscriptions:
                if "subscription_id" in subscription.keys():
                    subscription_id = subscription["subscription_id"]
                    if not checkUUID(subscription_id):
                        invalid += "subscriptions.subscription_id is invalid, "
                    else:
                        subscription_ids.append(subscription_id)
                    # End - if not checkUUID(subscription_id):
                else:
                    invalid += "subscriptions.subscription_id key not found, "
                # End - if "subscription_id" in subscription.keys():
                if "notification_index" in subscription.keys():
                    notification_index = subscription["notification_index"]
                    if not isinstance(notification_index, int):
                        invalid += "subscriptions.notification_index is invalid, "
                    else:
                        notification_indices.append(notification_index)
                    # End - if not isinstance(notification_index, int):
                else:
                    invalid += "subscriptions.notification_index key not found, "
                # End - if "notification_index" in subscription.keys():
            # End - for subscription in subscriptions:
        else:
            invalid += "subscriptions key not found, "
        # End - if "subscriptions" in struct.keys():

        # Get version information for highest version number
        sqlQuery = ("SELECT "
                    "operationalIntentID, "
                    "version, "
                    "active "
                    "FROM OperationalIntentReference WHERE operationalIntentID = %s ORDER BY version DESC LIMIT 1")
        bindData = operationalIntentID
        self.cursor.execute(sqlQuery, bindData)
        records = self.cursor.fetchall()
        if len(records) > 0:
            oi_active = records[0][2]
            if not oi_active:
                invalid += "Operational intent is not active, "
            else:
                previous_version = records[0][1]
                if referenceResult['referenceData']['version'] < previous_version:
                    invalid += "Higher version exists, "
                # End - if referenceData["version"] < previous_version:
            # End - if not oi_active:
        # End - if len(records) > 0:

        status = 204  # Succeeded
        self.connection.autocommit = False
        if invalid == "":
            referenceData = referenceResult["referenceData"]
            detailsData = detailsResult["detailsData"]
            sqlQuery = ("INSERT INTO OperationalIntentReference ("
                       "operationalIntentID, "
                       "manager, "
                       "uss_availability, "
                       "version, "
                       "state, "
                       "ovn, "
                       "time_start_value, "
                       "time_start_format, "
                       "time_end_value, "
                       "time_end_format, "
                       "uss_base_url, "
                       "subscription_id, "
                       "aircraft_registration, "
                       "operator_name, "
                       "active"
                       ") VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            bindData = [
                operationalIntentID,
                referenceData["manager"],
                referenceData["uss_availability"],
                referenceData["version"],
                referenceData["state"],
                referenceData["ovn"],
                referenceData["time_start_value"],
                referenceData["time_start_format"],
                referenceData["time_end_value"],
                referenceData["time_end_format"],
                referenceData["uss_base_url"],
                referenceData["subscription_id"],
                detailsData["aircraft_registration"],
                detailsData["operator_name"],
                1
            ]
            try:
                self.cursor.execute(sqlQuery, bindData)
            except self.connection.IntegrityError as err:
                status = 409  # Duplicate entry
            # End - try:
        else:
            status = 400  # Parameter error
        # End - if invalid == "":

        # Insert AllOperationalIntentReference
        self.connection.autocommit = False
        if invalid == "":
            sqlQuery = ("INSERT INTO AllOperationalIntentReference ("
                       "operationalIntentID "
                       ") VALUES (%s)")
            bindData = [
                operationalIntentID
            ]
            try:
                self.cursor.execute(sqlQuery, bindData)
            except self.connection.IntegrityError as err:
                status = 409  # Duplicate entry
            # End - try:



        if status == 204: # Reference insert succeeded
            trajectoryData = detailsResult["detailsData"]["trajectory"]
            trajectoryPoint = 0 # Sequence number for Trajectory Points
            for trajectoryItem in trajectoryData:
                sqlQuery = ("INSERT INTO Trajectory ("
                            "operationalIntentID, "
                            "version, "
                            "pointID, "
                            "point_designator, "
                            "latitude, "
                            "longitude, "
                            "altitude_value, "
                            "altitude_reference, "
                            "altitude_units, "
                            "time_value, "
                            "time_format, "
                            "speed, "
                            "units_speed, "
                            "track, "
                            "speed_type, "
                            "properties"
                            ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                propertyString = ""
                for p in trajectoryItem["properties"]:
                    if not propertyString == "":
                        propertyString += ","
                    # End - if not propertyString == "":
                    propertyString += p
                # End - for p in trajectoryItem["properties"]:
                bindData = [
                    operationalIntentID,
                    referenceData["version"],
                    trajectoryPoint,
                    trajectoryItem["point_designator"],
                    trajectoryItem["lat"],
                    trajectoryItem["lng"],
                    trajectoryItem["altitude_value"],
                    trajectoryItem["altitude_reference"],
                    trajectoryItem["altitude_units"],
                    trajectoryItem["time_value"],
                    trajectoryItem["time_format"],
                    trajectoryItem["speed"],
                    trajectoryItem["units_speed"],
                    trajectoryItem["track"],
                    trajectoryItem["speed_type"],
                    propertyString,
                ]
                try:
                    self.cursor.execute(sqlQuery, bindData)
                except self.connection.IntegrityError as err:
                    status = 409  # Duplicate entry
                # End - try:
                trajectoryPoint += 1
            # End - for trajectoryItem in trajectoryData:
        # End - if status == 204: # Reference insert succeeded

        if status == 204: # Reference and Trajectory inserts succeeded
            for i in range(len(subscription_ids)):
                sqlQuery = ("INSERT INTO OperationalIntentSubscriptions ("
                           "operationalIntentID, "
                           "version, "
                           "subscription_id, "
                           "notification_index"
                           ") VALUES(%s, %s, %s, %s)")
                bindData = [
                    operationalIntentID,
                    referenceData["version"],
                    subscription_ids[i],
                    notification_indices[i]
                ]
                try:
                    self.cursor.execute(sqlQuery, bindData)
                except self.connection.IntegrityError as err:
                    status = 409  # Duplicate entry
                # End - try:
            # End - for i in range(len(subscription_ids)):
        # End - if status == 204: # Reference and Trajectory inserts succeeded

        if status == 204: # All inserts succeded, commit
            self.connection.commit()
        else: # Something went wrong, rollback
            self.connection.rollback()
        # End - if status == 204:
        self.connection.autocommit = True
        result = {"status": status, "invalid": invalid}
        print("Invalid: " + str(invalid), flush = True)
        return result
    # End - def postOperationalIntent(self, struct):

    # GET OperationalIntent
    def getOperationalIntent(self, entityID):
        invalid = ""
        if checkUUID(entityID):
            # Get Reference information for highest version number
            sqlQuery = ("SELECT "
                        "operationalIntentID, "
                        "manager, "
                        "uss_availability, "
                        "version, "
                        "state, "
                        "ovn, "
                        "time_start_value, "
                        "time_start_format, "
                        "time_end_value, "
                        "time_end_format, "
                        "uss_base_url, "
                        "subscription_id, "
                        "aircraft_registration, "
                        "operator_name, "
                        "active "
                        "FROM OperationalIntentReference WHERE operationalIntentID = %s ORDER BY version DESC LIMIT 1")
            bindData = entityID
            self.cursor.execute(sqlQuery, bindData)
            records = self.cursor.fetchall()
            if len(records) > 0:
                oi_active = records[0][14]
                if not oi_active:
                    invalid += "Operational intent is not active, "
                    result = {"status": 404}
                else:
                    reference = {
                        "id": records[0][0],
                        "manager": records[0][1],
                        "uss_availability": records[0][2],
                        "version": records[0][3],
                        "state": records[0][4],
                        "ovn": records[0][5],
                        "time_start": {"value": records[0][6], "format": records[0][7]},
                        "time_end": {"value": records[0][8], "format": records[0][9]},
                        "uss_base_url": records[0][10],
                        "subscription_id": records[0][11],
                    }
                    details = {
                        "aircraft_registration": records[0][12],
                        "operator_name": records[0][13],
                        "trajectory": "",
                    }
                    # If ovn is null, do not include
                    if records[0][5] == "":
                        del reference["ovn"]
                    # End - if records[0][5] == "":

                    # Get Trajectory information
                    sqlQuery = ("SELECT "
                                "point_designator, "
                                "latitude, "
                                "longitude, "
                                "altitude_value, "
                                "altitude_reference, "
                                "altitude_units, "
                                "time_value, "
                                "time_format, "
                                "speed, "
                                "units_speed, "
                                "speed_type, "
                                "track, "
                                "properties "
                                "FROM Trajectory WHERE operationalIntentID = %s and version = %s ORDER BY pointID")
                    bindData = [entityID, reference["version"]]
                    self.cursor.execute(sqlQuery, bindData)
                    records = self.cursor.fetchall()
                    point_list = []
                    for record in records:
                        property_list = []
                        properties = record[12].split(",")
                        for property in properties:
                            property_list.append({"property_type": property})
                        # End - for property in properties:
                        point = {
                            "point_designator": record[0],
                            "lat_lng_point": {"lng": record[2], "lat": record[1]},
                            "altitude": {
                                "value": record[3],
                                "reference": record[4],
                                "units": record[5],
                            },
                            "time": {"value": record[6], "format": record[7]},
                            "speed": {
                                "speed": record[8],
                                "units_speed": record[9],
                                "speed_type": record[10],
                            },
                            "track": record[11],
                            "trajectory_property_array": property_list,
                        }
                        # If track is 0, do not include
                        if record[11] == 0:
                            del point["track"]
                        point_list.append(point)
                    # End - for record in records:

                    trajectory = point_list
                    details["trajectory"] = trajectory

                    operational_intent = {
                        "operational_intent": {
                            "reference": reference,
                            "details": details,
                        }
                    }

                    result = {"operational_intent": operational_intent, "status": 200}
                # End - if not oi_active:
            else:
                result = {"status": 404}
            # End - if len(records) > 0:
        else:
            result = {"status": 400}
        # End - if checkUUID(entityID):
        print("Invalid: " + str(invalid), flush = True)
        return result
    # End - def getOperationalIntent(self, entityID):

    # POST Telemetry - Not based on any API, just included so we can perform GET
    def postTelemetry(self, struct):
        invalid = ""
        status = 200 # Success
        if "operational_intent_id" in struct.keys():
            operational_intent_id = struct["operational_intent_id"]
            if not checkUUID(operational_intent_id):
                invalid += "operational_intent_id invalid format, "
            # End - if not checkUUID(operational_intent_id):
        else:
            invalid += "operational_intent_id key not found, "
        # End - if "operational_intent_id" in struct.keys():

        if "telemetry" in struct.keys():
            telemetry = struct["telemetry"]
            if "time_measured" in telemetry.keys():
                time_measured = telemetry["time_measured"]
                if "format" in time_measured.keys():
                    time_measured_format = time_measured["format"]
                    if not time_measured_format == "RFC3339":
                        invalid += "telemetry.time_measured.format wrong, "
                    # End - if not time_measured_format == "RFC3339":
                else:
                    invalid += "telemetry.time_measured.format key not found, "
                # End - if "format" in time_measured.keys():
                if "value" in time_measured.keys():
                    time_measured_value = time_measured["value"]
                    if not checkDateTime(time_measured_value):
                        invalid += "telemetry.time_measured.value invalid, "
                    # End - if not checkDateTime(time_measured_value):
                else:
                    invalid += "telemetry.time_measured.value key not found, "
                # End - if "value" in time_measured.keys():
            else:
                invalid += "telemetry.time_measured key not found, "
            # End - if "time_measured" in telemetry.keys():

            if "position" in telemetry.keys():
                position = telemetry["position"]
                if "longitude" in position.keys():
                    longitude = position["longitude"]
                    if isinstance(longitude, numbers.Number):
                        if (longitude < -180.0) or (longitude > 180.0):
                            invalid += "telemetry.position.longitude out of range, "
                        # End - if (longitude < -180.0) or (longitude > 180.0):
                    else:
                        invalid += "telemetry.position.longitude must be numeric, "
                    # End - if isinstance(longitude, numbers.Number):
                else:
                    invalid += "telemetry.position.longitude key not found, "
                # End - if "longitude" in position.keys():

                if "latitude" in position.keys():
                    latitude = position["latitude"]
                    if isinstance(latitude, numbers.Number):
                        if (latitude < -90.0) or (latitude > 90.0):
                            invalid += "telemetry.position.latitude out of range, "
                        # End - if (latitude < -90.0) or (latitude > 90.0):
                    else:
                        invalid += "telemetry.position.latitude must be numeric, "
                    # End - if isinstance(latitude, numbers.Number):
                else:
                    invalid += "telemetry.position.latitude key not found, "
                # End - if "latitude" in position.keys():

                accuracy_h = ""
                accuracy_v = ""
                extrapolated = False
                if "extrapolated" in position.keys():
                    extrapolated = position["extrapolated"]
                # End - if "extrapolated" in position.keys():
                if "accuracy_h" in position.keys():
                    accuracy_h = position["accuracy_h"]
                    if not accuracy_h in self.HA_Values:
                        invalid += "telemetry.position.accuracy_h illegal value, "
                    # End - if not accuracy_h in self.HA_Values:
                elif extrapolated:
                    invalid = (
                        invalid + "telemetry.position.accuracy_h mandatory when extrapolated is true, "
                    )
                # End - if "accuracy_h" in position.keys():
                if "accuracy_v" in position.keys():
                    accuracy_v = position["accuracy_v"]
                    if not accuracy_v in self.VA_Values:
                        invalid += "telemetry.position.accuracy_v illegal value, "
                    # End - if not accuracy_v in self.VA_Values:
                elif extrapolated:
                    invalid = (
                        invalid + "telemetry.position.accuracy_v mandatory when extrapolated is true, "
                    )
                # End - if "accuracy_v" in position.keys():

                if "altitude" in position.keys():
                    altitude = position["altitude"]
                    if "value" in altitude.keys():
                        altitude_value = altitude["value"]
                        if isinstance(altitude_value, numbers.Number):
                            if (altitude_value < -8000.0) or (altitude_value > 100000.0):
                                invalid += "altitude value out of range, "
                            # End - if (altitude_value < -8000.0) or (altitude_value > 100000.0):
                        else:
                            invalid += "telemetry.position.altitude.value must be numeric, "
                        # End - if isinstance(longitude, numbers.Number):
                    else:
                        invalid += "telemetry.position.altitude.value key not found, "
                    # End - if "value" in altitude.keys():
                    if "reference" in altitude.keys():
                        altitude_reference = altitude["reference"]
                        if not altitude_reference == "W84":
                            invalid += "altitude_reference is invalid, "
                        # End - if not altitude_reference == "W84":
                    else:
                        invalid += invalid + "position.altitude.reference key not found, "
                    # End - if "reference" in altitude.keys():
                    if "units" in altitude.keys():
                        altitude_units = altitude["units"]
                        if not altitude_units == "M":
                            invalid += "altitude_units is invalid, "
                        # End - if not altitude_units == "M":
                    else:
                        invalid += "position.altitude.units key not found, "
                    # End - if "units" in altitude.keys():
                else:
                    invalid += "position.altitude key not found, "
                # End - if "altitude" in position.keys():
            else:
                invalid += "telemetry.position key not found, "
            # End - if "position" in telemetry.keys():

            if "velocity" in telemetry.keys():
                velocity = telemetry["velocity"]
                if "speed" in velocity.keys():
                    velocity_speed = velocity["speed"]
                    if not isinstance(velocity_speed, numbers.Number):
                        invalid += "telemetry.velocity.speed must be numeric, "
                    # End - if not isinstance(velocity_speed, numbers.Number):
                else:
                    invalid += "telemetry.velocity.speed key not found, "
                # End - if "speed" in velocity.keys():
                if "units_speed" in velocity.keys():
                    units_speed = velocity["units_speed"]
                    if not units_speed == "MetersPerSecond":
                        invalid += "telemetry.velocity.units_speed is invalid, "
                    # End - if not units_speed == "MetersPerSecond":
                else:
                    invalid += "telemetry.velocity.units_speed key not found, "
                # End - if "units_speed" in velocity.keys():
                track = 0
                if "track" in velocity.keys():  # Optional
                    track = velocity["track"]
                    if isinstance(track, numbers.Number):
                        if track < 0 or track > 360:
                            invalid += "telemetry.velocity.track is invalid, "
                        # End - if track < 0 or track > 360:
                    else:
                        invalid += "telemetry.velocity.track must be numeric, "
                    # End - if not isinstance(track, numbers.Number):
                # End - if "track" in velocity.keys():  # Optional
                if "speed_type" in velocity.keys():
                    speed_type = velocity["speed_type"]
                    if not ((speed_type == "AIR") or (speed_type == "GROUND")):
                        invalid += "telemetry.velocity.speed_type is invalid, "
                    # End - if not ((speed_type == "AIR") or (speed_type == "GROUND")):
                else:
                    invalid += "velocity.units_speed_type key not found, "
                # End - if "speed_type" in velocity.keys():
            else:
                invalid += "telemetry.velocity key not found, "
            # End - if "velocity" in telemetry.keys():
        else:
            invalid += "telemetry key not found, "
        # End - if "telemetry" in struct.keys():

        next_opportunity_format = ""
        next_opportunity_value = ""
        if "next_telemetry_opportunity" in struct.keys():  # Optional
            next_opportunity = struct["next_telemetry_opportunity"]
            if "format" in next_opportunity.keys():
                next_opportunity_format = next_opportunity["format"]
                if not next_opportunity_format == "RFC3339":
                    invalid += "telemetry.next_telemetry_opportunity.format wrong, "
                # End - if not next_opportunity_format == "RFC3339":
            else:
                invalid += "telemetry.next_telemetry_opportunity.format key not found, "
            # End - if "format" in next_opportunity.keys():
            if "value" in next_opportunity.keys():
                next_opportunity_value = next_opportunity["value"]
                if not checkDateTime(next_opportunity_value):
                    invalid += "telemetry.next_telemetry_opportunity.value is invalid, "
                # End - if not checkDateTime(next_opportunity_value):
            else:
                invalid += "telemetry.next_telemetry_opportunity.value key not found, "
            # End - if "value" in next_opportunity.keys():
        # End - if "next_telemetry_opportunity" in struct.keys():  # Optional

        if "aircraft_registration" in struct.keys(): 
            aircraft_registration = struct["aircraft_registration"]
        else:
            invalid += "aircraft_registration key not found, "

        status = 200  # Succeeded
        self.connection.autocommit = False
        if invalid == "":
            sqlQuery = ("INSERT INTO Telemetry ("
                        "operationalIntentID, "
                        "time_measured_value, "
                        "time_measured_format, "
                        "latitude, "
                        "longitude, "
                        "accuracy_h, "
                        "accuracy_v, "
                        "extrapolated, "
                        "altitude_value, "
                        "altitude_reference, "
                        "altitude_units, "
                        "speed, "
                        "units_speed, "
                        "track, "
                        "speed_type, "
                        "next_opportunity_value, "
                        "next_opportunity_format, "
                        "active, "
                        "aircraft_registration"
                        ") VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            bindData = [
                operational_intent_id,
                time_measured_value,
                time_measured_format,
                latitude,
                longitude,
                accuracy_h,
                accuracy_v,
                extrapolated,
                altitude_value,
                altitude_reference,
                altitude_units,
                velocity_speed,
                units_speed,
                track,
                speed_type,
                next_opportunity_value,
                next_opportunity_format,
                1,
                aircraft_registration
                
            ]
            try:
                self.cursor.execute(sqlQuery, bindData)
            except self.connection.IntegrityError as err:
                status = 409  # Duplicate entry
            # End - try:
            self.connection.autocommit = True
        else:
            status = 400  # Parameter error
        # End - if invalid == "":
        self.connection.autocommit = True

        if status == 200: # All inserts succeded, commit
            self.connection.commit()
        else: # Something went wrong, rollback
            self.connection.rollback()
        # End - if status == 200: # All inserts succeded, commit
        result = {"status": status, "invalid": invalid}
        print("Invalid: " + str(invalid), flush = True)
        return result
    # End - def postTelemetry(self, struct):

    # GET Telemetry
    def getTelemetry(self, entityID):
        if checkUUID(entityID):
            # Get Reference information
            sqlQuery = ("SELECT "
                        "operationalIntentID, "
                        "time_measured_value, "
                        "time_measured_format, "
                        "latitude, "
                        "longitude, "
                        "accuracy_h, "
                        "accuracy_v, "
                        "extrapolated, "
                        "altitude_value, "
                        "altitude_reference, "
                        "altitude_units, "
                        "speed, "
                        "units_speed, "
                        "track, "
                        "speed_type, "
                        "next_opportunity_value, "
                        "next_opportunity_format, "
                        "aircraft_registration, "
                        "active"
                        "FROM Telemetry WHERE operationalIntentID = %s ORDER BY time_measured_value DESC LIMIT 1")
            bindData = entityID
            self.cursor.execute(sqlQuery, bindData)
            records = self.cursor.fetchall()
            if len(records) > 0:
                record = records[0]
                time_measured = {"value": record[1], "format": record[2]}
                if record[7] == 0:
                    extrapolated = False
                else:
                    extrapolated = True
                # End - if record[7] == 0:
                position = {
                    "longitude": record[4],
                    "latitude": record[3],
                    "accuracy_h": record[5],
                    "accuracy_v": record[6],
                    "extrapolated": extrapolated,
                    "altitude": {
                        "value": record[8],
                        "reference": record[9],
                        "units": record[10],
                    },
                }
                if record[5] == "":
                    del position["accuracy_h"]
                # End - if record[5] == "":
                if record[6] == "":
                    del position["accuracy_v"]
                # End - if record[6] == "":

                velocity = {
                    "speed": record[11],
                    "units_speed": record[12],
                    "track": record[13],
                    "speed_type": record[14],
                }
                telemetry = {
                    "time_measured": time_measured,
                    "position": position,
                    "velocity": velocity,
                }
                next_opportunity = {"value": record[15], "format": record[16]}
                aircraft_registration = {"aircraft_registration":record[18]}
                tel = {
                    "operational_intent_id": entityID,
                    "telemetry": telemetry,
                    "next_telemetry_opportunity": next_opportunity,
                    "aircraft_registration": aircraft_registration,
                }
                result = {"tel": tel, "status": 200}
            else:
                result = {"status": 404} # Reference not found
            # End - if len(records) > 0:
        else:
            result = {"status": 404} # Malformed entityID
        # End - if checkUUID(entityID):
        return result
    # End - def getTelemetry(self, entityID):

    # POST Constraint
    def postConstraint(self, struct):
        invalid = ""
        status = 204  # Succeeded
        constraintID = ""
        if "constraint_id" in struct.keys():
            constraintID = struct["constraint_id"]
            if not checkUUID(constraintID):
                invalid += "constraint_id invalid format, "
        else:
            invalid += "constraint_id key not found, "
        # End - if "constraint_id" in struct.keys():

        if "constraint" in struct.keys():
            constraint = struct["constraint"]
            if "reference" in constraint.keys():
                constraint_reference = constraint["reference"]
                referenceResult = self.checkConstraintReference(constraint_reference)
                invalid += referenceResult["invalid"]
                if "id" in referenceResult["referenceData"]:
                    if not (referenceResult["referenceData"]["id"] == constraintID):
                        invalid += "Reference.id does not match constraint_id, "
                    # End - if not (referenceResult["referenceData"]["id"] == constraintID):
                else:
                    invalid += "Reference.id does not match constraint_id, "
                # End - if "id" in referenceResult["referenceData"]:
            else:
                invalid += "constraint.reference key not found"
            # End - if "reference" in constraint.keys():
            if "details" in constraint.keys():
                constraint_details = constraint["details"]
                if "volumes" in constraint_details.keys():
                    volumes_data = []
                    volumes = constraint_details["volumes"]
                    if len(volumes) == 0:
                        invalid += "There are no volumes, "
                    # End - if len(volumes) == 0:
                    for volume in volumes:
                        if "volume" in volume.keys():
                            volume_data = {}
                            found_circle = False
                            found_polygon = False
                            if "outline_circle" in volume["volume"].keys():
                                found_circle = True
                                volume_data["volume_type"] = "CIRCLE"
                                outline_circle = volume["volume"]["outline_circle"]
                                if "center" in outline_circle.keys():
                                    center = outline_circle["center"]
                                    if "lng" in center.keys():
                                        lng = center["lng"]
                                        if isinstance(lng, numbers.Number):
                                            if (lng < -180) or (lng > 180):
                                                invalid += "constraint.details.volumes.volume.outline_circle.center.lng out of range, "
                                            else:
                                                volume_data["center_longitude"] = lng
                                            # End - if (lng < -180) or (lng > 180):
                                        else:
                                            invalid += "constraint.details.volumes.volume.outline_circle.center.lng must be numeric, "
                                        # End - if isinstance(lng, numbers.Number):
                                    else:
                                        invalid += "constraint.details.volumes.volume.outline_circle.center.lng key not found, "
                                    # End - if "lng" in center.keys():
                                    if "lat" in center.keys():
                                        lat = center["lat"]
                                        if isinstance(lat, numbers.Number):
                                            if (lat < -90) or (lat > 90):
                                                invalid += "constraint.details.volumes.volume.outline_circle.center.lat out of range, "
                                            else:
                                                volume_data["center_latitude"] = lat
                                            # End - if (lat < -90) or (lat > 90):
                                        else:
                                            invalid += "constraint.details.volumes.volume.outline_circle.center.lat must be numeric, "
                                        # End - if isinstance(lat, numbers.Number):
                                    else:
                                        invalid += "constraint.details.volumes.volume.outline_circle.center.lat key not found, "
                                    # End - if "lat" in center.keys():
                                else:
                                    invalid += "constraint.details.volumes.volume.outline_circle.center key not found, "
                                # End - if "center" in outline_circle.keys():
                                if "radius" in outline_circle.keys():
                                    radius = outline_circle["radius"]
                                    if "value" in radius.keys():
                                        value = radius["value"]
                                        if isinstance(value, numbers.Number):
                                            if (value <= 0):
                                                invalid += "constraint.details.volume.outline_circle.radius.value must be positive, "
                                            else:
                                                volume_data["radius_value"] = value
                                            # End - if (value <= 0):
                                        else:
                                            invalid += "constraint.details.volumes.volume.outline_circle.radius.value must be numeric, "
                                        # End - if isinstance(value, numbers.Number):
                                    else:
                                        invalid += "constraint.details.volumes.volume.outline_circle.radius.value key not found, "
                                    # End - if "value" in radius.keys():
                                    if "units" in radius.keys():
                                        units = radius["units"]
                                        if units == "M":
                                            volume_data["radius_units"] = units
                                        else:
                                            invalid += "constraint.details.volume.outline_circle.radius.units invalid, "
                                        # End - if units == "M":
                                    else:
                                        invalid += "constraint.details.volumes.volume.outline_circle.radius.units key not found, "
                                    # End - if "units" in radius.keys():
                                else:
                                    invalid += "constraint.details.volumes.volume.outline_circle.radius key not found, "
                                # End - if "radius" in outline_circle.keys():
                            # End - if "outline_circle" in volume["volume"].keys():
                            if "outline_polygon" in volume["volume"].keys():
                                found_polygon = True
                                volume_data["volume_type"] = "POLYGON"
                                outline_polygon = volume["volume"]["outline_polygon"]
                                if "vertices" in outline_polygon.keys():
                                    vertices = outline_polygon["vertices"]
                                    lngs = [];
                                    lats = [];
                                    if not len(vertices) >= 3:
                                        invalid += "vertices must have at least 3 entries, "
                                    # End - if not len(vertices) >= 3:
                                    for vertex in vertices:
                                        if "lng" in vertex.keys():
                                            lng = vertex["lng"]
                                            if isinstance(lng, numbers.Number):
                                                if (lng < -180) or (lng > 180):
                                                    invalid += "constraint.details.volumes.volume.outline_polygon.vertices.lng out of range, "
                                                else:
                                                    lngs.append(lng)
                                                # End - if (lng < -180) or (lng > 180):
                                            else:
                                                invalid += "constraint.details.volumes.volume.outline_polygon.vertices.lng must be numeric, "
                                            # End - if isinstance(lng, numbers.Number):
                                        else:
                                            invalid += "constraint.details.volumes.volume.outline_polygon.vertices.lng key not found, "
                                        # End - if "lng" in vertex.keys():
                                        if "lat" in vertex.keys():
                                            lat = vertex["lat"]
                                            if isinstance(lat, numbers.Number):
                                                if (lat < -90) or (lat > 90):
                                                    invalid += "constraint.details.volumes.volume.outline_polygon.vertices.lat out of range, "
                                                else:
                                                    lats.append(lat)
                                                # End - if (lat < -90) or (lat > 90):
                                            else:
                                                invalid += "constraint.details.volumes.volume.outline_polygon.vertices.lat must be numeric, "
                                            # End - if isinstance(lnststg, numbers.Number):
                                        else:
                                            invalid += "constraint.details.volumes.volume.outline_polygon.vertices.lat key not found, "
                                        # End - if "lat" in vertex.keys():
                                    # End - for vertex in vertices:
                                else:
                                    invalid += "constraint.details.volumes.volume.outline_polygon.vertices key not found, "
                                # End - if "vertices" in outline_polygon.keys():
                                volume_data["polygon_lngs"] = lngs
                                volume_data["polygon_lats"] = lats
                            # End - if "outline_polygon" in volume["volume"].keys():
                            if found_circle and found_polygon:
                                invalid += "both outline_circle and outline_polygon specified, "
                            # End - if found_circle and found_polygon:
                            if not (found_circle or found_polygon):
                                invalid += "neither outline_circle and outline_polygon specified, "
                            # End - if not (found_circle or found_polygon):
                            if "altitude_lower" in volume["volume"].keys():
                                altitude_lower = volume["volume"]["altitude_lower"]
                                if "value" in altitude_lower.keys():
                                    altitude_value = altitude_lower["value"]
                                    if isinstance(altitude_value, numbers.Number):
                                        if (altitude_value < -8000.0) or (altitude_value > 100000.0):
                                            invalid += "altitude_lower.value out of range, "
                                        else:
                                            volume_data["altitude_lower_value"] = altitude_value
                                        # End - if (altitude_value < -8000.0) or (altitude_value > 100000.0):
                                    else:
                                        invalid += "constraint.details.volumes.volume.altitude_lower.value must be numeric, "
                                    # End - if isinstance(altitude_value, numbers.Number):
                                else:
                                    invalid += "constraint.details.volumes.volume.altitude_lower.value key not found, "
                                # End - if "value" in altitude_lower.keys():
                                if "reference" in altitude_lower.keys():
                                    altitude_reference = altitude_lower["reference"]
                                    if not altitude_reference == "W84":
                                        invalid += "altitude_lower.reference is invalid, "
                                    else:
                                        volume_data["altitude_lower_reference"] = altitude_reference
                                    # End - if not altitude_reference == "W84":
                                else:
                                    invalid = (
                                # End - if "reference" in altitude_lower.keys():
                                        invalid + "constraint.details.volumes.volume.altitude_lower.reference key not found, "
                                    )
                                if "units" in altitude_lower.keys():
                                    altitude_units = altitude_lower["units"]
                                    if not altitude_units == "M":
                                        invalid += "altitude_lower.units is invalid, "
                                    else:
                                        volume_data["altitude_lower_units"] = altitude_units
                                    # End - if not altitude_units == "M":
                                else:
                                    invalid += "constraint.details.volumes.volume.altitude_lower.units key not found, "
                                # End - if "units" in altitude_lower.keys():
                            else:
                                invalid += "constraint.details.volumes.volume.altitude_lower key not found, "
                            # End - if "altitude_lower" in volume["volume"].keys():
                            if "altitude_upper" in volume["volume"].keys():
                                altitude_upper = volume["volume"]["altitude_upper"]
                                if "value" in altitude_upper.keys():
                                    altitude_value = altitude_upper["value"]
                                    if isinstance(altitude_value, numbers.Number):
                                        if (altitude_value < -8000.0) or (altitude_value > 100000.0):
                                            invalid += "altitude_upper.value out of range, "
                                        else:
                                            volume_data["altitude_upper_value"] = altitude_value
                                        # End - if (altitude_value < -8000.0) or (altitude_value > 100000.0):
                                    else:
                                        invalid += "constraint.details.volumes.volume.altitude_upper.value must be numeric, "
                                    # End - if isinstance(altitude_value, numbers.Number):
                                else:
                                    invalid += "constraint.details.volumes.volume.altitude_upper.value key not found, "
                                # End - if "value" in altitude_upper.keys():
                                if "reference" in altitude_upper.keys():
                                    altitude_reference = altitude_upper["reference"]
                                    if not altitude_reference == "W84":
                                        invalid += "altitude_upper.reference is invalid, "
                                    else:
                                        volume_data["altitude_upper_reference"] = altitude_reference
                                    # End - if not altitude_reference == "W84":
                                else:
                                    invalid += "constraint.details.volumes.volume.altitude_upper.reference key not found, "
                                # End - if "reference" in altitude_upper.keys():
                                if "units" in altitude_upper.keys():
                                    altitude_units = altitude_upper["units"]
                                    if not altitude_units == "M":
                                        invalid += "altitude_upper.units is invalid, "
                                    else:
                                        volume_data["altitude_upper_units"] = altitude_units
                                else:
                                    invalid += "constraint.details.volumes.volume.altitude_upper.units key not found, "
                                # End - if "units" in altitude_upper.keys():
                            else:
                                invalid += "constraint.details.volumes.volume.altitude_upper key not found, "
                            # End - if "altitude_upper" in volume["volume"].keys():
                        else:
                            invalid += "constraint.details.volumes.volume key not found, "
                        # End - if "volume" in volume.keys():
                        if "time_start" in volume.keys():
                            time_start = volume["time_start"]
                            if "format" in time_start.keys():
                                time_start_format = time_start["format"]
                                if not time_start_format == "RFC3339":
                                    invalid += "constraint.details.volumes.volume.time_start.format wrong, "
                                else:
                                    volume_data["time_start_format"] = time_start_format
                                # End - if not time_start_format == "RFC3339":
                            else:
                                invalid += "constraint.details.volumes.volume.time_start.format key not found, "
                            # End - if "format" in time_start.keys():
                            if "value" in time_start.keys():
                                time_start_value = time_start["value"]
                                if not checkDateTime(time_start_value):
                                    invalid += "constraint.details.volumes.volume.time_start.value is invalid, "
                                else:
                                    volume_data["time_start_value"] = time_start_value
                                # End - if not checkDateTime(time_start_value):
                            else:
                                invalid += "constraint.details.volumes.volume.time_start.value key not found, "
                            # End - if "value" in time_start.keys():
                        else:
                            invalid += "constraint.details.volumes.volume.time_start key not found, "
                        # End - if "time_start" in volume.keys():
                        if "time_end" in volume.keys():
                            time_end = volume["time_end"]
                            if "format" in time_end.keys():
                                time_end_format = time_end["format"]
                                if not time_end_format == "RFC3339":
                                    invalid += "constraint.details.volumes.volume.time_end.format wrong, "
                                else:
                                    volume_data["time_end_format"] = time_end_format
                                # End - if not time_end_format == "RFC3339":
                            else:
                                invalid += "constraint.details.volumes.volume.time_end.format key not found, "
                            # End - if "format" in time_end.keys():
                            if "value" in time_end.keys():
                                time_end_value = time_end["value"]
                                if not checkDateTime(time_end_value):
                                    invalid += "constraint.details.volumes.volume.time_end.value is invalid, "
                                else:
                                    volume_data["time_end_value"] = time_end_value
                                # End - if not checkDateTime(time_end_value):
                            else:
                                invalid += "constraint.details.volumes.volume.time_end.value key not found, "
                            # End - if "value" in time_end.keys():
                        else:
                            invalid += "constraint.details.volumes.volume.time_end key not found, "
                        # End - if "time_end" in volume.keys():
                        volumes_data.append(volume_data)
                    # End - for volume in volumes:
                else:
                    invalid += "constraint.details.volumes key not found, "
                # End - if "volumes" in constraint_details.keys():
                constraint_type = ""
                if "type" in constraint["details"].keys():
                    constraint_type = constraint_details["type"]
                # End - if "type" in constraint["details"].keys():
            else:
                invalid += "constraint.details  key not found"
            # End - if "details" in constraint.keys():
        else:
            # Remove constraint
            # Get Reference information for highest version number
            sqlQuery = ("SELECT "
                        "constraintID, "
                        "active "
                        "FROM ConstraintReference WHERE constraintID = %s")
            bindData = constraintID
            self.cursor.execute(sqlQuery, bindData)
            records = self.cursor.fetchall()
            if len(records) > 0:
                constraint_active = records[0][1]
                if not constraint_active:
                    invalid += "Constraint is not active, "
                    status = 404
                else:
                    sqlQuery = ("UPDATE ConstraintReference "
                                "SET active = 0 "
                                "WHERE constraintID = %s")
                    bindData = constraintID
                    self.cursor.execute(sqlQuery, bindData)
                    records = self.cursor.fetchall()
                    self.connection.commit()
                    status = 204
                # End - if not constraint_active:
            else:
                invalid += "Invalid constraint, "
                status = 404
            # End - if len(records) > 0:
            result = {"status": status, "invalid": invalid}
            print("Invalid: " + str(invalid), flush = True)
            return result
        # End - if "constraint" in struct.keys():

        subscription_ids = []
        if "subscriptions" in struct.keys():
            subscriptions = struct["subscriptions"]
            subscription_ids = []
            notification_indices = []
            if len(subscriptions) == 0:
                invalid += "There are no subscriptions, "
            # End - if len(subscriptions) == 0:
            for subscription in subscriptions:
                if "subscription_id" in subscription.keys():
                    subscription_id = subscription["subscription_id"]
                    if not checkUUID(subscription_id):
                        invalid += "subscriptions.subscription_id is invalid, "
                    else:
                        subscription_ids.append(subscription_id)
                    # End - if not checkUUID(subscription_id):
                else:
                    invalid += "subscriptions.subscription_id key not found, "
                # End - if "subscription_id" in subscription.keys():
                if "notification_index" in subscription.keys():
                    notification_index = subscription["notification_index"]
                    if not isinstance(notification_index, int):
                        invalid += "subscriptions.notification_index is invalid, "
                    else:
                        notification_indices.append(notification_index)
                    # End - if not isinstance(notification_index, int):
                else:
                    invalid += "subscriptions.notification_index key not found, "
                # End - if "notification_index" in subscription.keys():
            # End - for subscription in subscriptions:
        else:
            invalid += "subscriptions key not found, "
        # End - if "subscriptions" in struct.keys():


        # Get version information for highest version number
        sqlQuery = ("SELECT "
                    "constraintID, "
                    "version, "
                    "active "
                    "FROM ConstraintReference WHERE constraintID = %s ORDER BY version DESC LIMIT 1")
        bindData = constraintID
        self.cursor.execute(sqlQuery, bindData)
        records = self.cursor.fetchall()
        if len(records) > 0:
            constraint_active = records[0][2]
            if not constraint_active:
                invalid += "Constraint is not active, "
            else:
                previous_version = records[0][1]
                if referenceResult['referenceData']['version'] < previous_version:
                    invalid += "Higher version exists, "
                # End - if referenceData["version"] < previous_version:
            # End - if not constraint_active:
        # End - if len(records) > 0:




        status = 204  # Succeeded
        self.connection.autocommit = False
        if invalid == "":
            referenceData = referenceResult["referenceData"]
            sqlQuery = ("INSERT INTO ConstraintReference ("
                       "ConstraintID, "
                       "manager, "
                       "uss_availability, "
                       "version, "
                       "ovn, "
                       "time_start_value, "
                       "time_start_format, "
                       "time_end_value, "
                       "time_end_format, "
                       "uss_base_url, "
                       "type, "
                       "active"
                       ") VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            bindData = [
                constraintID,
                referenceData["manager"],
                referenceData["uss_availability"],
                referenceData["version"],
                referenceData["ovn"],
                referenceData["time_start_value"],
                referenceData["time_start_format"],
                referenceData["time_end_value"],
                referenceData["time_end_format"],
                referenceData["uss_base_url"],
                constraint_type,
                1
            ]
            try:
                self.cursor.execute(sqlQuery, bindData)
            except self.connection.IntegrityError as err:
                status = 409  # Duplicate entry
            # End - try:
        else:
            status = 400  # Parameter error
        # End - if invalid == "":


        if status == 204: # Reference insert succeeded
            volumeID = 0 # Sequence number for Volumes
            for volume_data in volumes_data:
                if (volume_data["volume_type"] == "CIRCLE"):
                    sqlQuery = ("INSERT INTO ConstraintDetails ("
                                "constraintID, "
                                "version, "
                                "volumeID, "
                                "volume_type, "
                                "center_longitude, "
                                "center_latitude, "
                                "radius_value, "
                                "radius_units, "
                                "altitude_lower_value, "
                                "altitude_lower_reference, "
                                "altitude_lower_units, "
                                "altitude_upper_value, "
                                "altitude_upper_reference, "
                                "altitude_upper_units, "
                                "time_start_value, "
                                "time_start_format, "
                                "time_end_value, "
                                "time_end_format "
                                ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    bindData = [
                        constraintID,
                        referenceData["version"],
                        volumeID,
                        volume_data["volume_type"],
                        volume_data["center_longitude"],
                        volume_data["center_latitude"],
                        volume_data["radius_value"],
                        volume_data["radius_units"],
                        volume_data["altitude_lower_value"],
                        volume_data["altitude_lower_reference"],
                        volume_data["altitude_lower_units"],
                        volume_data["altitude_upper_value"],
                        volume_data["altitude_upper_reference"],
                        volume_data["altitude_upper_units"],
                        volume_data["time_start_value"],
                        volume_data["time_start_format"],
                        volume_data["time_end_value"],
                        volume_data["time_end_format"],
                    ]
                elif (volume_data["volume_type"] == "POLYGON"):
                    polystr = "POLYGON(("
                    for i in range(len(volume_data["polygon_lats"])):
                        polystr += str(volume_data["polygon_lngs"][i]) + " "
                        polystr += str(volume_data["polygon_lats"][i]) + ","
                    # End - for i in len(volume_data["polygon_lats"]):
                    polystr += str(volume_data["polygon_lngs"][0]) + " "
                    polystr += str(volume_data["polygon_lats"][0])
                    polystr += "))"
                    sqlQuery = ("INSERT INTO ConstraintDetails ("
                                "constraintID, "
                                "version, "
                                "volumeID, "
                                "volume_type, "
                                "polygon, "
                                "altitude_lower_value, "
                                "altitude_lower_reference, "
                                "altitude_lower_units, "
                                "altitude_upper_value, "
                                "altitude_upper_reference, "
                                "altitude_upper_units, "
                                "time_start_value, "
                                "time_start_format, "
                                "time_end_value, "
                                "time_end_format "
                                ") VALUES (%s, %s, %s, %s, ST_PolygonFromText(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    bindData = [
                        constraintID,
                        referenceData["version"],
                        volumeID,
                        volume_data["volume_type"],
                        polystr,
                        volume_data["altitude_lower_value"],
                        volume_data["altitude_lower_reference"],
                        volume_data["altitude_lower_units"],
                        volume_data["altitude_upper_value"],
                        volume_data["altitude_upper_reference"],
                        volume_data["altitude_upper_units"],
                        volume_data["time_start_value"],
                        volume_data["time_start_format"],
                        volume_data["time_end_value"],
                        volume_data["time_end_format"],
                    ]
                else:
                    print("volume_type should be CIRCLE or POLYGON", flush = True) # Should not get here
                # End - if (volume_data["volume_type"] == "CIRCLE"):
                try:
                    self.cursor.execute(sqlQuery, bindData)
                except self.connection.IntegrityError as err:
#                except:
                    status = 409  # Duplicate entry
#                    print(self.cursor._last_executed)
#                    pass
                # End - try:
                volumeID += 1
            # End - for volume_data in volumes_data:
        # End - if status == 204: # Reference and Details inserts succeeded

        if status == 204: # Reference and Volume inserts succeeded
            for i in range(len(subscription_ids)):
                sqlQuery = ("INSERT INTO ConstraintSubscriptions ("
                           "constraintID, "
                           "version, "
                           "subscription_id, "
                           "notification_index"
                           ") VALUES(%s, %s, %s, %s)")
                bindData = [
                    constraintID,
                    referenceData["version"],
                    subscription_ids[i],
                    notification_indices[i]
                ]
                try:
                    self.cursor.execute(sqlQuery, bindData)
                except self.connection.IntegrityError as err:
                    status = 409  # Duplicate entry
                # End - try:
            # End - for i in range(len(subscription_ids)):
        # End - if status == 204: # Reference and Volume inserts succeeded

        if status == 204: # All inserts succeded, commit
            self.connection.commit()
        else: # Something went wrong, rollback
            self.connection.rollback()
        # End - if status == 204:
        self.connection.autocommit = True
        result = {"status": status, "invalid": invalid}
        print("Invalid: " + str(invalid), flush = True)
        return result
    # End - def postConstraint(self, struct):


    # GET Constraint
    def getConstraint(self, entityID):
        invalid = ""
        if checkUUID(entityID):
            # Get Reference information for highest version number
            sqlQuery = ("SELECT "
                        "constraintID, "
                        "manager, "
                        "uss_availability, "
                        "version, "
                        "ovn, "
                        "time_start_value, "
                        "time_start_format, "
                        "time_end_value, "
                        "time_end_format, "
                        "uss_base_url, "
                        "type, "
                        "active "
                        "FROM ConstraintReference WHERE constraintID = %s ORDER BY version DESC LIMIT 1")
            bindData = entityID
            self.cursor.execute(sqlQuery, bindData)
            records = self.cursor.fetchall()
            if len(records) > 0:
                constraint_active = records[0][11]
                if not constraint_active:
                    invalid += "Constraint is not active, "
                    result = {"status": 404}
                else:
                    reference = {
                        "id": records[0][0],
                        "manager": records[0][1],
                        "uss_availability": records[0][2],
                        "version": records[0][3],
                        "ovn": records[0][4],
                        "time_start": {"value": records[0][5], "format": records[0][6]},
                        "time_end": {"value": records[0][7], "format": records[0][8]},
                        "uss_base_url": records[0][9],
                    }
                    constraint_type  = records[0][10]
                    # If ovn is null, do not include
                    if records[0][4] == "":
                        del reference["ovn"]
                    # End - if records[0][4] == "":

                    # Get Trajectory information
                    sqlQuery = ("SELECT "
                                "volume_type, "
                                "center_longitude, "
                                "center_latitude, "
                                "radius_value, "
                                "radius_units, "
                                "ST_AsText(polygon), "
                                "altitude_lower_value, "
                                "altitude_lower_reference, "
                                "altitude_lower_units, "
                                "altitude_upper_value, "
                                "altitude_upper_reference, "
                                "altitude_upper_units, "
                                "time_start_value, "
                                "time_start_format, "
                                "time_end_value, "
                                "time_end_format "
                                "FROM ConstraintDetails WHERE constraintID = %s and version = %s ORDER BY volumeID")
                    bindData = [entityID, reference["version"]]
                    self.cursor.execute(sqlQuery, bindData)
                    records = self.cursor.fetchall()
                    volumes_list = []
                    for record in records:
                        volumes = {}
                        volume_type = record[0]
                        volume = {}
                        if volume_type == "CIRCLE":
                            volume = {"outline_circle": {"center": {"lng": record[1], "lat": record[2]}, "radius": {"value": record[3], "units": record[4]}}}
                        elif volume_type == "POLYGON":
                            polygon = record[5]
                            polygon_text_len = len(polygon)
                            points = polygon[9:len(polygon)-2]
                            points = points.split(',')
                            vertices = []
                            for point in points:
                                xy = point.split(' ')
                                vertices.append({"lng": float(xy[0]), "lat": float(xy[1])})
                            # End - for point in points:
                            del vertices[-1]
                            volume = {"outline_polygon": {"vertices": vertices}}
                        else:
                            print("volume_type should be CIRCLE or POLYGON", flush = True) # Should not get here
                        altitude_lower = {"value": record[6], "reference": record[7], "units": record[8]}
                        altitude_upper = {"value": record[9], "reference": record[10], "units": record[11]}
                        volume["altitude_lower"] = altitude_lower
                        volume["altitude_upper"] = altitude_upper
                        volumes["volume"] = volume
                        time_start = {"value": record[12], "format":record[13]}
                        time_end = {"value": record[14], "format":record[15]}
                        volumes["time_start"] = time_start
                        volumes["time_end"] = time_end
                        # End - if volume_type == "CIRCLE":
                        volumes_list.append(volumes)
                    # End - for record in records:
                    # Remove last element, which is a copy of the first element


                    constraint = {
                        "constraint": {
                            "reference": reference,
                            "details": {"volumes": volumes_list, "type": constraint_type}
                        }
                    }

                    result = {"constraint": constraint, "status": 200}
                # End - if not constraint_active:
            else:
                result = {"status": 404}
            # End - if len(records) > 0:
        else:
            result = {"status": 400}
        # End - if checkUUID(entityID):
        print("Invalid: " + str(invalid), flush = True)
        return result
    # End - def getConstraint(self, entityID):

    # Check PSU Client Trajectory
    def checkPsuClientTrajectory(self, trajectory):
        invalid = ""
        trajectoryData = []
        npoints = len(trajectory)
        if (npoints < 2) or (npoints > 1000):
            invalid += "trajectory must contain 2 to 1000 points, "
        else:
            point_count = 0
            npoints = len(trajectory)
            for TrajectoryPoint4D in trajectory:
                if "point_designator_uuid" in TrajectoryPoint4D.keys():
                    point_designator_uuid = TrajectoryPoint4D["point_designator_uuid"]
                    if not checkUUID(point_designator_uuid):
                        invalid += "point_designator_uuid format is invalid, "
                    # End - if not checkUUID(point_designator_uuid):
                else:
                    invalid += "point_designator_uuid key not found, "
                # End - if "point_designator_uuid" in TrajectoryPoint4D.keys():
                point_designator = ""  # Optional
                if "point_designator" in TrajectoryPoint4D.keys():
                    point_designator = TrajectoryPoint4D["point_designator"]
                # End - if "point_designator" in TrajectoryPoint4D.keys():
                if "point_type" in TrajectoryPoint4D.keys():
                    point_type = TrajectoryPoint4D["point_type"]
                    if (not point_type in PointTypes):
                        invalid += "trajectory.point_type invalid, "
                    # End - if (not point_type in PointTypes):
                else:
                    invalid += "point_type key not found, "
                if "speed_type" in TrajectoryPoint4D.keys():
                    speed_type = TrajectoryPoint4D["speed_type"]
                    if (not speed_type in SpeedTypes):
                        invalid += "trajectory.speed_type invalid, "
                    # End - if (not speed_type in SpeedTypes):
                else:
                    invalid += "speed_type key not found, "
                if "lat_lng_point" in TrajectoryPoint4D.keys():
                    lat_lng_point = TrajectoryPoint4D["lat_lng_point"]
                    if "lat" in lat_lng_point.keys():
                        lat = lat_lng_point["lat"]
                        if isinstance(lat, numbers.Number):
                            if (lat < -90) or (lat > 90):
                                invalid += "trajectory.lat_lng_point.lat out of range, "
                            # End - if (lat < -90) or (lat > 90):
                        else:
                            invalid += "trajectory.lat_lng_point.lat must be numeric, "
                        # End - if isinstance(lat, numbers.Number):
                    else:
                        invalid += "trajectory.lat_lng_point.lat key not found, "
                    # End - if "lat" in lat_lng_point.keys():
                    if "lng" in lat_lng_point.keys():
                        lng = lat_lng_point["lng"]
                        if isinstance(lng, numbers.Number):
                            if (lng < -180) or (lng > 180):
                                invalid += "trajectory.lat_lng_point.lng out of range, "
                            # End - if (lng < -180) or (lng > 180):
                        else:
                            invalid += "trajectory.lat_lng_point.lng must be numeric, "
                        # End - if isinstance(lng, numbers.Number):
                    else:
                        invalid += "trajectory.lat_lng_point.lng key not found, "
                    # End - if "lng" in lat_lng_point.keys():
                else:
                    invalid += "lat_lng_point key not found, "
                # End - if "lat_lng_point" in TrajectoryPoint4D.keys():
                if "altitude" in TrajectoryPoint4D.keys():
                    altitude = TrajectoryPoint4D["altitude"]
                    if "value" in altitude.keys():
                        altitude_value = altitude["value"]
                        if isinstance(altitude_value, numbers.Number):
                            if (altitude_value < -8000) or (altitude_value > 100000):
                                invalid += "trajectory.altitude.value out of range, "
                            # End - if (altitude_value < -8000) or (altitude_value > 100000):
                        else:
                            invalid += "trajectory.altitude.value must be numeric, "
                        # End - if isinstance(altitude_value, numbers.Number):
                    else:
                        invalid += "trajectory.altitude.value key not found, "
                    # End - if "value" in altitude.keys():
                    if "reference" in altitude.keys():
                        altitude_reference = altitude["reference"]
                        if not altitude_reference == "W84":
                            invalid += "trajectory.altitude.reference invalid, "
                        # End - if not altitude_reference == "W84":
                    else:
                        invalid += "trajectory.altitude.reference key not found, "
                    # End - if "reference" in altitude.keys():
                    if "units" in altitude.keys():
                        altitude_units = altitude["units"]
                        if not altitude_units == "M":
                            invalid += "trajectory.altitude.units invalid, "
                        # End - if not altitude_units == "M":
                    else:
                        invalid += "trajectory.altitude.units key not found, "
                    # End - if "units" in altitude.keys():
                else:
                    invalid += "trajectory.altitude key not found, "
                # End - if "altitude" in TrajectoryPoint4D.keys():
                if "time" in TrajectoryPoint4D.keys():
                    time = TrajectoryPoint4D["time"]
                    if "format" in time.keys():
                        time_format = time["format"]
                        if not time_format == "RFC3339":
                            invalid += "trajectory.time.format wrong, "
                        # End - if not time_format == "RFC3339":
                    else:
                        invalid += "trajectory.time.format key not found, "
                    # End - if "format" in time.keys():
                    if "value" in time.keys():
                        time_value = time["value"]
                        if not checkDateTime(time_value):
                            invalid += "trajectory.time.value invalid, "
                        # End - if not checkDateTime(time_value):
                    else:
                        invalid += "trajectory.time.value key not found, "
                    # End - if "value" in time.keys():
                else:
                    invalid += "trajectory.time key not found, "
                # End - if "time" in TrajectoryPoint4D.keys():
                if "speed" in TrajectoryPoint4D.keys():
                    velocity = TrajectoryPoint4D["speed"]
                    if "speed" in velocity.keys():
                        speed = velocity["speed"]
                        if not isinstance(speed, numbers.Number):
                            invalid += "trajectory.speed.speed must be numeric, "
                        # End - if not isinstance(speed, numbers.Number):
                    else:
                        invalid += "trajectory.speed.speed key not found, "
                    # End - if "speed" in velocity.keys():
                    if "units_speed" in velocity.keys():
                        units_speed = velocity["units_speed"]
                        if not units_speed in {"MetersPerSecond", "Knots"}:
                            invalid += "trajectory.speed.units_speed invalid, "
                        # End - if not units_speed in {"MetersPerSecond", "Knots"}:
                    else:
                        invalid += "trajectory.speed.units_speed key not found, "
                    # End - if "units_speed" in velocity.keys():
                    track = 0  # Optional
                    if "track" in velocity.keys():
                        track = velocity["track"]
                        if isinstance(track, numbers.Number):
                            if (track < 0) or (track > 360):
                                invalid += "trajectory.speed.track out of range, "
                            # End - if (track < 0) or (track > 360):
                        else:
                            invalid += "trajectory.speed.track must be numeric, "
                        # End - if isinstance(track, numbers.Number):
                    # End - if "track" in velocity.keys():
                    speed_speed_type = "GROUND"  # Optional
                    if "speed_type" in velocity.keys():
                        speed_speed_type = velocity["speed_type"]
                        if not speed_speed_type in {"GROUND", "AIR"}:
                            invalid += "trajectory.speed.speed_type invalid, "
                        # End - if not speed_speed_type in {"GROUND", "AIR"}:
                    # End - if "speed_type" in velocity.keys():
                else:
                    invalid += "trajectory.speed key not found, "
                # End - if "speed" in TrajectoryPoint4D.keys():
                if "trajectory_property_array" in TrajectoryPoint4D.keys():
                    trajectory_property_array = TrajectoryPoint4D[
                        "trajectory_property_array"
                    ]
                    nprops = len(trajectory_property_array)
                    if (nprops < 1) or (nprops > 4):
                        invalid += "trajectory.trajectory_property_array x must contain 1 to 4 properties, "
                    else:
                        properties = []
                        found_airport_reference_location = False
                        found_wheels_off = False
                        found_wheels_on = False
                        for TrajectoryProperty in trajectory_property_array:
                            if("property_type" in TrajectoryProperty.keys()):
                                property_type = TrajectoryProperty["property_type"]
                                if property_type == "AIRPORT_REFERENCE_LOCATION":
                                    found_airport_reference_location = True
                                # End - if property_type == "AIRPORT_REFERENCE_LOCATION":
                                if property_type == "WHEELS_OFF":
                                    found_wheels_off = True
                                # End - if property_type == "WHEELS_OFF":
                                if property_type == "WHEELS_ON":
                                    found_wheels_on = True
                                # End - if property_type == "WHEELS_ON":
                                if (property_type in PropertyTypes):
                                    properties.append(property_type)
                                else:
                                    invalid += "trajectory.trajectory_property_array.property_type invalid, "
                                # End - if (property_type in PropertyTypes):
                            else:
                                invalid += "trajectory.trajectory_property_array.property_type key not found, "
                            # End - if("property_type" in TrajectoryProperty.keys()):
                        # End - for TrajectoryProperty in trajectory_property_array:
                        if point_count == 0:
                            if not (found_airport_reference_location and found_wheels_off):
                                invalid += "trajectory.trajectory_property_array.property_type first point does not have airport_reference_location and wheels_off, " 
                            # End - if not (found_airport_reference_location and found_wheels_off):
                        # End - if point_count == 0:
                        if point_count == npoints - 1:
                            if not (found_airport_reference_location and found_wheels_on):
                                invalid += "trajectory.trajectory_property_array.property_type last point does not have airport_reference_location and wheels_on, " 
                            # End - if not (found_airport_reference_location and found_wheels_off):
                        # End - if point_count == npoints - 1:
                    # End - if (nprops < 1) or (nprops > 4):
                else:
                    invalid += "trajectory.trajectory_property_array key not found, "
                # End - if "trajectory_property_array" in TrajectoryPoint4D.keys():

                # If Trajectory has no errors, return fields in a dictionary
                if invalid == "":
                    trajectory_item = {
                        "point_designator_uuid": point_designator_uuid,
                        "point_designator": point_designator,
                        "point_type": point_type,
                        "speed_type": speed_type,
                        "lat": lat,
                        "lng": lng,
                        "altitude_value": altitude_value,
                        "altitude_reference": altitude_reference,
                        "altitude_units": altitude_units,
                        "time_format": time_format,
                        "time_value": time_value,
                        "speed": speed,
                        "units_speed": units_speed,
                        "track": track,
                        "speed_speed_type": speed_speed_type,
                        "properties": properties,
                    }
                    trajectoryData.append(trajectory_item)
                # End - if invalid == "":
                point_count += 1
            # End - for TrajectoryPoint4D in trajectory:
        # End - if (npoints < 2) or (npoints > 1000):
        result = {"invalid": invalid, "trajectoryData": trajectoryData}
        return result
    # End - def checkPsuClientTrajectory(self, trajectory):

    def putPsuClientOperationalIntent(self, entityID, ovn, data):
        invalid = ""
        status = 200

        if not checkUUID(entityID):
            invalid += "entityId format is invalid, "
        # End - if not checkUUID(entityID):
        if (not ovn == ""):
            if (len(ovn) < 16) or (len(ovn) > 128):
                invalid += "reference.ovn incorrect length, "
            # End - if (len(ovn) < 16) or (len(ovn) > 128):
        # End - if (not ovn == ""):
        if "volume" in data.keys():
            volume = data["volume"]
            volume_data = {}
            if "outline_polygon" in volume.keys():
                volume_data["volume_type"] = "POLYGON"
                outline_polygon = volume["outline_polygon"]
                if "vertices" in outline_polygon.keys():
                    vertices = outline_polygon["vertices"]
                    lngs = [];
                    lats = [];
                    if not len(vertices) >= 3:
                        invalid += "vertices must have at least 3 entries, "
                    # End - if not len(vertices) >= 3:
                    for vertex in vertices:
                        if "lng" in vertex.keys():
                            lng = vertex["lng"]
                            if isinstance(lng, numbers.Number):
                                if (lng < -180) or (lng > 180):
                                    invalid += "volume.outline_polygon.vertices.lng out of range, "
                                else:
                                    lngs.append(lng)
                                # End - if (lng < -180) or (lng > 180):
                            else:
                                invalid += "volume.outline_polygon.vertices.lng must be numeric, "
                            # End - if isinstance(lng, numbers.Number):
                        else:
                            invalid += "volume.outline_polygon.vertices.lng key not found, "
                        # End - if "lng" in vertex.keys():
                        if "lat" in vertex.keys():
                            lat = vertex["lat"]
                            if isinstance(lat, numbers.Number):
                                if (lat < -90) or (lat > 90):
                                    invalid += "volume.outline_polygon.vertices.lat out of range, "
                                else:
                                    lats.append(lat)
                                # End - if (lat < -90) or (lat > 90):
                            else:
                                invalid += "volume.outline_polygon.vertices.lat must be numeric, "
                            # End - if isinstance(lnststg, numbers.Number):
                        else:
                            invalid += "volume.outline_polygon.vertices.lat key not found, "
                        # End - if "lat" in vertex.keys():
                    # End - for vertex in vertices:
                else:
                    invalid += "volume.outline_polygon.vertices key not found, "
                # End - if "vertices" in outline_polygon.keys():
                volume_data["polygon_lngs"] = lngs
                volume_data["polygon_lats"] = lats
            else:
                invalid += "volume.outline_polygon key not found, "
            # End - if "outline_polygon" in volume.keys():
            if "altitude_lower" in volume.keys():
                altitude_lower = volume["altitude_lower"]
                if "value" in altitude_lower.keys():
                    altitude_value = altitude_lower["value"]
                    if isinstance(altitude_value, numbers.Number):
                        if (altitude_value < -8000.0) or (altitude_value > 100000.0):
                            invalid += "altitude_lower.value out of range, "
                        else:
                            volume_data["altitude_lower_value"] = altitude_value
                        # End - if (altitude_value < -8000.0) or (altitude_value > 100000.0):
                    else:
                        invalid += "volume.altitude_lower.value must be numeric, "
                    # End - if isinstance(altitude_value, numbers.Number):
                else:
                    invalid += "volume.altitude_lower.value key not found, "
                # End - if "value" in altitude_lower.keys():
                if "reference" in altitude_lower.keys():
                    altitude_reference = altitude_lower["reference"]
                    if not altitude_reference == "W84":
                        invalid += "altitude_lower.reference is invalid, "
                    else:
                        volume_data["altitude_lower_reference"] = altitude_reference
                    # End - if not altitude_reference == "W84":
                else:
                    invalid = (
                # End - if "reference" in altitude_lower.keys():
                        invalid + "volume.altitude_lower.reference key not found, "
                    )
                if "units" in altitude_lower.keys():
                    altitude_units = altitude_lower["units"]
                    if not altitude_units == "M":
                        invalid += "altitude_lower.units is invalid, "
                    else:
                        volume_data["altitude_lower_units"] = altitude_units
                    # End - if not altitude_units == "M":
                else:
                    invalid += "volume.altitude_lower.units key not found, "
                # End - if "units" in altitude_lower.keys():
            else:
                invalid += "volume.altitude_lower key not found, "
            # End - if "altitude_lower" in volume.keys():
            if "altitude_upper" in volume.keys():
                altitude_upper = volume["altitude_upper"]
                if "value" in altitude_upper.keys():
                    altitude_value = altitude_upper["value"]
                    if isinstance(altitude_value, numbers.Number):
                        if (altitude_value < -8000.0) or (altitude_value > 100000.0):
                            invalid += "altitude_upper.value out of range, "
                        else:
                            volume_data["altitude_upper_value"] = altitude_value
                        # End - if (altitude_value < -8000.0) or (altitude_value > 100000.0):
                    else:
                        invalid += "volume.altitude_upper.value must be numeric, "
                    # End - if isinstance(altitude_value, numbers.Number):
                else:
                    invalid += "volume.altitude_upper.value key not found, "
                # End - if "value" in altitude_upper.keys():
                if "reference" in altitude_upper.keys():
                    altitude_reference = altitude_upper["reference"]
                    if not altitude_reference == "W84":
                        invalid += "altitude_upper.reference is invalid, "
                    else:
                        volume_data["altitude_upper_reference"] = altitude_reference
                    # End - if not altitude_reference == "W84":
                else:
                    invalid += "volume.altitude_upper.reference key not found, "
                # End - if "reference" in altitude_upper.keys():
                if "units" in altitude_upper.keys():
                    altitude_units = altitude_upper["units"]
                    if not altitude_units == "M":
                        invalid += "altitude_upper.units is invalid, "
                    else:
                        volume_data["altitude_upper_units"] = altitude_units
                else:
                    invalid += "volume.altitude_upper.units key not found, "
                # End - if "units" in altitude_upper.keys():
            else:
                invalid += "volume.altitude_upper key not found, "
            # End - if "altitude_upper" in volume.keys():
        else:
            invalid += "volume key not found, "
        # End - if "volume" in data.keys():
        if "aircraft_registration" in data.keys():
            aircraft_registration = data["aircraft_registration"]
            found = re.search("^[A-Z0-9]{1,7}$", aircraft_registration)
            if not found:
                invalid += "aircraft_registration invalid format, "
            # End - if not found:
        else:
            invalid += "aircraft_registration key not found, "
        # End - if "aircraft_registration" in data.keys():

        if "operator_name" in data.keys():
            operator_name = data["operator_name"]
            found = re.search("^[A-Z]{3}$", operator_name)
            if not found:
                invalid += "operator_name invalid format, "
            # End - if not found:
        else:
            invalid += "operator_name key not found, "
        # End - if "operator_name" in data.keys():
        if "trajectory" in data.keys():
            trajectory = data["trajectory"]
            trajectoryResult = self.checkPsuClientTrajectory(trajectory)
            invalid += trajectoryResult["invalid"]
        else:
            invalid += "trajectory key not found, "
        # End - if "trajectory" in data.keys():
        if "time_start" in data.keys():
            time_start = data["time_start"]
            if "format" in time_start.keys():
                time_start_format = time_start["format"]
                if not time_start_format == "RFC3339":
                    invalid += "time_start.format wrong, "
                # End - if not time_start_format == "RFC3339":
            else:
                invalid += "time_start.format key not found, "
            # End - if "format" in time_start.keys():
            if "value" in time_start.keys():
                time_start_value = time_start["value"]
                if not checkDateTime(time_start_value):
                    invalid += "time_start.value is invalid, "
                # End - if not checkDateTime(time_start_value):
            else:
                invalid += "time_start.value key not found, "
            # End - if "value" in time_end.keys():
        else:
            invalid += "time_start key not found, "
        # End - if "time_start" in data.keys():
        if "time_end" in data.keys():
            time_end = data["time_end"]
            if "format" in time_end.keys():
                time_end_format = time_end["format"]
                if not time_end_format == "RFC3339":
                    invalid += "time_end.format wrong, "
                # End - if not time_end_format == "RFC3339":
            else:
                invalid += "tine_end.format key not found, "
            # End - if "format" in time_end.keys():
            if "value" in time_end.keys():
                time_end_value = time_end["value"]
                if not checkDateTime(time_end_value):
                    invalid += "time_end.value is invalid, "
                # End - if not checkDateTime(time_end_value):
            else:
                invalid += "time_end.value key not found, "
            # End - if "value" in time_end.keys():
        else:
            invalid += "time_end key not found, "
        # End - if "time_end" in data.keys():
        if "adaptation_id" in data.keys():
            adaptation_id = data["adaptation_id"]
            if not checkUUID(adaptation_id):
                invalid += "adaptation_id format is invalid, "
            # End - if not checkUUID(adaptation_id):
        # End - if "adaptation_id" in data.keys():
        if "state" in data.keys():
            state = data["state"]
            if not state in { "Draft", "Accept", "Activate", "End"}:
                invalid += "state is invalid, "
            # End - if not checkUUID(adaptaiion_id):
        # End - if "state" in data.keys():
        if "purpose" in data.keys():
            purpose = data["purpose"]
        # End - if "purpose" in data.keys():

        polystr = "POLYGON(("
        for i in range(len(volume_data["polygon_lats"])):
            polystr += str(volume_data["polygon_lngs"][i]) + " "
            polystr += str(volume_data["polygon_lats"][i]) + ","
        # End - for i in len(volume_data["polygon_lats"]):
        polystr += str(volume_data["polygon_lngs"][0]) + " "
        polystr += str(volume_data["polygon_lats"][0])
        polystr += "))"

        status = 204  # Succeeded
        self.connection.autocommit = False
        if invalid == "":
            sqlQuery = ("INSERT INTO PsuClientOperationalIntentReference ("
                       "operationalIntentID, "
                       "ovn, "
                       "polygon, "
                       "altitude_lower_value, "
                       "altitude_lower_reference, "
                       "altitude_lower_units, "
                       "altitude_upper_value, "
                       "altitude_upper_reference, "
                       "altitude_upper_units, "
                       "aircraft_registration, "
                       "operator_name, "
                       "time_start_value, "
                       "time_start_format, "
                       "time_end_value, "
                       "time_end_format, "
                       "adaptation_id, "
                       "state, "
                       "purpose "
                       ") VALUES (%s, %s, ST_PolygonFromText(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            bindData = [
                entityID,
                ovn,
                polystr,
                volume_data['altitude_lower_value'],
                volume_data['altitude_lower_reference'],
                volume_data['altitude_lower_units'],
                volume_data['altitude_upper_value'],
                volume_data['altitude_upper_reference'],
                volume_data['altitude_upper_units'],
                aircraft_registration,
                operator_name,
                time_start_value,
                time_start_format,
                time_end_value,
                time_end_format,
                adaptation_id,
                state,
                purpose
            ]
            try:
                self.cursor.execute(sqlQuery, bindData)
            except self.connection.IntegrityError as err:
                status = 409  # Duplicate entry
            # End - try:
        else:
            status = 400  # Parameter error
        # End - if invalid == "":

        # Insert AllOperationalIntentReference
        self.connection.autocommit = False
        if invalid == "":
            sqlQuery = ("INSERT INTO AllOperationalIntentReference ("
                       "operationalIntentID "
                       ") VALUES (%s)")
            bindData = [
                entityID
            ]
            try:
                self.cursor.execute(sqlQuery, bindData)
            except self.connection.IntegrityError as err:
                status = 409  # Duplicate entry
            # End - try:
        else:
            status = 400  # Parameter error
        # End - if invalid == "":


        if status == 204: # Reference insert succeeded
            trajectoryPoint = 0 # Sequence number for Trajectory Points
            trajectoryData = trajectoryResult["trajectoryData"]
            for trajectoryItem in trajectoryData:
                sqlQuery = ("INSERT INTO PsuClientTrajectory ("
                            "operationalIntentID, "
                            "ovn, "
                            "pointID, "
                            "point_designator_uuid, "
                            "point_designator, "
                            "point_type, "
                            "speed_type, "
                            "latitude, "
                            "longitude, "
                            "altitude_value, "
                            "altitude_reference, "
                            "altitude_units, "
                            "time_value, "
                            "time_format, "
                            "speed, "
                            "units_speed, "
                            "track, "
                            "speed_speed_type, "
                            "properties"
                            ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

                propertyString = ""
                for p in trajectoryItem["properties"]:
                    if not propertyString == "":
                        propertyString += ","
                    # End - if not propertyString == "":
                    propertyString += p
                # End - for p in trajectoryItem["properties"]:

                bindData = [
                    entityID,
                    ovn,
                    trajectoryPoint,
                    trajectoryItem["point_designator_uuid"],
                    trajectoryItem["point_designator"],
                    trajectoryItem["point_type"],
                    trajectoryItem["speed_type"],
                    trajectoryItem["lat"],
                    trajectoryItem["lng"],
                    trajectoryItem["altitude_value"],
                    trajectoryItem["altitude_reference"],
                    trajectoryItem["altitude_units"],
                    trajectoryItem["time_value"],
                    trajectoryItem["time_format"],
                    trajectoryItem["speed"],
                    trajectoryItem["units_speed"],
                    trajectoryItem["track"],
                    trajectoryItem["speed_speed_type"],
                    propertyString
                ]
                try:
                    self.cursor.execute(sqlQuery, bindData)
                except self.connection.IntegrityError as err:
                    status = 409  # Duplicate entry
                # End - try:
                trajectoryPoint += 1
            # End - for trajectoryItem in trajectoryData:
        # End - if status == 204: # Reference insert succeeded

        if status == 204: # All inserts succeded, commit
            self.connection.commit()
        else: # Something went wrong, rollback
            self.connection.rollback()
        # End - if status == 204:
        self.connection.autocommit = True
        result = {"status": status, "invalid": invalid}
        print("Invalid: " + str(invalid), flush = True)

        return result
    # End - def putPsuClientOperationalIntent(self, entityID, data):

    def putCommandUAV(self, data):
        invalid = ""
        status = 204

        if "flight_plan_id" in data.keys():
            operationalIntentID = data["flight_plan_id"]
            if not checkUUID(operationalIntentID):
                invalid += "flight_plan_id format is invalid, "
            # End - if not checkUUID(operationalIntentID):
        else:
            invalid += "flight_plan_id key not found, "
        # End - if "flight_plan_id" in data.keys():

        if "type" in data.keys():
            command_type = data["type"]
            if not command_type == "mav_command":
                invalid += "type must be mav_command, "
            # End - if not command_type == "mav_command":
        else:
            invalid += "type key not found, "
        # End - if "type" in data.keys():

        if "command_id" in data.keys():
            command_id = data["command_id"]
            if (not isinstance(command_id, int)):
                invalid += "command_id must be integer"
            else:
                if not command_id in {1, 12, 14}:
                    invalid += "command_id must be one of 1, 12 or 14"
                # End - if not command_id in {"1", "12", "14"}:
            # End - if (not isinstance(command_id, int)):
        else:
            invalid += "command_id key not found, "
        # End - if "command_id" in data.keys():

        if "drone_id" in data.keys():
            aircraft_registration = data["drone_id"]
            found = re.search("^[A-Z0-9]{1,7}$", aircraft_registration)
            if not found:
                invalid += "drone_id invalid format, "
            # End - if not found:
        else:
            invalid += "drone_id key not found, "
        # End - if "drone_id" in data.keys():

        sqlQuery = ("INSERT INTO CommandUAV ("
                   "operationalIntentID, "
                   "type, "
                   "command_id, "
                   "aircraft_registration "
                   ") VALUES(%s, %s, %s, %s)")
        bindData = [
            operationalIntentID,
            command_type,
            command_id,
            aircraft_registration
        ]
        try:
            self.cursor.execute(sqlQuery, bindData)
        except self.connection.IntegrityError as err:
            status = 409  # Foreign key error
        # End - try:

        if status == 204: # All inserts succeded, commit
            self.connection.commit()
        else: # Something went wrong, rollback
            self.connection.rollback()
        # End - if status == 204:
        self.connection.autocommit = True
        result = {"status": status, "invalid": invalid}
        print("Invalid: " + str(invalid), flush = True)

        return result
    # End - def putPsuClientOperationalIntent(self, entityID, ovn, data):

    def logPut(self, direction, remote, request_uri, request_method, request_time, request_header, request_json, response_time, response_json, invalid, status):
        sqlQuery = ("INSERT INTO RequestLog ("
                   "direction, "
                   "remote, "
                   "request_uri, "
                   "request_method, "
                   "request_time, "
                   "request_header, "
                   "request_json, "
                   "response_time, "
                   "response_json, "
                   "invalid, "
                   "status"
                   ") VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        bindData = [
            direction,
            remote,
            request_uri,
            request_method,
            request_time,
            request_header,
            request_json,
            response_time,
            response_json,
            invalid,
            status
        ]
        try:
            self.cursor.execute(sqlQuery, bindData)
        except:
#            print(self.cursor._last_executed)
            pass
        # End - try:
        self.connection.commit()
    # End - def logIt(self, direction, remote, request_uri, request_method, request_time, request_header, request_json, response_time, response_json, invalid, status)

    def logGet(self ):
        status = 200
        sqlQuery = ("SELECT "
                    "request_uri, "
                    "request_method, "
                    "direction, "
                    "DATE_FORMAT(request_time, '%Y-%m-%dT%H:%i:%s.%fZ'), "
                    "request_header, "
                    "request_json, "
                    "DATE_FORMAT(response_time, '%Y-%m-%dT%H:%i:%s.%fZ'), "
                    "response_json, "
                    "status "
                    "FROM RequestLog ORDER BY request_time ASC")
        self.cursor.execute(sqlQuery)
        records = self.cursor.fetchall()
        logs = []
        for record in records:
            log = {}
            log["url"] = record[0]
            log["method"] = record[1]
            log["headers"] = record[4]
            if (record[2] == "IN"):
                log["recorder_role"] = "Server"
            elif (record[2] == "OUT"):
                log["recorder_role"] = "Client"
            else:
                log["recorder_role"] = "Unknown"
            log["request_time"] = {}
            log["request_time"]["format"] = "RFC3339"
            log["request_time"]["value"] = record[3]
            log["request_body"] = base64.b64encode(record[5].encode("ascii")).decode("ascii")
            log["response_time"] = {}
            log["response_time"]["format"] = "RFC3339"
            log["response_time"]["value"] = record[6]
            log["response_body"] = base64.b64encode(record[7].encode("ascii")).decode("ascii")
            log["response_code"] = record[8]
            logs.append(log)
        result = {"exchange": logs}
        return result, status
    # End - def logGet(self ):
# End - class processData(object):
