"""
Module de connexion à la base de données PostgreSQL/Supabase
"""
import os
from sqlalchemy import create_engine, MetaData, Table, Column, BigInteger, Integer, String, Float, Boolean, DateTime, Date, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import text
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer l'URL de connexion à la base de données
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie.")

# Créer une connexion à la base de données
engine = create_engine(DATABASE_URL)
Base = declarative_base()
metadata = MetaData()

# Créer une session factory
Session = sessionmaker(bind=engine)

# Définition des modèles ORM
class Trip(Base):
    __tablename__ = "trips"
    
    trip_id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    departure_date = Column(DateTime(timezone=True), nullable=True)
    departure_name = Column(String, nullable=True)
    departure_schedule = Column(DateTime(timezone=True), nullable=True)
    destination_name = Column(String, nullable=True)
    destination_schedule = Column(DateTime(timezone=True), nullable=True)
    number_of_seats = Column(Integer, nullable=True)
    available_seats = Column(Integer, nullable=True)
    price_per_seat = Column(Integer, nullable=True)
    trip_distance = Column(Float, nullable=True)
    trip_precision = Column(String, nullable=True)
    trip_polyline = Column(String, nullable=True)
    auto_confirmation = Column(Boolean, nullable=True)
    passenger_count = Column(Integer, nullable=True)
    driver_id = Column(String, nullable=True)
    passenger_reservations = Column(JSON, nullable=True)
    departure_latitude = Column(Float, nullable=True)
    departure_longitude = Column(Float, nullable=True)
    destination_latitude = Column(Float, nullable=True)
    destination_longitude = Column(Float, nullable=True)
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            "trip_id": self.trip_id,
            "created_at": self.created_at,
            "departure_date": self.departure_date,
            "departure_name": self.departure_name,
            "departure_schedule": self.departure_schedule,
            "destination_name": self.destination_name,
            "destination_schedule": self.destination_schedule,
            "number_of_seats": self.number_of_seats,
            "available_seats": self.available_seats,
            "price_per_seat": self.price_per_seat,
            "trip_distance": self.trip_distance,
            "trip_precision": self.trip_precision,
            "trip_polyline": self.trip_polyline,
            "auto_confirmation": self.auto_confirmation,
            "passenger_count": self.passenger_count,
            "driver_id": self.driver_id,
            "passenger_reservations": self.passenger_reservations,
            "departure_latitude": self.departure_latitude,
            "departure_longitude": self.departure_longitude,
            "destination_latitude": self.destination_latitude,
            "destination_longitude": self.destination_longitude
        }


class User(Base):
    __tablename__ = "users"
    
    # Clé primaire est uid et non id
    uid = Column(String, primary_key=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)  # La base utilise updated_at et non created_at
    display_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    birth = Column(Date, nullable=True)
    photo_url = Column(String, nullable=True)
    short_description = Column(String, nullable=True)
    # phone_verified retiré car n'existe pas dans la base de données
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            "uid": self.uid,  # uid est la clé primaire, on ne renvoie pas id
            "updated_at": self.updated_at,
            "display_name": self.display_name,
            "email": self.email,
            "first_name": self.first_name,
            "name": self.name,
            "phone_number": self.phone_number,
            "birth": self.birth,
            "photo_url": self.photo_url,
            "short_description": self.short_description
            # "phone_verified" retiré car n'existe pas dans la base de données
        }


class TripPassenger(Base):
    __tablename__ = "trip_passengers"
    
    id = Column(BigInteger, primary_key=True)
    trip_id = Column(String, ForeignKey("trips.trip_id"), nullable=False)
    passenger_id = Column(String, ForeignKey("users.uid"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=True)  # ex: confirmed, pending, cancelled
    seats = Column(Integer, nullable=True, default=1)  # nombre de sièges réservés
    
    # Relations avec les autres tables
    trip = relationship("Trip")
    passenger = relationship("User")
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            "id": self.id,
            "trip_id": self.trip_id,
            "passenger_id": self.passenger_id,
            "created_at": self.created_at,
            "status": self.status,
            "seats": self.seats
        }


class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(String, primary_key=True)
    trip_id = Column(String, nullable=True)
    sender_id = Column(String, nullable=True)
    message = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    # Relation avec les autres tables
    # Désactivons les relations pour l'instant car nous n'avons pas de clés étrangères
    # trip = relationship("Trip")
    # sender = relationship("User")
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            "id": self.id,
            "trip_id": self.trip_id,
            "sender_id": self.sender_id,
            "message": self.message,
            "timestamp": self.timestamp,
            "updated_at": self.updated_at
        }


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.uid"), nullable=True)
    external_id = Column(String, nullable=True)
    msg = Column(String, nullable=True)
    amount = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    service_code = Column(String, nullable=True)
    sender = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)
    has_transactions = Column(Boolean, nullable=True)
    transaction_metadata = Column(JSON, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "external_id": self.external_id,
            "msg": self.msg,
            "amount": self.amount,
            "status": self.status,
            "phone": self.phone,
            "service_code": self.service_code,
            "sender": self.sender,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error_message": self.error_message,
            "has_transactions": self.has_transactions,
            "transaction_metadata": self.transaction_metadata
        }


def init_db():
    """Initialise la base de données en créant les tables si elles n'existent pas"""
    # Utiliser des commandes SQL directes pour créer les tables dans le bon ordre
    with engine.begin() as connection:
        # Essayons une approche plus simple sans les contraintes de clés étrangères
        # pour un premier test - nous ajouterons les contraintes plus tard si nécessaire
        
        # Créer la table trips
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS trips (
            trip_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP,
            departure_date TIMESTAMP,
            departure_name VARCHAR,
            departure_schedule TIMESTAMP,
            destination_name VARCHAR,
            destination_schedule TIMESTAMP,
            number_of_seats INTEGER,
            available_seats INTEGER,
            price_per_seat INTEGER,
            trip_distance FLOAT,
            trip_precision VARCHAR,
            trip_polyline VARCHAR,
            auto_confirmation BOOLEAN,
            passenger_count INTEGER,
            driver_id VARCHAR,
            passenger_reservations JSON,
            departure_latitude FLOAT,
            departure_longitude FLOAT,
            destination_latitude FLOAT,
            destination_longitude FLOAT
        );
        """))
        
        # Créer la table users
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            created_at TIMESTAMP,
            uid VARCHAR,
            display_name VARCHAR,
            email VARCHAR,
            first_name VARCHAR,
            name VARCHAR,
            phone_number VARCHAR,
            birth DATE,
            photo_url VARCHAR,
            short_description VARCHAR,
            phone_verified BOOLEAN
        );
        """))
        
        # Créer la table trip_passengers
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS trip_passengers (
            id BIGSERIAL PRIMARY KEY,
            trip_id VARCHAR REFERENCES trips(trip_id),
            passenger_id BIGINT REFERENCES users(id),
            created_at TIMESTAMP,
            status VARCHAR,
            seats INTEGER DEFAULT 1
        );
        """))
        
        # Créer la table chats sans les contraintes de clés étrangères
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS chats (
            id VARCHAR PRIMARY KEY,
            trip_id VARCHAR,
            sender_id VARCHAR,
            message VARCHAR,
            timestamp TIMESTAMP,
            updated_at TIMESTAMP
        );
        """))
        
        # Créer la table transactions
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS transactions (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR REFERENCES users(id),
            external_id VARCHAR,
            msg VARCHAR,
            amount INTEGER,
            status VARCHAR,
            phone VARCHAR,
            service_code VARCHAR,
            sender VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            error_message VARCHAR,
            has_transactions BOOLEAN,
            transaction_metadata JSON
        );
        """))


def get_session():
    """Renvoie une session de base de données"""
    return Session()


def execute_raw_query(query, params=None):
    """Exécute une requête SQL brute et renvoie les résultats"""
    with engine.connect() as connection:
        if params:
            result = connection.execute(text(query), params)
        else:
            result = connection.execute(text(query))
        return result.fetchall()
