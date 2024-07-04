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
    return jsonify([{"ingredients": p.ingredients, "name": p.name} for p in pizzas]), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"errors": ["No JSON data received"]}), 400

        price = float(data.get('price'))
        pizza_id = int(data.get('pizza_id'))
        restaurant_id = int(data.get('restaurant_id'))

        if not price or not pizza_id or not restaurant_id:
            return jsonify({"errors": ["All fields required"]}), 400

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza or not restaurant:
            return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404

        new_restaurant_pizza = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)
        db.session.add(new_restaurant_pizza)
        db.session.commit()

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

    except ValueError:
        return jsonify({"errors": ["Validation errors"]}), 400
    except NoResultFound:
        return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 500

if __name__ == "__main__":
    app.run(port=5555, debug=True)
