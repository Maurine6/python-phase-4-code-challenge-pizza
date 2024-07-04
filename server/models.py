from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Float, String, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    address = Column(String)

    # Relationship with RestaurantPizza
    restaurant_pizzas = relationship("RestaurantPizza", back_populates="restaurant")

    # Serialization rules
    serialize_rules = (
        '-password',
        {'name': {'exclude': True}},
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'restaurant_pizzas': [rp.to_dict() for rp in self.restaurant_pizzas]
        }

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ingredients = Column(String)

    # Relationship with RestaurantPizza
    restaurant_pizzas = relationship("RestaurantPizza", back_populates="pizza")

    # Serialization rules
    serialize_rules = (
        '-password',
        {'name': {'exclude': True}},
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = Column(Integer, primary_key=True)
    price = Column(Float, nullable=False)

    # Relationships
    pizza_id = Column(Integer, ForeignKey('pizzas.id'))
    pizza = relationship("Pizza", back_populates="restaurant_pizzas")
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    restaurant = relationship("Restaurant", back_populates="restaurant_pizzas")

    # Validation
    @validates('price')
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30.")
        return price
        

    # Serialization rules
    serialize_rules = (
        '-password',
        {'name': {'exclude': True}},
    )

    def to_dict(self):
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'restaurant': self.restaurant.to_dict() if self.restaurant else None,
            'pizza_id': self.pizza_id,
            'pizza': self.pizza.to_dict() if self.pizza else None,
            'price': self.price
        }

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
