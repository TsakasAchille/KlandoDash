"""
Service de mapping sécurisé pour les références de tickets
"""
import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from dash_apps.core.database import get_session
from dash_apps.models.ticket_reference import TicketReference

logger = logging.getLogger("klando.ticket_reference")

class TicketReferenceService:
    """Service pour gérer les tokens de référence sécurisés des tickets"""
    
    @staticmethod
    def generate_reference_token(ticket_id: str, format_type: str = "TK") -> str:
        """
        Génère un token de référence sécurisé pour un ticket
        
        Args:
            ticket_id: ID interne du ticket (UUID)
            format_type: Type de format (TK, REF, SUP)
            
        Returns:
            str: Token de référence (ex: TK-2024-A7B9)
        """
        try:
            # Générer une partie aléatoire sécurisée
            random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                                for _ in range(4))
            
            # Format avec année courante
            year = datetime.now().year
            token = f"{format_type}-{year}-{random_part}"
            
            logger.info(f"DEBUG: Token généré: {token} pour ticket {ticket_id[:8] if ticket_id else 'None'}...")
            return token
            
        except Exception as e:
            logger.error(f"Erreur génération token: {e}")
            # Fallback simple
            return f"TK-{secrets.token_hex(4).upper()}"
    
    @staticmethod
    def create_reference_mapping(ticket_id: str, custom_token: str = None) -> Optional[str]:
        """
        Crée un mapping entre un ticket et son token de référence
        
        Args:
            ticket_id: ID interne du ticket
            custom_token: Token personnalisé (optionnel)
            
        Returns:
            str: Token de référence créé, None si erreur
        """
        try:
            with get_session() as session:
                # Vérifier si un mapping existe déjà
                existing = session.query(TicketReference).filter(
                    TicketReference.ticket_id == ticket_id
                ).first()
                
                if existing:
                    logger.info(f"DEBUG: Mapping existant trouvé: {existing.reference_token}")
                    return existing.reference_token
                
                # Générer ou utiliser le token fourni
                token = custom_token or TicketReferenceService.generate_reference_token(ticket_id)
                
                # Vérifier l'unicité du token
                while session.query(TicketReference).filter(
                    TicketReference.reference_token == token
                ).first():
                    logger.warning(f"DEBUG: Token {token} déjà utilisé, régénération...")
                    token = TicketReferenceService.generate_reference_token(ticket_id)
                
                # Créer le mapping
                reference = TicketReference(
                    reference_token=token,
                    ticket_id=ticket_id,
                    created_at=datetime.utcnow()
                )
                
                session.add(reference)
                session.commit()
                
                logger.info(f"DEBUG: Mapping créé: {token} -> {ticket_id[:8] if ticket_id else 'None'}...")
                return token
                
        except Exception as e:
            logger.error(f"Erreur création mapping: {e}")
            return None
    
    @staticmethod
    def resolve_reference_token(token: str) -> Optional[str]:
        """
        Résout un token de référence vers l'ID interne du ticket
        
        Args:
            token: Token de référence (ex: TK-2024-A7B9)
            
        Returns:
            str: ID interne du ticket, None si non trouvé
        """
        try:
            with get_session() as session:
                reference = session.query(TicketReference).filter(
                    TicketReference.reference_token == token
                ).first()
                
                if reference:
                    logger.info(f"DEBUG: Token {token} résolu vers {reference.ticket_id[:8] if reference.ticket_id else 'None'}...")
                    return reference.ticket_id
                else:
                    logger.warning(f"DEBUG: Token {token} non trouvé")
                    return None
                    
        except Exception as e:
            logger.error(f"Erreur résolution token {token}: {e}")
            return None
    
    @staticmethod
    def get_reference_for_ticket(ticket_id: str) -> Optional[str]:
        """
        Récupère le token de référence d'un ticket existant
        
        Args:
            ticket_id: ID interne du ticket
            
        Returns:
            str: Token de référence, None si non trouvé
        """
        try:
            with get_session() as session:
                reference = session.query(TicketReference).filter(
                    TicketReference.ticket_id == ticket_id
                ).first()
                
                if reference:
                    return reference.reference_token
                else:
                    # Créer automatiquement un token si il n'existe pas
                    logger.info(f"DEBUG: Création automatique token pour {ticket_id[:8] if ticket_id else 'None'}...")
                    return TicketReferenceService.create_reference_mapping(ticket_id)
                    
        except Exception as e:
            logger.error(f"Erreur récupération référence: {e}")
            return None
    
    @staticmethod
    def extract_token_from_subject(subject: str) -> Optional[str]:
        """
        Extrait un token de référence depuis le sujet d'un email
        
        Args:
            subject: Sujet de l'email
            
        Returns:
            str: Token trouvé, None sinon
        """
        import re
        
        # Patterns pour différents formats de tokens
        patterns = [
            r'#(TK-\d{4}-[A-Z0-9]{4})',  # #TK-2024-A7B9
            r'#(REF-\d{4}-[A-Z0-9]{4})', # #REF-2024-B8C1
            r'#(SUP-\d{4}-[A-Z0-9]{4})', # #SUP-2024-D2E5
            r'ticket\s*#([A-Z0-9-]{8,})', # ticket #TK-2024-A7B9
        ]
        
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                token = match.group(1).upper()
                logger.info(f"DEBUG: Token extrait du sujet: {token}")
                return token
        
        logger.warning(f"DEBUG: Aucun token trouvé dans: {subject[:50]}...")
        return None
    
    @staticmethod
    def cleanup_expired_tokens(days_old: int = 365) -> int:
        """
        Nettoie les tokens expirés ou très anciens
        
        Args:
            days_old: Âge en jours pour considérer un token comme ancien
            
        Returns:
            int: Nombre de tokens supprimés
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            with get_session() as session:
                # Supprimer les tokens anciens
                deleted = session.query(TicketReference).filter(
                    TicketReference.created_at < cutoff_date
                ).delete()
                
                session.commit()
                
                logger.info(f"DEBUG: {deleted} tokens anciens supprimés")
                return deleted
                
        except Exception as e:
            logger.error(f"Erreur nettoyage tokens: {e}")
            return 0
