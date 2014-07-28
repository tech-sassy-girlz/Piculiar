CREATE DATABASE IF NOT EXISTS pic_flick;

use `pic_flick`;

CREATE TABLE IF NOT EXISTS `pic_flick`.`users`
(
	`id` int NOT NULL AUTO_INCREMENT,
	`name` varchar(45),
	`email` varchar(45),
	`pwd` varchar(100),
	PRIMARY KEY (`id`)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS `pic_flick`.`images`
(
	`id` int NOT NULL AUTO_INCREMENT,
	`user_id` int,
	`file_name` varchar(45),
	`year_created` varchar(45),
	`month_created` varchar(45),
	PRIMARY KEY (`id`), 
	INDEX `user_idx` (`user_id`),
	FOREIGN KEY (`user_id`) REFERENCES `pic_flick`.`users`(`id`)
) ENGINE=INNODB;
