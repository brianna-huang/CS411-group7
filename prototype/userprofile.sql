CREATE DATABASE IF NOT EXISTS userprofile;
USE userprofile;
SET GLOBAL sql_mode='';

CREATE TABLE Users(
 user_id INTEGER AUTO_INCREMENT,
 first_name VARCHAR(100),
 last_name VARCHAR(100),
 email VARCHAR(100),
 password VARCHAR(100) NOT NULL,
 PRIMARY KEY (user_id)
 );
 
 INSERT INTO Users (email, password, first_name, last_name) VALUES ('yyan@bu.edu', 'yuyan821', 'Yu', 'Yan');