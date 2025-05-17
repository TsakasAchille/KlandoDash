import polyline

# Lire la polyline depuis le fichier
with open('polyline_data.txt', 'r') as file:
    polyline_str = file.read().strip()

try:
    # Tenter de décoder la polyline
    coords = polyline.decode(polyline_str)
    print(f"Décodage réussi! Nombre de points: {len(coords)}")
    
    # Afficher les premiers et derniers points
    if coords:
        print(f"Premier point: {coords[0]}")
        print(f"Dernier point: {coords[-1]}")
    
    # Vérifier si les coordonnées sont valides
    valid = all(len(point) == 2 and isinstance(point[0], float) and isinstance(point[1], float) for point in coords)
    print(f"Toutes les coordonnées sont valides: {valid}")
    
    # Afficher les plages de latitude/longitude pour vérifier la zone géographique
    if coords:
        lats = [p[0] for p in coords]
        lngs = [p[1] for p in coords]
        print(f"Latitude min: {min(lats)}, max: {max(lats)}")
        print(f"Longitude min: {min(lngs)}, max: {max(lngs)}")
        
except Exception as e:
    print(f"Erreur lors du décodage: {e}")
