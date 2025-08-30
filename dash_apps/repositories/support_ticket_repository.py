from dash_apps.models.support_ticket import SupportTicket
from dash_apps.schemas.support_ticket import SupportTicketSchema
from dash_apps.core.database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any, Tuple

class SupportTicketRepository:
    @staticmethod
    def get_ticket(session: Session, ticket_id: str) -> Optional[SupportTicketSchema]:
        ticket = session.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()
        return SupportTicketSchema.model_validate(ticket) if ticket else None

    @staticmethod
    def list_tickets(session: Session, skip: int = 0, limit: int = 100) -> List[SupportTicketSchema]:
        tickets = session.query(SupportTicket).offset(skip).limit(limit).all()
        ticket_dicts = []
        for ticket in tickets:
            d = ticket.to_dict() if hasattr(ticket, 'to_dict') else dict(ticket)
            if 'ticket_id' in d and not isinstance(d['ticket_id'], str):
                d['ticket_id'] = str(d['ticket_id'])
            ticket_dicts.append(d)
        return [SupportTicketSchema.model_validate(ticket) for ticket in ticket_dicts]

    @staticmethod
    def create_ticket(session: Session, ticket_data: dict) -> SupportTicketSchema:
        raise NotImplementedError("La création de tickets de support n'est pas autorisée via ce repository.")

    @staticmethod
    def update_ticket(session: Session, ticket_id: str, updates: dict) -> Optional[SupportTicketSchema]:
        # Toujours convertir ticket_id en str pour éviter les erreurs Pydantic
        ticket_id_str = str(ticket_id)
        ticket = session.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id_str).first()
        if not ticket:
            return None
        # N'autoriser la modification que du champ 'status'
        if 'status' in updates:
            ticket.status = updates['status']
            session.commit()
            session.refresh(ticket)
        # Toujours passer un dict avec ticket_id en str à Pydantic
        if hasattr(ticket, 'to_dict'):
            ticket_dict = ticket.to_dict()
        else:
            ticket_dict = dict(ticket)
        if 'ticket_id' in ticket_dict and not isinstance(ticket_dict['ticket_id'], str):
            ticket_dict['ticket_id'] = str(ticket_dict['ticket_id'])
        return SupportTicketSchema.model_validate(ticket_dict)

    @staticmethod
    def delete_ticket(session: Session, ticket_id: str) -> bool:
        raise NotImplementedError("La suppression de tickets de support n'est pas autorisée via ce repository.")
        
    @staticmethod
    def count_tickets(session: Session, status: Optional[str] = None,
                      category: Optional[str] = None, subtype: Optional[str] = None) -> int:
        """Compte le nombre total de tickets, filtré par statut/catégorie/sous-type si spécifié"""
        query = session.query(func.count(SupportTicket.ticket_id))
        if status:
            query = query.filter(SupportTicket.status == status)

        # Appliquer les filtres de catégorie et sous-type (insensibles à la casse)
        if category:
            c = (category or "").lower()
            if c == "signalement_trajet":
                query = query.filter(func.lower(SupportTicket.subject).like('%[signalement trajet]%'))

        if subtype:
            s = (subtype or "").lower()
            tag_map = {
                "conducteur_absent": "[conducteur absent]",
                "conducteur_en_retard": "[conducteur en retard]",
                "autre": "[autre]",
            }
            tag = tag_map.get(s)
            if tag:
                query = query.filter(func.lower(SupportTicket.message).like(f'%{tag}%'))
        return query.scalar() or 0
    
    @staticmethod
    def update_ticket_status(session: Session, ticket_id: str, new_status: str) -> Tuple[Optional[str], Optional[str]]:
        """Met à jour le statut d'un ticket et retourne l'ancien et le nouveau statut
        
        Args:
            session: Session de base de données
            ticket_id: Identifiant du ticket à mettre à jour
            new_status: Nouveau statut à appliquer
            
        Returns:
            Tuple contenant (ancien_statut, nouveau_statut) ou (None, None) si le ticket n'est pas trouvé
        """
        from datetime import datetime
        
        # Toujours convertir ticket_id en str
        ticket_id_str = str(ticket_id)
        
        # Récupérer le ticket
        ticket = session.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id_str).first()
        
        if not ticket:
            return None, None
            
        # Sauvegarder l'ancien statut et appliquer le nouveau
        old_status = ticket.status
        ticket.status = new_status
        ticket.updated_at = datetime.now()
        
        # Valider la transaction
        session.commit()
        
        return old_status, new_status
        
    @staticmethod
    def convert_ticket_to_schema(ticket) -> SupportTicketSchema:
        """Convertit un modèle SupportTicket en schéma validé
        
        Args:
            ticket: Objet SupportTicket de la base de données
            
        Returns:
            SupportTicketSchema validé
        """
        # Convertir en dictionnaire selon la méthode disponible
        d = ticket.to_dict() if hasattr(ticket, 'to_dict') else dict(ticket)
        
        # S'assurer que l'ID est une chaîne de caractères
        if 'ticket_id' in d and not isinstance(d['ticket_id'], str):
            d['ticket_id'] = str(d['ticket_id'])
            
        # Valider et retourner le schéma
        return SupportTicketSchema.model_validate(d)
        
    @staticmethod
    def get_tickets_with_pagination(session: Session, page: int = 1, page_size: int = 10, status: Optional[str] = None) -> Dict[str, Any]:
        """Récupère une page de tickets avec pagination et métadonnées
        
        Args:
            session: Session de base de données
            page: Numéro de page (commence à 1)
            page_size: Nombre d'éléments par page
            status: Filtre optionnel par statut
            
        Returns:
            Un dictionnaire contenant la liste des tickets et les métadonnées de pagination
        """
        # Calcul de l'offset
        skip = (page - 1) * page_size
        
        # Construction de la requête de base
        query = session.query(SupportTicket)
        
        # Appliquer le filtre de statut si nécessaire
        if status:
            query = query.filter(SupportTicket.status == status)
            
        # Compter le nombre total
        total_count = SupportTicketRepository.count_tickets(session, status)
        
        # Récupérer la page demandée
        tickets = query.order_by(SupportTicket.created_at.desc()).offset(skip).limit(page_size).all()
        
        # Convertir en schémas
        ticket_schemas = [SupportTicketRepository.convert_ticket_to_schema(ticket) for ticket in tickets]
        
        # Calculer le nombre total de pages
        total_pages = (total_count + page_size - 1) // page_size
        
        # Retourner les tickets et les métadonnées de pagination
        return {
            "tickets": ticket_schemas,
            "pagination": {
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
    
    @staticmethod
    def get_tickets_by_page(session: Session, page: int = 1, page_size: int = 10, status: Optional[str] = None,
                            category: Optional[str] = None, subtype: Optional[str] = None) -> dict:
        """Récupère les tickets par page, version simplifiée
        
        Args:
            session: Session de base de données
            page: Numéro de la page
            page_size: Nombre de tickets par page
            status: Filtre optionnel par statut
            
        Returns:
            Dict contenant les tickets et les informations de pagination
        """
        # Calculer le décalage
        skip = (page - 1) * page_size
        
        # Construction de la requête de base
        query = session.query(SupportTicket)

        # Appliquer le filtre de statut si nécessaire
        if status:
            query = query.filter(SupportTicket.status == status)

        # Appliquer les filtres de catégorie et sous-type (insensibles à la casse)
        if category:
            c = (category or "").lower()
            if c == "signalement_trajet":
                query = query.filter(func.lower(SupportTicket.subject).like('%[signalement trajet]%'))

        if subtype:
            s = (subtype or "").lower()
            tag_map = {
                "conducteur_absent": "[conducteur absent]",
                "conducteur_en_retard": "[conducteur en retard]",
                "autre": "[autre]",
            }
            tag = tag_map.get(s)
            if tag:
                query = query.filter(func.lower(SupportTicket.message).like(f'%{tag}%'))

        # Compter le nombre total filtré
        total_count = query.count()

        # Récupérer les tickets pour la page demandée
        tickets = query.order_by(SupportTicket.created_at.desc()).offset(skip).limit(page_size).all()
        
        # Convertir en schémas
        ticket_schemas = [SupportTicketRepository.convert_ticket_to_schema(ticket) for ticket in tickets]
        
        # Calculer le nombre total de pages
        total_pages = (total_count + page_size - 1) // page_size
        
        # Retourner les tickets et les informations de pagination
        return {
            "tickets": ticket_schemas,
            "pagination": {
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
