import math

def point_side(line_start, line_end, point):
    ax = line_start["lon"]
    ay = line_start["lat"]
    bx = line_end["lon"]
    by = line_end["lat"]
    px = point["lon"]
    py = point["lat"]

    return (bx - ax) * (py - ay) - (by - ay) * (px - ax)

def haversine_distance(p1, p2):
    r = 6371000

    lat1 = math.radians(p1["lat"])
    lon1 = math.radians(p1["lon"])
    lat2 = math.radians(p2["lat"])
    lon2 = math.radians(p2["lon"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c

def compute_eta(path, speed, base=None):
    if not path:
        return 0

    total_distance = 0

    if base:
        total_distance += haversine_distance(base, path[0])

    for i in range(len(path) - 1):
        total_distance += haversine_distance(path[i], path[i + 1])

    flight_time = total_distance / speed
    hover_time = sum(point.get("hover_time", 30) for point in path)

    return round(flight_time + hover_time, 1)

def nearest_neighbor(points, base=None):
    if not points:
        return []

    unvisited = points[:]
    ordered = []

    current = base if base else unvisited.pop(0)

    while unvisited:
        nearest = min(
            unvisited,
            key=lambda point: haversine_distance(current, point)
        )

        ordered.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    return ordered

def plan_mission(sar_points, uavs):
    if not uavs:
        return {"error": "No UAV data provided"}

    line_start = {"lat": 25.0330, "lon": 121.50}
    line_end = {"lat": 25.0330, "lon": 121.60}

    left_points = []
    right_points = []

    for point in sar_points:
        side = point_side(line_start, line_end, point)

        if side > 0:
            point["side"] = "left"
            left_points.append(point)
        else:
            point["side"] = "right"
            right_points.append(point)

    missions = []
    
    left_path = nearest_neighbor(left_points, uavs[0].get("base"))
    right_path = nearest_neighbor(right_points, uavs[1].get("base"))

    if len(uavs) >= 1:
        missions.append({
            "uav_id": uavs[0]["id"],
            "path": left_path,
            "eta": compute_eta(left_path, uavs[0].get("speed", 8), uavs[0].get("base"))
        })

    if len(uavs) >= 2:
        missions.append({
            "uav_id": uavs[1]["id"],
            "path": right_path,
            "eta": compute_eta(right_path, uavs[1].get("speed", 8), uavs[1].get("base"))
        })

    return {
        "missions": missions,
        "explain_info": {
            "line_start": line_start,
            "line_end": line_end,
            "left_count": len(left_points),
            "right_count": len(right_points)
        }
    }