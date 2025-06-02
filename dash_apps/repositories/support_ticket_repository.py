from dash_apps.models.support_ticket import SupportTicket
from dash_apps.schemas.support_ticket import SupportTicketSchema
from dash_apps.core.database import SessionLocal
from sqlalchemy.orm import Session
from typing import List, Optional

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
