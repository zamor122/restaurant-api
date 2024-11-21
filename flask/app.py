import os
from flask import Flask, jsonify
from services import RestaurantHours

app = Flask(__name__)

@app.route("/")
def home():
    response = {
        "message": "Welcome to the API!",
        "status": "success"
    }
    return jsonify(response), 200

@app.route("/restaurants/search", methods=["GET"])
@app.route("/restaurants/search/<datetime_str>", methods=["GET"])
def search_open_restaurants(datetime_str=None):
    try:
        rh = RestaurantHours()
        open_restaurants = rh.get_open_restaurants(datetime_str)
        if open_restaurants:
            response = {
                "message": "Data found",
                "status": "success",
                "restaurants": open_restaurants
            }
            return jsonify(response), 200
        else:
            response = {
                "message": "No data found",
                "status": "failure",
                "restaurants": []
            }
            return jsonify(response), 404
    except Exception as e:
        response = {
            "message": f"An error occurred: {str(e)}",
            "status": "error"
        }
        return jsonify(response), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
