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

    # POST Telemetry - Not based on any API, just included so we can perform GET
    def postTelemetry(self, struct):
        invalid = ""

        first = struct["Country"]
        last = struct["Animal"]
        

        status = 200  # Succeeded
        self.connection.autocommit = False
        if invalid == "":
            sqlQuery = ("INSERT INTO animalKingdom ("
                            "Country, "
                            "Animal"
                            ") VALUES (%s, %s)")
            bindData = [
                    first,
                    last
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
