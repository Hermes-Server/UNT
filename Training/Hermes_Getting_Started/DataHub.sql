
DROP TABLE IF EXISTS `myBusiness`.`AnimalKingdom`;
CREATE TABLE `myBusiness`.`AnimalKingdom` (
	`Country` CHAR(36) NOT NULL,
	`Animal` CHAR(36),
	UNIQUE (`Country`))
	ENGINE = InnoDB;