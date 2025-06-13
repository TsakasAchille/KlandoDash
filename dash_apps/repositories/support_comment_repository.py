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
        comments = session.query(SupportComment).filter(SupportComment.ticket_id == ticket_id).order_by(SupportComment.created_at.asc()).all()
        comment_dicts = []
        for comment in comments:
            d = comment.to_dict() if hasattr(comment, 'to_dict') else dict(comment)
            if 'comment_id' in d and not isinstance(d['comment_id'], str):
                d['comment_id'] = str(d['comment_id'])
            if 'ticket_id' in d and not isinstance(d['ticket_id'], str):
                d['ticket_id'] = str(d['ticket_id'])
            comment_dicts.append(d)
        return [SupportCommentSchema.model_validate(comment) for comment in comment_dicts]

    @staticmethod
    def add_comment(session: Session, ticket_id: str, user_id: str, comment_text: str) -> SupportCommentSchema:
        comment = SupportComment(
            ticket_id=ticket_id,
            user_id=user_id,
            comment_text=comment_text,
            created_at=datetime.now()
        )
        session.add(comment)
        session.commit()
        session.refresh(comment)
        d = comment.to_dict() if hasattr(comment, 'to_dict') else dict(comment)
        if 'comment_id' in d and not isinstance(d['comment_id'], str):
            d['comment_id'] = str(d['comment_id'])
        if 'ticket_id' in d and not isinstance(d['ticket_id'], str):
            d['ticket_id'] = str(d['ticket_id'])
        return SupportCommentSchema.model_validate(d)
