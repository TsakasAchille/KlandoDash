"""
Modèle pour le mapping des références de tickets sécurisées
"""
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from dash_apps.core.database import Base
from datetime import datetime
import uuid

class TicketReference(Base):
    """
    Table de mapping entre tokens publics et IDs de tickets internes
    """
    __tablename__ = 'ticket_references'
    
    # Token public (ex: TK-2024-001, REF-ABC123)
    reference_token = Column(String(20), primary_key=True, nullable=False)
    
    # ID interne du ticket (UUID)
    ticket_id = Column(String(36), nullable=False, unique=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # Optionnel: expiration du token
    
    # Index pour recherche rapide
    __table_args__ = (
        Index('idx_ticket_references_ticket_id', 'ticket_id'),
        Index('idx_ticket_references_token', 'reference_token'),
    )
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'reference_token': self.reference_token,
            'ticket_id': self.ticket_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
