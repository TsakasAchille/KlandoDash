from dash_apps.models.support_comment import SupportComment
from dash_apps.schemas.support_comment import SupportCommentSchema
from dash_apps.core.database import SessionLocal
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class SupportCommentRepository:
    @staticmethod
    def list_comments_for_ticket(session: Session, ticket_id: str) -> List[SupportCommentSchema]:
        # Récupérer les commentaires depuis la base de données
        comments = session.query(SupportComment).filter(SupportComment.ticket_id == ticket_id).order_by(SupportComment.created_at.desc()).all()
        
        # Importer FlaskLogin pour accéder à la session
        from flask import session as flask_session
        
        comment_dicts = []
        for comment in comments:
            d = comment.to_dict() if hasattr(comment, 'to_dict') else dict(comment)
            if 'comment_id' in d and not isinstance(d['comment_id'], str):
                d['comment_id'] = str(d['comment_id'])
            if 'ticket_id' in d and not isinstance(d['ticket_id'], str):
                d['ticket_id'] = str(d['ticket_id'])
                
            # Enrichir avec le nom d'utilisateur
            user_id = d.get('user_id')
            
            # Dans tous les cas, utiliser le nom complet s'il est disponible
            # Le nom est peut-être déjà stocké dans le champ user_id (voir add_comment)
            if user_id and len(user_id.split()) > 1:
                # Si user_id ressemble déjà à un nom (contient des espaces)
                d['user_name'] = user_id
            elif user_id == flask_session.get('user_id'):
                # Si c'est l'utilisateur courant, prendre son nom de la session
                d['user_name'] = flask_session.get('user_name', user_id)
            else:
                # Pour les autres cas, afficher le nom complet disponible ou "Contact" par défaut
                d['user_name'] = user_id if user_id else "Système"
            
            comment_dicts.append(d)
            
        return [SupportCommentSchema.model_validate(comment) for comment in comment_dicts]

    @staticmethod
    def add_comment(session: Session, ticket_id: str, user_id: str, comment_text: str, user_name: str = None) -> SupportCommentSchema:
        # Créer le commentaire en base de données (type internal par défaut)
        comment = SupportComment(
            ticket_id=ticket_id,
            user_id=user_name,
            comment_text=comment_text,
            comment_type="internal",
            created_at=datetime.now()
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)
        
        # Convertir en dictionnaire pour la validation Pydantic
        d = comment.to_dict() if hasattr(comment, 'to_dict') else dict(comment)
        if 'comment_id' in d and not isinstance(d['comment_id'], str):
            d['comment_id'] = str(d['comment_id'])
        if 'ticket_id' in d and not isinstance(d['ticket_id'], str):
            d['ticket_id'] = str(d['ticket_id'])
        
        # Ajouter le nom d'utilisateur pour l'affichage (non stocké en base)
        d['user_name'] = user_name or user_id
        
        return SupportCommentSchema.model_validate(d)

    @staticmethod
    def add_comment_with_type(session: Session, ticket_id: str, user_id: str, comment_text: str, user_name: str = None, comment_type: str = "internal", comment_sent: str = None) -> SupportCommentSchema:
        """
        Ajoute un commentaire avec un type spécifique (pour emails)
        
        Args:
            session: Session de base de données
            ticket_id: ID du ticket
            user_id: ID de l'utilisateur
            comment_text: Contenu du commentaire
            user_name: Nom d'affichage de l'utilisateur
            comment_type: Type de commentaire (internal, external_sent, external_received)
            comment_sent: Contenu du message envoyé (pour emails)
        """
        comment = SupportComment(
            ticket_id=ticket_id,
            user_id=user_name or user_id,
            comment_text=comment_text,
            comment_type=comment_type,
            comment_sent=comment_sent,
            comment_source="mail" if comment_sent else None,
            created_at=datetime.now()
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)
        
        # Convertir en dictionnaire pour la validation Pydantic
        d = comment.to_dict() if hasattr(comment, 'to_dict') else dict(comment)
        if 'comment_id' in d and not isinstance(d['comment_id'], str):
            d['comment_id'] = str(d['comment_id'])
        if 'ticket_id' in d and not isinstance(d['ticket_id'], str):
            d['ticket_id'] = str(d['ticket_id'])
        
        # Ajouter le nom d'utilisateur pour l'affichage
        d['user_name'] = user_name or user_id
        
        return SupportCommentSchema.model_validate(d)
