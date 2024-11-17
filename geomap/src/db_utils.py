import mysql.connector
import json
import math
from geopy.distance import geodesic

def connect_to_db():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",  
            password="Mybdpas_1",  
            database="ukraine_map"  
        )
        print("Підключення до бази даних успішне!")
        return db
    except mysql.connector.Error as err:
        print(f"Помилка при підключенні до бази даних: {err}")
        return None

# Генерація квадратів
def generate_squares(lat_min, lat_max, lon_min, lon_max, square_size_km=150):
    squares = []
    lat_step = square_size_km / 111.32
    lon_step = square_size_km / (111.32 * math.cos(math.radians((lat_min + lat_max) / 2)))
    lat = lat_min
    while lat + lat_step <= lat_max:
        lon = lon_min
        while lon + lon_step <= lon_max:
            square = [
                (lat, lon),  # Південно-західна точка
                (lat + lat_step, lon),  # Південно-східна точка
                (lat, lon + lon_step),  # Північно-західна точка
                (lat + lat_step, lon + lon_step)  # Північно-східна точка
            ]
            squares.append(square)
            lon += lon_step
        lat += lat_step
    return squares

# Вставка координат з GeoJSON
def insert_coordinates(db):
    cursor = db.cursor()

    with open('C:\\Users\\Mi\\OneDrive\\Desktop\\dz_folder\\data\\geoBoundaries-UKR-ADM0_simplified.geojson', 'r') as file:
        data = json.load(file)

    for feature in data['features']:
        for coord in feature['geometry']['coordinates'][0]:
            latitude = coord[1]
            longitude = coord[0]
            cursor.execute(
                "INSERT INTO ukraine_border (latitude, longitude) VALUES (%s, %s)",
                (latitude, longitude)
            )

    # Генерація квадратів
    lat_min = 45.0
    lat_max = 55.0
    lon_min = 22.0
    lon_max = 40.0
    squares = generate_squares(lat_min, lat_max, lon_min, lon_max, square_size_km=150)

    # Створення таблиці для зберігання квадратів
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ukraine_squares (
        id INT AUTO_INCREMENT PRIMARY KEY,
        lat1 FLOAT,
        lon1 FLOAT,
        lat2 FLOAT,
        lon2 FLOAT,
        lat3 FLOAT,
        lon3 FLOAT,
        lat4 FLOAT,
        lon4 FLOAT
    )
    """)

    # Вставка координат квадратів
    for square in squares:
        cursor.execute("""
        INSERT INTO ukraine_squares (lat1, lon1, lat2, lon2, lat3, lon3, lat4, lon4)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (square[0][0], square[0][1], square[1][0], square[1][1], square[2][0], square[2][1], square[3][0], square[3][1]))

    db.commit()

    # Створення таблиці для перетинів секторів
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sector_intersections (
        id INT AUTO_INCREMENT PRIMARY KEY,
        point_lat FLOAT,
        point_lon FLOAT,
        azimuth INT,
        intersection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    db.commit()
    cursor.close()


# Функція для обчислення відстані
def distance(point1, point2):
    return geodesic(point1, point2).km

# Функція для обчислення азимуту між двома точками
def calculate_azimuth(center, point):
    lat1, lon1 = map(math.radians, center)  
    lat2, lon2 = map(math.radians, point)   

    # Якщо довготи однакові
    if lon1 == lon2:
        return 90 if lat2 > lat1 else 270

    # Якщо широти однакові
    if lat1 == lat2:
        return 0 if lon2 > lon1 else 180

    # обчислення азимуту
    d_lon = lon2 - lon1
    x = math.sin(d_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(d_lon))

    azimuth = math.degrees(math.atan2(x, y))
    return azimuth if azimuth >= 0 else azimuth + 360

# Функція для перевірки, чи точка знаходиться в секторі
def is_point_in_sector(point, sector_center, azimuth, radius, opening_angle=60):
    # Обчислюємо відстань до точки
    dist = distance(sector_center, point)
    if dist > radius:
        return False  # Якщо точка знаходиться поза радіусом, вона не в секторі

    # Обчислюємо азимут від центру до точки
    angle_to_point = calculate_azimuth(sector_center, point)

    # Різниця між азимутами
    angle_diff = (angle_to_point - azimuth) % 360
    if angle_diff > 180:
        angle_diff = 360 - angle_diff  # Мінімальна різниця

    # Перевірка, чи точка в межах відкриття сектора
    return angle_diff <= opening_angle / 2

# Генерація кінцевих точок секторів
def generate_sector_endpoints(center, radius_km=5):
    # Азимути для секторів
    azimuths = [0, 120, 240]  
    sectors = []

    for azimuth in azimuths:
        # Обчислюємо координати кінцевої точки сектора
        end_lat = center[0] + (radius_km / 111.32) * math.cos(math.radians(azimuth))
        end_lon = center[1] + (radius_km / (111.32 * math.cos(math.radians(center[0])))) * math.sin(math.radians(azimuth))
        sectors.append((end_lat, end_lon, azimuth))
    
    return sectors

# Оновлений check_intersections
def check_intersections(cursor, squares, db):
    sector_radius = 5  # км
    opening_angle = 60  # градуси
    intersections = []  # Місця перетину

    for square in squares:
        for point in square:
            sector_endpoints = generate_sector_endpoints(point, sector_radius)
            
            for end_lat, end_lon, azimuth in sector_endpoints:
                print(f"Перевіряємо сектор з центром {point}, азимутом {azimuth}")
                
                # Перевірка перетинів
                for square_point in square:
                    if is_point_in_sector(square_point, point, azimuth, sector_radius, opening_angle):
                        cursor.execute(
                            "INSERT INTO sector_intersections (point_lat, point_lon, azimuth) VALUES (%s, %s, %s)",
                            (square_point[0], square_point[1], azimuth)
                        )
                        intersections.append((square_point, azimuth))
                        db.commit()

    print(f"Перетини збережено: {len(intersections)} записів.")
    return intersections

# Основна функція для вставки координат і перевірки перетину
def insert_coordinates_and_check_intersections():
    db = connect_to_db()
    if not db:
        return
    cursor = db.cursor()

    # Вставка координат
    insert_coordinates(db)

    # Генерація квадратів для перевірки перетинів
    lat_min = 45.0
    lat_max = 55.0
    lon_min = 22.0
    lon_max = 40.0
    squares = generate_squares(lat_min, lat_max, lon_min, lon_max, square_size_km=150)

    # Перевірка перетинів
    check_intersections(cursor, squares, db)

    cursor.close()
    db.close()

insert_coordinates_and_check_intersections()









