import folium
import mysql.connector
from square_utils import generate_squares
from import_geojson import load_geojson, insert_coordinates

# Підключення до MySQL
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mybdpas_1",  
        database="ukraine_map"
    )

# Завантаження координат з БД та створення карти
def display_map_with_limit(max_markers=1000):
    db = connect_to_db()
    cursor = db.cursor()

    cursor.execute("SELECT latitude, longitude FROM ukraine_border LIMIT %s", (max_markers,))
    coordinates = cursor.fetchall()

    # Створення карти
    m = folium.Map(location=[48.5, 31.0], zoom_start=6)

    # Додавання координат як маркери на карту
    for coord in coordinates:
        folium.Marker([coord[0], coord[1]]).add_to(m)

    # Додавання квадратів на карту
    cursor.execute("SELECT lat1, lon1, lat2, lon2, lat3, lon3, lat4, lon4 FROM ukraine_squares LIMIT 48")
    squares = cursor.fetchall()

    for square in squares:
        # Перевірка координат
        if all(isinstance(coord, (int, float)) for coord in square):
            folium.Polygon(
                locations=[(square[0], square[1]), (square[2], square[3]), (square[4], square[5]), (square[6], square[7])],
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.3
            ).add_to(m)

    # Збереження карти
    m.save("limited_map.html")
    
    

    cursor.close()
    db.close()

# Завантаження координат з GeoJSON
file_path = "C:\\Users\\Mi\\OneDrive\\Desktop\\dz_folder\\data\\geoBoundaries-UKR-ADM0_simplified.geojson"  
coordinates = load_geojson(file_path)
insert_coordinates(coordinates)  # Вставка координат у базу

print(f"Inserted {len(coordinates)} coordinates into the database.")

# Викликаємо функцію для відображення карти з лімітом маркерів
display_map_with_limit(max_markers=5727)




