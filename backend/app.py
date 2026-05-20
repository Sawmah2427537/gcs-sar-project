from flask import Flask, request, jsonify
from flask_cors import CORS
from planner.planner import plan_mission

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

    result = plan_mission(sar_points, uavs)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)