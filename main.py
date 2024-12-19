from flask import Flask, jsonify, request
from functools import wraps
import json

app = Flask(__name__)

catalog = {
    1: {"name": "Apple", "price": 0.5, "color": "Red"},
    2: {"name": "Banana", "price": 0.3, "color": "Yellow"},
    3: {"name": "Grapes", "price": 2.0, "color": "Purple"}
}

users = {
    "admin": "password123",
    "user": "userpass"
}

def load_users_from_file():
    user_file = "users.txt"
    loaded_users = {}
    try:
        with open(user_file, "r") as file:
            for line in file:
                username, password = line.strip().split(":")
                loaded_users[username] = password
    except FileNotFoundError:
        pass
    return loaded_users

users.update(load_users_from_file())

def check_auth(username, password):
    return username in users and users[username] == password

def authenticate():
    return jsonify({"Помилка": "Потрібна автентифікація."}), 401, {
        'WWW-Authenticate': 'Basic realm="Login Required"'
    }

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def save_catalog_to_file():
    with open('catalog.json', 'w') as file:
        json.dump(catalog, file)

@app.route('/items', methods=['GET', 'POST'])
@requires_auth
def handle_items():
    if request.method == 'GET':
        return jsonify(catalog), 200
    elif request.method == 'POST':
        new_item = request.get_json()
        if not new_item or not all(k in new_item for k in ("name", "price", "color")):
            return jsonify({"Помилка": "Не знайдено."}), 400
        new_id = max(catalog.keys(), default=0) + 1
        catalog[new_id] = new_item
        save_catalog_to_file()
        return jsonify({"id": new_id, "item": new_item}), 201

@app.route('/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@requires_auth
def handle_item(item_id):
    if item_id not in catalog:
        return jsonify({"Помилка": "Не знайдено."}), 404

    if request.method == 'GET':
        return jsonify(catalog[item_id]), 200
    elif request.method == 'PUT':
        updated_item = request.get_json()
        if not updated_item or not all(k in updated_item for k in ("name", "price", "color")):
            return jsonify({"Помилка": "Не знайдено."}), 400
        catalog[item_id] = updated_item
        save_catalog_to_file()
        return jsonify({"id": item_id, "item": updated_item}), 200
    elif request.method == 'DELETE':
        deleted_item = catalog.pop(item_id)
        save_catalog_to_file()
        return jsonify({"id": item_id, "item": deleted_item}), 200

if __name__ == '__main__':
    app.run(debug=True)