"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
jackson_family = FamilyStructure("Jackson")

initial_members = [
    {"first_name": "John", "age": 33, "lucky_numbers": [7, 13, 22]},
    {"first_name": "Jane", "age": 35, "lucky_numbers": [10, 14, 3]},
    {"first_name": "Jimmy", "age": 5, "lucky_numbers": [1]}
]

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/members', methods=['GET'])
def handle_hello():
    members = jackson_family.get_all_members()
    response_body = {
        "hello": "world",
        "family": members
    }
    return jsonify(response_body), 200

@app.route('/members/<int:member_id>', methods=['GET'])
def get_one_member(member_id):
    member = jackson_family.get_member(member_id)

    if member:
        response = {
            "id": member["id"],
            "first_name": member["first_name"],
            "age": member["age"],
            "lucky_numbers": member["lucky_numbers"]
        }
        return jsonify(response), 200
    else:
        return jsonify({"error": "Miembro no encontrado"}), 404

    return jsonify(response), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)


@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_family_member(member_id):
    if jackson_family.delete_member(member_id):
        return jsonify({"done": True}), 200
    else:
        return jsonify({"error": "Miembro no encontrado"}), 404


@app.route('/members', methods=['POST'])
def add_family_member():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400
    required_fields = ["first_name", "age", "lucky_numbers"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Falta el campo: {field}"}), 400
    new_member = {
        "first_name": data["first_name"],
        "age": data["age"],
        "lucky_numbers": data["lucky_numbers"]
    }
    if "id" in data:
        new_member["id"] = data["id"]
    jackson_family.add_member(new_member)
    return jsonify(), 200