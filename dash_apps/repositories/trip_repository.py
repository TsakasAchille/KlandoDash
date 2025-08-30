from dash_apps.models.trip import Trip
from dash_apps.schemas.trip import TripSchema
from dash_apps.core.database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, exists
from typing import List, Optional
import datetime

from dash_apps.models.support_ticket import SupportTicket

class TripRepository:
    @staticmethod
    def get_trip(session: Session, trip_id: str) -> Optional[TripSchema]:
        trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()
        return TripSchema.model_validate(trip) if trip else None

    @staticmethod
    def list_trips(session: Session, skip: int = 0, limit: int = 100) -> List[TripSchema]:
        trips = session.query(Trip).offset(skip).limit(limit).all()
        return [TripSchema.model_validate(trip) for trip in trips]

    @staticmethod
    def get_trip_by_id(trip_id: str) -> Optional[TripSchema]:
        with SessionLocal() as db:
            trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
            return TripSchema.model_validate(trip) if trip else None

    @staticmethod
    def get_trip_position(trip_id: str) -> Optional[int]:
        """Trouve la position d'un trajet dans la liste triée par date de création (desc par défaut)"""
        with SessionLocal() as db:
            # Trouver le trajet cible
            target_trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
            if not target_trip:
                return None
            
            # Compter les trajets créés APRÈS ce trajet (pour l'ordre descendant)
            # car l'ordre par défaut est desc (plus récents en premier)
            position = db.query(func.count(Trip.trip_id)).filter(
                Trip.created_at > target_trip.created_at
            ).scalar()
            
            return position if position is not None else None

    @staticmethod
    def get_trips_paginated(page: int = 0, page_size: int = 10, filters: dict = None) -> dict:
        """Récupère les trajets de façon paginée avec filtrage optionnel
        
        Args:
            page: Numéro de page (commence à 0)
            page_size: Nombre d'éléments par page
            filters: Dictionnaire des filtres à appliquer avec les clés suivantes:
                - text: Recherche par origine, destination ou trip_id
                - date_from: Date de création minimale
                - date_to: Date de création maximale
                - status: Filtrer par statut (active, completed, cancelled)
            
        Returns:
            Un dictionnaire contenant:
            - trips: Liste des trajets de la page
            - total_count: Nombre total de trajets après filtrage
        """
        with SessionLocal() as db:
            # Commencer avec une requête de base
            query = db.query(Trip)
            
            # Appliquer les filtres si spécifiés
            if filters:
                # Filtre texte (origine, destination, trip_id)
                if filters.get("text"):
                    search_term = f'%{filters["text"]}%'
                    query = query.filter(
                        or_(
                            Trip.departure_name.ilike(search_term),
                            Trip.destination_name.ilike(search_term),
                            Trip.trip_id.ilike(search_term)
                        )
                    )
                
                # Filtrage par date de création
                date_filter_type = filters.get("date_filter_type", "range")
                
                if date_filter_type == "after" and filters.get("single_date"):
                    single_date = filters["single_date"]
                    try:
                        date_obj = datetime.datetime.strptime(single_date, "%Y-%m-%d").date()
                        query = query.filter(func.date(Trip.created_at) >= date_obj)
                    except ValueError:
                        pass
                
                elif date_filter_type == "before" and filters.get("single_date"):
                    single_date = filters["single_date"]
                    try:
                        date_obj = datetime.datetime.strptime(single_date, "%Y-%m-%d").date()
                        query = query.filter(func.date(Trip.created_at) <= date_obj)
                    except ValueError:
                        pass
                
                else:  # range
                    if filters.get("date_from"):
                        try:
                            date_from = datetime.datetime.strptime(filters["date_from"], "%Y-%m-%d").date()
                            query = query.filter(func.date(Trip.created_at) >= date_from)
                        except ValueError:
                            pass
                    
                    if filters.get("date_to"):
                        try:
                            date_to = datetime.datetime.strptime(filters["date_to"], "%Y-%m-%d").date()
                            query = query.filter(func.date(Trip.created_at) <= date_to)
                        except ValueError:
                            pass
                
                # Filtre statut
                if filters.get("status") and filters["status"] != "all":
                    query = query.filter(Trip.status == filters["status"])

                # Filtre: trajets ayant au moins un signalement associé
                if filters.get("has_signalement"):
                    subq = db.query(SupportTicket.ticket_id).filter(
                        func.lower(SupportTicket.subject).like('%[signalement trajet]%'),
                        SupportTicket.subject.ilike(func.concat('%', Trip.trip_id, '%'))
                    ).exists()
                    query = query.filter(subq)
            
            # Tri par date de création (plus récent en premier par défaut)
            date_sort = filters.get("date_sort", "desc") if filters else "desc"
            if date_sort == "asc":
                query = query.order_by(Trip.created_at.asc())
            else:
                query = query.order_by(Trip.created_at.desc())
            
            # Compter le total après filtrage
            total_count = query.count()
            
            # Appliquer la pagination
            trips = query.offset(page * page_size).limit(page_size).all()
            
            # Convertir en schémas Pydantic
            trips_schemas = [TripSchema.model_validate(trip) for trip in trips]
            
            return {
                "trips": trips_schemas,
                "total_count": total_count
            }

    @staticmethod
    def create_trip(session: Session, trip_data: dict) -> TripSchema:
        trip = Trip(**trip_data)
        session.add(trip)
        session.commit()
        session.refresh(trip)
        return TripSchema.model_validate(trip)

    @staticmethod
    def update_trip(session: Session, trip_id: str, updates: dict) -> Optional[TripSchema]:
        trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            return None
        for key, value in updates.items():
            setattr(trip, key, value)
        session.commit()
        session.refresh(trip)
        return TripSchema.model_validate(trip)

    @staticmethod
    def delete_trip(session: Session, trip_id: str) -> bool:
        trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            return False
        session.delete(trip)
        session.commit()
        return True
