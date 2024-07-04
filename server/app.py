from models import db, Restaurant, RestaurantPizza, Pizza
from sqlalchemy.orm import Session
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from sqlalchemy.exc import NoResultFound
import os
import logging

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False


migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)
#api.add_resource(GetRestaurant, '/restaurants/<int:id>')

@app.route('/restaurants', methods=['GET'])
def restaurants():
    if request.method == 'GET':
        restaurants = Restaurant.query.all()
        return jsonify([{ "id":r.id, "address": r.address, "name": r.name} for r in restaurants]), 200
        


@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return restaurant.to_dict(), 200
    else:
        return jsonify({'error': 'Restaurant not found'}), 404

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return jsonify({'error': 'Restaurant not found'}), 404    


@app.route('/pizzas', methods=['GET'])
def pizzas():
    pizzas = Pizza.query.all()
    return jsonify([{"id":p.id, "ingredients": p.ingredients, "name": p.name} for p in pizzas]), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    try:
        data = request.get_json()  # Safely get JSON data

        price = float(data.get('price'))  # Convert to float explicitly
        pizza_id = int(data.get('pizza_id'))  # Convert to int explicitly
        restaurant_id = int(data.get('restaurant_id'))  # Convert to int explicitly

        # Validate input
        if not price or not pizza_id or not restaurant_id:
            return jsonify({"errors": ["validation errors"]}), 400

        # Fetch existing Pizza and Restaurant
        try:
            pizza = Pizza.query.get(pizza_id)
            restaurant = Restaurant.query.get(restaurant_id)
        except NoResultFound:
            return jsonify({"errors": ["validation errors"]}), 404

        # Create new RestaurantPizza
        new_restaurant_pizza = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        # Construct and return response
        response_data = {
            "id": new_restaurant_pizza.id,
            "price": price,
            "pizza_id": pizza_id,
            "restaurant_id": restaurant_id,
            "pizza": {
                "id": pizza.id,
                "ingredients": pizza.ingredients,
                "name": pizza.name
            },
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
        }
        return jsonify(response_data), 201

    except ValueError:  # Catch specific exceptions like ValueError for type conversion failures
        return jsonify({"errors": ["validation errors"]}), 400
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 500

if __name__ == "__main__":
    app.run(port=5555, debug=True)
