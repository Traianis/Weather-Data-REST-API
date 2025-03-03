import os
from flask import Flask
from flask import request, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import select
from sqlalchemy import and_
from os import getenv
import time

from datetime import datetime

DB_name = "temperatures"
host = "postgres"
user = getenv('POSTGRES_USER')
password = getenv('POSTGRES_PASSWORD')
port = 5432

URL = f"postgresql://{user}:{password}@{host}:{port}/{DB_name}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

engine = create_engine(URL)

db = SQLAlchemy(app)

class Countries(db.Model):
    __tablename__ = 'Tari'
    id = db.Column(db.Integer, nullable = False, primary_key=True, autoincrement=True)
    nume_tara = db.Column(db.String(100), nullable=False, unique=True)
    latitudine = db.Column(db.Double, nullable=False)
    longitudine = db.Column(db.Double, nullable=False)

    def as_dict(self):
        response_def = {
            'nume_tara': 'nume',
            'latitudine': 'lat',
            'longitudine': 'lon'
        }
        return {
            response_def.get(c.name, c.name): getattr(self, c.name)
            for c in self.__table__.columns
        }

class Cities(db.Model):
    __tablename__ = 'Orase'
    id = db.Column(db.Integer, nullable = False, primary_key=True, autoincrement=True)
    id_tara = db.Column(db.Integer, nullable=False)
    nume_oras = db.Column(db.String(100), nullable=False)
    latitudine = db.Column(db.Double, nullable=False)
    longitudine = db.Column(db.Double, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('id_tara', 'nume_oras', name='unique_id_tara_nume_oras'),
    )

    def as_dict(self):
        response_def = {
            'id_tara': 'idTara',
            'nume_oras': 'nume',
            'latitudine': 'lat',
            'longitudine': 'lon'
        }
        return {
            response_def.get(c.name, c.name): getattr(self, c.name)
            for c in self.__table__.columns
        }
    
class Temperatures(db.Model):
    __tablename__ = 'Temperaturi'
    id = db.Column(db.Integer, nullable = False, primary_key=True, autoincrement=True)
    valoare = db.Column(db.Double, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    id_oras = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('id_oras', 'timestamp', name='unique_id_oras_timestamp'),
    )

    def as_dict(self):
        response_def = {'id': 'id', 'valoare': 'valoare', 'timestamp': 'timestamp'}
        return {
            response_def.get(c.name, c.name): getattr(self, c.name)
            for c in self.__table__.columns
            if c.name in response_def
        }

# ----------------------------------------------------------------------------------------------------------------------------
# Countries API
@app.route('/api/countries', methods=['POST'])
def add_country():
    if not request.json or not 'nume' in request.json or not 'lat' in request.json or not 'lon' in request.json:
        return jsonify({"status": False, "error": "Data is missing"}), 400
    
    nume = request.json['nume']
    if (isinstance(nume, str) == False):
        return jsonify({"status": False, "error": "Country name is not a string"}), 400

    list_countries = db.session.execute(select(Countries.nume_tara).where(Countries.nume_tara == nume)).first()
    if list_countries:
        return jsonify({"status": False, "error": "Country already exists"}), 409
    
    if (isinstance(request.json['lat'], str) == True):
        return jsonify({"status": False, "error": "Latitude is not a number"}), 400
    if (isinstance(request.json['lon'], str) == True):
        return jsonify({"status": False, "error": "Longitude is not a number"}), 400
    
    country = Countries(
        nume_tara = nume,
        latitudine = request.json['lat'],
        longitudine = request.json['lon']
    )
    db.session.add(country)
    db.session.commit()

    return jsonify ({"id": country.id}), 201


@app.route('/api/countries', methods=['GET'])
def get_countries():
    return jsonify([c.as_dict() for c in Countries.query.all()]), 200

@app.route('/api/countries/<int:id>', methods=['PUT'])
def update_country(id):
    country = db.session.query(Countries).filter(Countries.id == id).first()
    if not country:
        return jsonify({"status": False, "error": "Country not found"}), 404
    
    if not request.json or not 'nume' in request.json or not 'lat' in request.json or not 'lon' in request.json:
        return jsonify({"status": False, "error": "Data is missing"}), 400

    already_exists = db.session.execute(select(Countries.id).where(and_(Countries.id != id, Countries.nume_tara == request.json['nume']))).first()
    if already_exists:
        return jsonify({"status": False, "error": "Country already exists"}), 409
    
    if(isinstance(request.json['lat'], str) == True):
        return jsonify({"status": False, "error": "Latitude is not a number"}), 400
    if(isinstance(request.json['lon'], str) == True):
        return jsonify({"status": False, "error": "Longitude is not a number"}), 400
    if(isinstance(request.json['nume'], str) == False):
        return jsonify({"status": False, "error": "Country name is not a string"}), 400
    
    country.nume_tara = request.json['nume']
    country.latitudine = request.json['lat']
    country.longitudine = request.json['lon']

    db.session.commit()
    return jsonify(), 200

@app.route('/api/countries/<int:id>', methods=['DELETE'])
def delete_country(id):
    if id == 0:
        return jsonify({"status": False, "error": "Country with id 0 cannot be deleted"}), 400

    country = db.session.query(Countries).filter(Countries.id == id).first()
    if not country:
        return jsonify({"status": False, "error": "Country not found"}), 404
    
    db.session.delete(country)
    db.session.commit()
    return jsonify(), 200

# ----------------------------------------------------------------------------------------------------------------------------
# Cities API
@app.route('/api/cities', methods=['POST'])
def add_city():
    if not request.json or not 'idTara' in request.json or not 'nume' in request.json or not 'lat' in request.json or not 'lon' in request.json:
        return jsonify({"status": False, "error": "Data is missing"}), 400
    
    nume = request.json['nume']
    if (isinstance(nume, str) == False):
        return jsonify({"status": False, "error": "City name is not a string"}), 400

    list_cities = db.session.execute(select(Cities.nume_oras).where(Cities.nume_oras == nume)).first()
    if list_cities:
        return jsonify({"status": False, "error": "City already exists"}),409
    
    idTara = request.json['idTara']
    if (isinstance(idTara, str) == True):
        return jsonify({"status": False, "error": "Country id is not a number"}), 400

    list_countries = db.session.execute(select(Countries.id).where(Countries.id == idTara)).first()
    if not list_countries:
        return jsonify({"status": False, "error": "Country not found"}),404
    
    if (isinstance(request.json['lat'], str) == True):
        return jsonify({"status": False, "error": "Latitude is not a number"}), 400
    if (isinstance(request.json['lon'], str) == True):
        return jsonify({"status": False, "error": "Longitude is not a number"}), 400
    
    city = Cities(
        id_tara = idTara,
        nume_oras = nume,
        latitudine = request.json['lat'],
        longitudine = request.json['lon']
    )
    db.session.add(city)
    db.session.commit()

    return jsonify ({"id": city.id}), 201

@app.route('/api/cities', methods=['GET'])
def get_cities():
    return jsonify([c.as_dict() for c in Cities.query.all()]), 200

@app.route('/api/cities/country/<int:id_Tara>', methods=['GET'])
def get_cities_by_country(id_Tara):
    cities = db.session.query(Cities).filter(Cities.id_tara == id_Tara).all()
    return jsonify([c.as_dict() for c in cities]), 200

@app.route('/api/cities/<int:id>', methods=['PUT'])
def update_city(id):
    city = db.session.query(Cities).filter(Cities.id == id).first()
    if not city:
        return jsonify({"status": False, "error": "City not found"}), 404
    
    if not request.json or not 'idTara' in request.json or not 'nume' in request.json or not 'lat' in request.json or not 'lon' in request.json:
        return jsonify({"status": False, "error": "Data is missing"}), 400
    
    if(isinstance(request.json['idTara'], str) == True):
        return jsonify({"status": False, "error": "Country id is not a number"}), 400
    if(isinstance(request.json['nume'], str) == False):
        return jsonify({"status": False, "error": "City name is not a string"}), 400
    
    already_exists = db.session.execute(select(Cities.id).where(and_(
            Cities.id != id,
            Cities.id_tara == request.json['idTara'],
            Cities.nume_oras == request.json['nume']
        ))).first()
    if already_exists:
        return jsonify({"status": False, "error": "(id_tara, nume_oras) already exist", "data": request.json}), 409
    
    if(isinstance(request.json['lat'], str) == True):
        return jsonify({"status": False, "error": "Latitude is not a number"}), 400
    if(isinstance(request.json['lon'], str) == True):
        return jsonify({"status": False, "error": "Longitude is not a number"}), 400

    city.id_tara = int(request.json['idTara'])
    city.nume_oras = request.json['nume']
    city.latitudine = request.json['lat']
    city.longitudine = request.json['lon']

    db.session.commit()
    return jsonify(), 200

@app.route('/api/cities/<int:id>', methods=['DELETE'])
def delete_city(id):
    if id == 0:
        return jsonify({"status": False, "error": "City with id 0 cannot be deleted"}), 400

    city = db.session.query(Cities).filter(Cities.id == id).first()
    if not city:
        return jsonify({"status": False, "error": "City not found"}), 404
    
    db.session.delete(city)
    db.session.commit()
    return jsonify(), 200


# ----------------------------------------------------------------------------------------------------------------------------
# Temperatures API
@app.route('/api/temperatures', methods=['POST'])
def add_temperature():
    if not request.json or not 'idOras' in request.json or not 'valoare' in request.json:
        return jsonify({"status": False, "error": "Data is missing" , "data" : request.json}), 400
    
    id_oras = int(request.json['idOras'])
    if (isinstance(id_oras, str) == True):
        return jsonify({"status": False, "error": "City id is not a number"}), 400

    list_cities = db.session.execute(select(Cities.id).where(Cities.id == id_oras)).first()
    if not list_cities:
        return jsonify({"status": False, "error": "City not found"}),404

    if (isinstance(request.json['valoare'], str) == True):
        return jsonify({"status": False, "error": "Temperature is not a number"}),400
    
    curr_timestamp = datetime.now().timestamp()

    timestamp = datetime.fromtimestamp(curr_timestamp)

    if db.session.query(Temperatures).filter(and_(Temperatures.id_oras == id_oras, Temperatures.timestamp == timestamp)).first():
        return jsonify({"status": False, "error": "Temperature already exists"}), 409

    temperature = Temperatures(
        id_oras = id_oras,
        valoare = float(request.json['valoare']),
        timestamp = timestamp
    )
    db.session.add(temperature)
    db.session.commit()

    return jsonify ({"id": temperature.id}), 201

def is_valid_date(date_string, date_format='%Y-%m-%d'):
    try:
        return datetime.strptime(date_string, date_format)
    except ValueError:
        return None
    
@app.route('/api/temperatures', methods=['GET'])
def get_temperatures():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    from_date = request.args.get('from')
    until = request.args.get('until')

    try:
        if lat:
            lat = float(lat)
        if lon:
            lon = float(lon)
    except ValueError:
        return jsonify({"status": False, "error": "Latitude or Longitude is not a number"}), 400

    query = Temperatures.query.join(Cities, Cities.id == Temperatures.id_oras)

    if lat:
        query = query.filter(Cities.latitudine == float(lat))

    if lon:
        query = query.filter(Cities.longitudine == float(lon))

    if from_date:
        valid_time = is_valid_date(from_date)
        if not valid_time:
            return jsonify({"status": False, "error": "Invalid date format"}), 400
        
        query = query.filter(Temperatures.timestamp >= valid_time)

    if until:
        valid_time = is_valid_date(until)
        if not valid_time:
            return jsonify({"status": False, "error": "Invalid date format"}), 400
        query = query.filter(Temperatures.timestamp <= valid_time)

    list_temperatures = query.all()
    
    return jsonify([c.as_dict() for c in list_temperatures]), 200

@app.route('/api/temperatures/cities/<int:id_oras>', methods=['GET'])
def get_temperatures_of_cities_by_date(id_oras):
    from_date = request.args.get('from')
    until = request.args.get('until')

    query = db.session.query(Temperatures).filter(Temperatures.id_oras == id_oras)

    if from_date:
        valid_time = is_valid_date(from_date)
        if not valid_time:
            return jsonify({"status": False, "error": "Invalid date format"}), 400
        query = query.filter(Temperatures.timestamp >= valid_time)
    if until:
        valid_time = is_valid_date(until)
        if not valid_time:
            return jsonify({"status": False, "error": "Invalid date format"}), 400
        query = query.filter(Temperatures.timestamp <= valid_time)

    list_temperatures = query.all()

    return jsonify([c.as_dict() for c in list_temperatures]), 200

@app.route('/api/temperatures/countries/<int:id_tara>', methods=['GET'])
def get_temperatures_of_countries_by_date(id_tara):
    from_date = request.args.get('from')
    until = request.args.get('until')

    query = db.session.query(Temperatures).join(Cities, Cities.id == Temperatures.id_oras).filter(Cities.id_tara == id_tara)

    if from_date:
        valid_time = is_valid_date(from_date)
        if not valid_time:
            return jsonify({"status": False, "error": "Invalid date format"}), 400
        query = query.filter(Temperatures.timestamp >= valid_time)
    if until:
        valid_time = is_valid_date(until)
        if not valid_time:
            return jsonify({"status": False, "error": "Invalid date format"}), 400
        query = query.filter(Temperatures.timestamp <= valid_time)

    list_temperatures = query.all()

    return jsonify([c.as_dict() for c in list_temperatures]), 200

@app.route('/api/temperatures/<int:id>', methods=['PUT'])
def update_temperature(id):
    if id == 0:
        return jsonify({"status": False, "error": "Temperature with id 0 cannot be updated"}), 400

    temperature = db.session.query(Temperatures).filter(Temperatures.id == id).first()
    if not temperature:
        return jsonify({"status": False, "error": "Temperature not found"}), 404
    
    if not request.json or not 'idOras' in request.json or not 'valoare' in request.json:
        return jsonify({"status": False, "error": "Data is missing"}), 400
    
    if (isinstance(request.json['idOras'],str) == True):
        return jsonify({"status": False, "error": "City id is not a number"}), 400
    if (isinstance(request.json['valoare'], str) == True):
        return jsonify({"status": False, "error": "Temperature is not a number"}), 400
    
    temperature.id_oras = request.json['idOras']
    temperature.valoare = request.json['valoare']

    curr_timestamp = datetime.now().timestamp()

    temperature.timestamp = datetime.fromtimestamp(curr_timestamp)

    db.session.commit()
    return jsonify(), 200

@app.route('/api/temperatures/<int:id>', methods=['DELETE'])
def delete_temperature(id):
    if id == 0:
        return jsonify({"status": False, "error": "Temperature with id 0 cannot be deleted"}), 400

    temperature = db.session.query(Temperatures).filter(Temperatures.id == id).first()
    if not temperature:
        
        return jsonify({"status": False, "error": "Temperature not found"}), 404
    
    db.session.delete(temperature)
    db.session.commit()
    return jsonify(), 200


def ensure_database_exists():
    retries = 5
    # Try to connect to the database server
    while retries > 0:
        try:
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            if not database_exists(engine.url):
                print("Creating database")
                create_database(app.config['SQLALCHEMY_DATABASE_URI'])
                with app.app_context():
                    db.create_all()
            break
        except Exception as e:
            print(e)
            retries -= 1
            time.sleep(5)
    if retries == 0:
        print("Could not create database")
        exit(1)

if __name__ == "__main__":
    ensure_database_exists()
    app.run('0.0.0.0', debug=True)