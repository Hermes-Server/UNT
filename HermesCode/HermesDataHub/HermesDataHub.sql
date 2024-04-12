SET foreign_key_checks = 0;
DROP TABLE IF EXISTS `unt`.`PsuClientOperationalIntentReference`;
CREATE TABLE `unt`.`PsuClientOperationalIntentReference` (
	`operationalIntentID` CHAR(36) NOT NULL,
	`ovn` VARCHAR(128),
	`polygon` POLYGON,
	`altitude_lower_value` DOUBLE,
	`altitude_lower_reference` CHAR(3),
	`altitude_lower_units` CHAR(1),
	`altitude_upper_value` DOUBLE,
	`altitude_upper_reference` CHAR(3),
	`altitude_upper_units` CHAR(1),
	`aircraft_registration` VARCHAR(7),
	`operator_name` CHAR(3),
	`time_start_value` CHAR(24) NOT NULL,
	`time_start_format` CHAR(7) NOT NULL,
	`time_end_value` CHAR(24) NOT NULL,
	`time_end_format` CHAR(7) NOT NULL,
	`adaptation_id` CHAR(36) NOT NULL,
	`state` ENUM('Draft', 'Accept', 'Activate', 'End'),
	`purpose` VARCHAR(128),
	UNIQUE (`operationalIntentID`, `ovn`))
	ENGINE = InnoDB;

DROP TABLE IF EXISTS `unt`.`PsuClientTrajectory`;
CREATE TABLE `unt`.`PsuClientTrajectory` (
	`operationalIntentID` CHAR(36) NOT NULL,
	`ovn` VARCHAR(128),
	`pointID` INT NOT NULL,
	`point_designator_uuid` CHAR(36) NOT NULL,
	`point_designator` VARCHAR(128),
	`point_type` ENUM('Vertiport', 'Track', 'Navigational', 'Final', 'Transition', 'Non_ASDS'),
	`speed_type` ENUM('Vertiport', 'Enroute', 'Final', 'Transition', 'Non_ASDS'),
	`latitude` DOUBLE,
	`longitude` DOUBLE,
	`altitude_value` DOUBLE,
	`altitude_reference` CHAR(3),
	`altitude_units` CHAR(1),
	`time_value` CHAR(24),
	`time_format` CHAR(7),
	`speed` FLOAT,
	`units_speed` VARCHAR(15),
	`track` FLOAT,
	`speed_speed_type` ENUM('GROUND', 'AIR'),
	`properties` SET('TOP_OF_CLIMB', 'TOP_OF_DESCENT', 'CROSSOVER_ALTITUDE', 'TRANSITION_ALTITUDE_OR_LEVEL', 'TCP_VERTICAL', 'TCP_SPEED', 'TCP_LATERAL', 'DEPARTURE_RUNWAY_END', 'START_TAKEOFF_ROLL', 'END_LANDING_ROLL', 'WHEELS_OFF', 'WHEELS_ON', 'ENTRY_RESTRICTED_OR_RESERVED_AIRSPACE', 'EXIT_RESTRICTED_OR_RESERVED_AIRSPACE', 'CROSSING_CONSTRAINED_AIRSPACE', 'EXIT_CONSTRAINED_AIRSPACE', 'INITIAL_PREDICTION_POINT', 'END_PREDICTION_POINT', 'HOLD_ENTRY', 'HOLD_EXIT', 'BEGIN_STAY', 'END_STAY', 'START_EXPECT_VECTORS', 'END_EXPECT_VECTORS', 'CONSTRAINT_POINT', 'FIR_BOUBDARY_CROSSING_POINT', 'RUNWAY_THRESHOLD', 'PRESCRIBED_EET_POINT', 'ENTRY_CONSTRAINED_AIRSPACE', 'AIRPORT_REFERENCE_LOCATION', 'WAYPOINT'),
	FOREIGN KEY (`operationalIntentID`, `ovn`) REFERENCES PsuClientOperationalIntentReference(`operationalIntentID`, `ovn`))
	ENGINE = InnoDB;

DROP TABLE IF EXISTS `unt`.`Telemetry`;
CREATE TABLE `unt`.`Telemetry` (
	`operationalIntentID` CHAR(36) NOT NULL,
	`time_measured_value` CHAR(24),
	`time_measured_format` CHAR(7),
	`latitude` DOUBLE,
	`longitude` DOUBLE,
	`accuracy_h` ENUM('HAUnknown', 'HA10NMPlus', 'HA10NM', 'HA4NM', 'HA2NM', 'HA1NM', 'HA05NM', 'HA03NM', 'HA01NM', 'HA005NM', 'HA30m', 'HA10m', 'HA3m', 'HA1m'),
	`accuracy_v` ENUM('VAUnknown', 'VA150mPlus', 'VA150m', 'VA45m', 'VA25m', 'VA10m', 'VA3m', 'VA1m'),
	`extrapolated` BOOLEAN,
	`altitude_value` DOUBLE,
	`altitude_reference` CHAR(3),
	`altitude_units` CHAR(1),
	`speed` FLOAT,
	`units_speed` VARCHAR(15),
	`track` FLOAT,
	`speed_type` ENUM('GROUND', 'AIR'),
	`next_opportunity_value` CHAR(24),
	`next_opportunity_format` CHAR(7),
	`aircraft_registration` VARCHAR(7),
	`active` BOOLEAN,
	UNIQUE (`operationalIntentID`, `time_measured_value`),
	FOREIGN KEY (`operationalIntentID`) REFERENCES PsuClientOperationalIntentReference(`operationalIntentID`))
	ENGINE = InnoDB;

DROP TABLE IF EXISTS `unt`.`CommandUAV`;
CREATE TABLE `unt`.`CommandUAV` (
	`operationalIntentID` CHAR(36) NOT NULL,
	`type` VARCHAR(32) NOT NULL,
	`command_id` INT,
	`aircraft_registration` VARCHAR(7),
	FOREIGN KEY (`operationalIntentID`) REFERENCES PsuClientOperationalIntentReference(`operationalIntentID`))
	ENGINE = InnoDB;
	

DROP TABLE IF EXISTS `unt`.`ConstraintReference`;
CREATE TABLE `unt`.`ConstraintReference` (
	`constraintID` CHAR(36) NOT NULL,
	`manager` VARCHAR(256) NOT NULL,
	`uss_availability` ENUM('Unknown', 'Normal', 'Down'),
	`version` INT NOT NULL,
	`ovn` VARCHAR(128),
	`time_start_value` CHAR(24) NOT NULL,
	`time_start_format` CHAR(7) NOT NULL,
	`time_end_value` CHAR(24) NOT NULL,
	`time_end_format` CHAR(7) NOT NULL,
	`uss_base_url` VARCHAR(256) NOT NULL,
	`type` VARCHAR(256),
	`active` BOOLEAN,
	UNIQUE (`constraintID`, `version`))
	ENGINE = InnoDB;

DROP TABLE IF EXISTS `unt`.`ConstraintDetails`;
CREATE TABLE `unt`.`ConstraintDetails` (
	`constraintID` CHAR(36) NOT NULL,
	`version` INT NOT NULL,
	`volumeID` INT NOT NULL,
	`volume_type` ENUM('CIRCLE', 'POLYGON'),
	`center_longitude` DOUBLE,
	`center_latitude` DOUBLE,
	`radius_value` FLOAT,
	`radius_units` CHAR(1),
	`polygon` POLYGON,
	`altitude_lower_value` DOUBLE,
	`altitude_lower_reference` CHAR(3),
	`altitude_lower_units` CHAR(1),
	`altitude_upper_value` DOUBLE,
	`altitude_upper_reference` CHAR(3),
	`altitude_upper_units` CHAR(1),
	`time_start_value` CHAR(24) NOT NULL,
	`time_start_format` CHAR(7) NOT NULL,
	`time_end_value` CHAR(24) NOT NULL,
	`time_end_format` CHAR(7) NOT NULL,
	FOREIGN KEY (`constraintID`) REFERENCES ConstraintReference(`constraintID`))
	ENGINE = InnoDB;

DROP TABLE IF EXISTS `unt`.`ConstraintSubscriptions`;
CREATE TABLE `unt`.`ConstraintSubscriptions` (
	`constraintID` CHAR(36) NOT NULL,
	`version` INT NOT NULL,
	`subscription_id` CHAR(36) NOT NULL,
	`notification_index` INT NOT NULL,
	FOREIGN KEY (`constraintID`, `version`) REFERENCES ConstraintReference(`constraintID`, `version`))
	ENGINE = InnoDB;

DROP TABLE IF EXISTS `unt`.`RequestLog`;
CREATE TABLE `unt`.`RequestLog` (
	`direction` ENUM('IN', 'OUT'),
	`remote` VARCHAR(15),
	`request_uri` VARCHAR(255),
	`request_method` CHAR(10),
	`request_time` DATETIME(6),
	`request_header` TEXT,
	-- See if JSON data type can be used, it was truncating the outer level
	`request_json` TEXT,
	`response_time` DATETIME(6),
	-- See if JSON data type can be used, it was truncating the outer level
	`response_json` TEXT,
	`invalid` TEXT,
	`status` INT )
	ENGINE = InnoDB;

DROP TABLE IF EXISTS `unt`.`Users`;
CREATE TABLE `unt`.`Users` (
	`username` VARCHAR(16) NOT NULL,
	`password` VARCHAR(16) NOT NULL,
	`entity` CHAR(36) NOT NULL,
	UNIQUE (`username`))
	ENGINE = InnoDB;
INSERT INTO `unt`.`Users` (`username`, `password`, `entity`) VALUES ('test_subscriber', 'test', 'Hermes');

DROP TABLE IF EXISTS `unt`.`Subscriptions`;
CREATE TABLE `unt`.`Subscriptions` (
	`username` VARCHAR(16) NOT NULL,
	`url` VARCHAR(256) NOT NULL,
	`data` ENUM('constraints', 'operationalIntent', 'telemetry'),
	UNIQUE (`username`, `data`),
	FOREIGN KEY (`username`) REFERENCES Users(`username`))
	ENGINE = InnoDB;

DROP TABLE IF EXISTS `unt`.`OperationalIntentReference`;
CREATE TABLE `unt`.`OperationalIntentReference` (
	`operationalIntentID` CHAR(36) NOT NULL,
	`manager` VARCHAR(256) NOT NULL,
	`uss_availability` ENUM('Unknown', 'Normal', 'Down'),
	`version` INT NOT NULL,
	`state` ENUM('Accepted', 'Activated', 'Nonconforming', 'Contingent'),
	`ovn` VARCHAR(128),
	`time_start_value` CHAR(24) NOT NULL,
	`time_start_format` CHAR(7) NOT NULL,
	`time_end_value` CHAR(24) NOT NULL,
	`time_end_format` CHAR(7) NOT NULL,
	`uss_base_url` VARCHAR(256) NOT NULL,
	`subscription_id` CHAR(36) NOT NULL,
	`aircraft_registration` VARCHAR(7),
	`operator_name` CHAR(3),
	`active` BOOLEAN,
	UNIQUE (`operationalIntentID`, `version`))
	ENGINE = InnoDB;

DROP TABLE IF EXISTS `unt`.`Trajectory`;
CREATE TABLE `unt`.`Trajectory` (
	`operationalIntentID` CHAR(36) NOT NULL,
	`version` INT NOT NULL,
	`pointID` INT NOT NULL,
	`point_designator` VARCHAR(128),
	`latitude` DOUBLE,
	`longitude` DOUBLE,
	`altitude_value` DOUBLE,
	`altitude_reference` CHAR(3),
	`altitude_units` CHAR(1),
	`time_value` CHAR(24),
	`time_format` CHAR(7),
	`speed` FLOAT,
	`units_speed` VARCHAR(15),
	`track` FLOAT,
	`speed_type` ENUM('GROUND', 'AIR'),
	`properties` SET('TOP_OF_CLIMB', 'TOP_OF_DESCENT', 'CROSSOVER_ALTITUDE', 'TRANSITION_ALTITUDE_OR_LEVEL', 'TCP_VERTICAL', 'TCP_SPEED', 'TCP_LATERAL', 'DEPARTURE_RUNWAY_END', 'START_TAKEOFF_ROLL', 'END_LANDING_ROLL', 'WHEELS_OFF', 'WHEELS_ON', 'ENTRY_RESTRICTED_OR_RESERVED_AIRSPACE', 'EXIT_RESTRICTED_OR_RESERVED_AIRSPACE', 'CROSSING_CONSTRAINED_AIRSPACE', 'EXIT_CONSTRAINED_AIRSPACE', 'INITIAL_PREDICTION_POINT', 'END_PREDICTION_POINT', 'HOLD_ENTRY', 'HOLD_EXIT', 'BEGIN_STAY', 'END_STAY', 'START_EXPECT_VECTORS', 'END_EXPECT_VECTORS', 'CONSTRAINT_POINT', 'FIR_BOUBDARY_CROSSING_POINT', 'RUNWAY_THRESHOLD', 'PRESCRIBED_EET_POINT', 'ENTRY_CONSTRAINED_AIRSPACE', 'AIRPORT_REFERENCE_LOCATION', 'WAYPOINT'),
	FOREIGN KEY (`operationalIntentID`, `version`) REFERENCES OperationalIntentReference(`operationalIntentID`, `version`))
	ENGINE = InnoDB;

DROP TABLE IF EXISTS `unt`.`OperationalIntentSubscriptions`;
CREATE TABLE `unt`.`OperationalIntentSubscriptions` (
	`operationalIntentID` CHAR(36) NOT NULL,
	`version` INT NOT NULL,
	`subscription_id` CHAR(36) NOT NULL,
	`notification_index` INT NOT NULL,
	FOREIGN KEY (`operationalIntentID`, `version`) REFERENCES OperationalIntentReference(`operationalIntentID`, `version`))
	ENGINE = InnoDB;

