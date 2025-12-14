import json
from geopy.distance import geodesic

with open("C:/Users/oosth/OneDrive/Documenten/SubwayBuilder/saves/COL/COL1.json") as f:
    save = json.load(f)

seen_segments = set()
total_km = 0

for track in save["data"]["tracks"]:
    coords = track["coords"]
    for i in range(len(coords)-1):
        p1, p2 = tuple(coords[i]), tuple(coords[i+1])
        segment = tuple(sorted([p1, p2]))
        if segment not in seen_segments:
            total_km += geodesic(p1[::-1], p2[::-1]).km / 2
            seen_segments.add(segment)

print(f"Total network length: {total_km:.1f} km")
