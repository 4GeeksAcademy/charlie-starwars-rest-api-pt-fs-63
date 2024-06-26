"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorites, FavoriteEnum
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    if people is None:
        return jsonify({"Error": "Something went wrong"}), 404
    return jsonify([person.serialize() for person in people]),200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Character.query.get(people_id)
    if person is None:
        return jsonify({"Error": "Person not found"}), 404
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    if planets is None:
        return jsonify({"Error": "Something went wrong"}), 404
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize())

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    if users is None:
        return jsonify({"Error": "Something went wrong"}), 404
    return jsonify([user.serialize() for user in users])

@app.route('/users/favorites/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    favorites_list = []
    for fav in favorites:
        if fav.favorite_enum == FavoriteEnum.PLANET:
            planet = Planet.query.get(fav.planet_id)
            favorites_list.append({"type": "planet", "data": planet.serialize()})
        elif fav.favorite_enum == FavoriteEnum.CHARACTER:
            character = Character.query.get(fav.character_id)
            favorites_list.append({"type": "character", "data": character.serialize()})
    return jsonify(favorites_list)

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    new_favorite = Favorites(user_id=user_id, planet_id=planet_id, favorite_enum=FavoriteEnum.PLANET)
    print(new_favorite)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"message": "Favorite planet added successfully"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.json.get('user_id')
    new_favorite = Favorites(user_id=user_id, character_id=people_id, favorite_enum=FavoriteEnum.CHARACTER)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"message": "Favorite person added successfully"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id, favorite_enum=FavoriteEnum.PLANET).first()
    if not favorite:
        return jsonify({"error": "Favorite planet not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite planet deleted successfully"})

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = request.json.get('user_id')
    favorite = Favorites.query.filter_by(user_id=user_id, character_id=people_id, favorite_enum=FavoriteEnum.CHARACTER).first()
    if not favorite:
        return jsonify({"error": "Favorite person not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite person deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
