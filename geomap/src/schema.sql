
CREATE DATABASE IF NOT EXISTS ukraine_map;
USE ukraine_map;

-- Таблиця ukraine_borde
CREATE TABLE IF NOT EXISTS ukraine_border (
    id INT AUTO_INCREMENT PRIMARY KEY,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

-- Таблиця ukraine_squares
CREATE TABLE IF NOT EXISTS ukraine_squares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lat1 FLOAT NOT NULL,
    lon1 FLOAT NOT NULL,
    lat2 FLOAT NOT NULL,
    lon2 FLOAT NOT NULL,
    lat3 FLOAT NOT NULL,
    lon3 FLOAT NOT NULL,
    lat4 FLOAT NOT NULL,
    lon4 FLOAT NOT NULL
);

-- Таблиця sector_intersections
CREATE TABLE IF NOT EXISTS sector_intersections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    point_lat FLOAT NOT NULL,
    point_lon FLOAT NOT NULL,
    azimuth INT NOT NULL,
    intersection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


