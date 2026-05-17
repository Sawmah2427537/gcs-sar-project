from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "SAR GCS backend is running"
    })

@app.route("/plan", methods=["POST"])
def plan():
    data = request.get_json()

    sar_points = data.get("sar_points", [])
    uavs = data.get("uavs", [])

    if not uavs:
        return jsonify({
            "error": "No UAV data provided"
        }), 400

    missions = []

    for index, uav in enumerate(uavs):
        assigned_points = sar_points[index::len(uavs)]

        missions.append({
            "uav_id": uav["id"],
            "path": assigned_points,
            "eta": len(assigned_points) * 30
        })

    return jsonify({
        "missions": missions
    })

if __name__ == "__main__":
    app.run(debug=True)