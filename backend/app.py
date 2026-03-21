import json
import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:6060"])

DATA_FILE = os.path.join(os.path.dirname(__file__), "slimes.json")

DEFAULT_PARAMS = {
    "slime": {
        "num_agents": 1000,
        "sensor_angle": 45.0,
        "sensor_distance": 9.0,
        "rotation_angle": 45.0,
        "step_size": 1.0,
        "deposit_amount": 5.0,
        "decay_rate": 0.9,
        "diffuse_rate": 0.5,
        "width": 800,
        "height": 600,
    },
    "boids": {
        "num_boids": 200,
        "max_speed": 4.0,
        "min_speed": 1.0,
        "perception_radius": 60.0,
        "separation_radius": 20.0,
        "alignment_weight": 1.0,
        "cohesion_weight": 1.0,
        "separation_weight": 1.5,
        "width": 800,
        "height": 600,
    },
    "cells": {
        "grid_width": 120,
        "grid_height": 90,
        "birth_min": 3,
        "birth_max": 3,
        "survival_min": 2,
        "survival_max": 3,
        "initial_density": 0.3,
    },
}

VALID_TYPES = set(DEFAULT_PARAMS.keys())


def load_sims():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return json.load(f)


def save_sims(sims):
    with open(DATA_FILE, "w") as f:
        json.dump(sims, f, indent=2)


@app.route("/api/params/defaults", methods=["GET"])
def get_defaults():
    return jsonify(DEFAULT_PARAMS)


@app.route("/api/slimes", methods=["GET"])
def list_sims():
    return jsonify(load_sims())


@app.route("/api/slimes", methods=["POST"])
def create_sim():
    body = request.json or {}
    sim_type = body.get("type", "slime")
    if sim_type not in VALID_TYPES:
        return jsonify({"error": "Invalid type"}), 400
    sims = load_sims()
    defaults = DEFAULT_PARAMS[sim_type]
    sim = {
        "id": str(int(time.time() * 1000)),
        "name": body.get("name", f"New {sim_type.capitalize()}"),
        "author": body.get("author", "Anonymous"),
        "type": sim_type,
        "params": {**defaults, **body.get("params", {})},
        "created_at": int(time.time()),
    }
    sims.append(sim)
    save_sims(sims)
    return jsonify(sim), 201


@app.route("/api/slimes/<sim_id>", methods=["GET"])
def get_sim(sim_id):
    sims = load_sims()
    sim = next((s for s in sims if s["id"] == sim_id), None)
    if not sim:
        return jsonify({"error": "Not found"}), 404
    return jsonify(sim)


@app.route("/api/slimes/<sim_id>", methods=["PUT"])
def update_sim(sim_id):
    body = request.json or {}
    sims = load_sims()
    sim = next((s for s in sims if s["id"] == sim_id), None)
    if not sim:
        return jsonify({"error": "Not found"}), 404
    if "name" in body:
        sim["name"] = body["name"]
    if "author" in body:
        sim["author"] = body["author"]
    if "params" in body:
        defaults = DEFAULT_PARAMS.get(sim.get("type", "slime"), {})
        sim["params"] = {**defaults, **body["params"]}
    save_sims(sims)
    return jsonify(sim)


@app.route("/api/simulate", methods=["POST"])
def simulate():
    body = request.json or {}
    sim_type = body.get("type", "slime")
    defaults = DEFAULT_PARAMS.get(sim_type, {})
    merged = {**defaults, **body.get("params", {}), "type": sim_type}
    # TODO: integrate with simulation backends here
    return jsonify({"status": "ok", "params": merged})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=7070, debug=True)
