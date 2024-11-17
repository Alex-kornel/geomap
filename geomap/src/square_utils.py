import math

# Розрахунок відстані між двома координатами (в км)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Радіус Землі в км
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Функція для розбиття на квадрати
def generate_squares(lat_min, lat_max, lon_min, lon_max, square_size_km=100):
    squares = []
    
    # Визначаємо відстань для одного кроку у градусах
    lat_step = square_size_km / 111.32
    lon_step = square_size_km / (111.32 * math.cos(math.radians((lat_min + lat_max) / 2)))

    # Проходимо по всіх координатах, щоб створити квадрати
    lat = lat_min
    while lat < lat_max:
        lon = lon_min
        while lon < lon_max:
            # Додаємо координати чотирьох вершин квадрата
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
