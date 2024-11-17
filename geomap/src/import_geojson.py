import json
import mysql.connector

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mybdpas_1",  
        database="ukraine_map"
    )

def insert_coordinates(coordinates):
    db = connect_to_db()
    cursor = db.cursor()

    # Запиту для вставки координат у таблицю
    cursor.executemany("INSERT INTO ukraine_border (latitude, longitude) VALUES (%s, %s)", coordinates)

    db.commit()
    cursor.close()
    db.close()

def load_geojson(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    coordinates = []
    
    import json

def load_geojson(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    coordinates = []
    
    for feature in data["features"]:
        if feature["geometry"]["type"] == "Polygon":
            for coord_pair in feature["geometry"]["coordinates"][0]:
                lat, lon = round(coord_pair[1], 5), round(coord_pair[0], 5)  # округляємо до 5 знаків
                
                # Фільтрація координат 
                if 44 < lat < 50 and 30 < lon < 40:  # обмеження по координатах
                    coordinates.append((lat, lon))  # latitude, longitude

    return coordinates


if __name__ == "__main__":
    file_path = "C:\\Users\\Mi\\OneDrive\\Desktop\\dz_folder\\data\\geoBoundaries-UKR-ADM0_simplified.geojson"  
    coordinates = load_geojson(file_path)
    insert_coordinates(coordinates)
    print(f"Inserted {len(coordinates)} coordinates into the database.")

