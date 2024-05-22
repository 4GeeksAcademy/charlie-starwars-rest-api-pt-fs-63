import os
import sys
import enum
from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FavoriteEnum(enum.Enum):
    PLANET = 'planet'
    CHARACTER = 'character'

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(String(100), nullable=False, unique=True)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Character(db.Model):
    __tablename__ = 'character'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(50), nullable=False)
    surname = db.Column(String(100), nullable=False)
    is_favorite = db.Column(Boolean, default=False)
    gender = db.Column(String(10))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "gender": self.gender
        }

class Planet(db.Model):
    __tablename__ = 'planet'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    is_favorite = db.Column(Boolean, default=False)
    climate = db.Column(String(50))
    population = db.Column(Integer)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population
        }

class Favorites(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('user.id'))
    character_id = db.Column(Integer, ForeignKey('character.id'))
    planet_id = db.Column(Integer, ForeignKey('planet.id'))
    favorite_enum = db.Column(Enum(FavoriteEnum))

    user = relationship(User)
    character = relationship(Character)
    planet = relationship(Planet)

    pass