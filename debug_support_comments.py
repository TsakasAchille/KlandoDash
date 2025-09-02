#!/usr/bin/env python3
"""
Script pour lire et afficher toute la table support_comments
"""

from dash_apps.core.database import get_session
from dash_apps.models.support_comment import SupportComment
from sqlalchemy import text, inspect
import pandas as pd

def debug_support_comments():
    """
    Lit et affiche toutes les données de la table support_comments
    """
    
    print("🔍 Debug de la table support_comments")
    print("=" * 60)
    
    try:
        with get_session() as session:
            # Détecter le type de base de données
            engine = session.get_bind()
            db_type = engine.dialect.name
            print(f"Type de base de données: {db_type}")
            print()
            
            # 1. Vérifier la structure de la table
            print("1. Structure de la table:")
            
            # Utiliser l'inspector SQLAlchemy qui fonctionne avec tous les types de DB
            inspector = inspect(engine)
            
            if 'support_comments' not in inspector.get_table_names():
                print("   ❌ Table support_comments non trouvée")
                return
            
            columns = inspector.get_columns('support_comments')
            
            if columns:
                print("   Colonnes:")
                for col in columns:
                    nullable = "YES" if col.get('nullable', True) else "NO"
                    default = col.get('default', 'NULL')
                    print(f"   - {col['name']} ({col['type']}) - Nullable: {nullable} - Default: {default}")
            else:
                print("   ❌ Impossible de lire la structure de la table")
                return
            
            print()
            
            # 2. Compter le nombre total de commentaires
            count_query = text("SELECT COUNT(*) FROM support_comments")
            total_count = session.execute(count_query).scalar()
            print(f"2. Nombre total de commentaires: {total_count}")
            
            if total_count == 0:
                print("   ℹ️ Aucun commentaire dans la table")
                return
            
            print()
            
            # 3. Lister tous les commentaires avec leurs types
            print("3. Tous les commentaires:")
            print("-" * 60)
            
            comments = session.query(SupportComment).order_by(SupportComment.created_at.desc()).all()
            
            for i, comment in enumerate(comments, 1):
                # Déterminer le type d'interaction basé sur les colonnes
                if comment.comment_sent and comment.comment_sent.strip():
                    display_type = "COMMENT_SENT"
                    icon = "📤"
                    content = comment.comment_sent
                elif comment.comment_received and comment.comment_received.strip():
                    display_type = "COMMENT_RECEIVED"
                    icon = "📥"
                    content = comment.comment_received
                elif comment.comment_type == "external":
                    display_type = "EXTERNAL"
                    icon = "🌐"
                    content = comment.comment_text
                elif comment.comment_type == "internal":
                    display_type = "INTERNAL"
                    icon = "💭"
                    content = comment.comment_text
                else:
                    display_type = f"UNKNOWN ({comment.comment_type})" if comment.comment_type else "NO_TYPE"
                    icon = "❓"
                    content = comment.comment_text
                
                print(f"{i}. {icon} {display_type}")
                print(f"   ID: {comment.comment_id}")
                print(f"   Ticket: {comment.ticket_id}")
                print(f"   Utilisateur: {comment.user_id}")
                print(f"   Date: {comment.created_at}")
                print(f"   comment_text: {comment.comment_text[:50]}{'...' if len(str(comment.comment_text)) > 50 else ''}")
                print(f"   comment_sent: {comment.comment_sent[:50] if comment.comment_sent else 'NULL'}{'...' if comment.comment_sent and len(comment.comment_sent) > 50 else ''}")
                print(f"   comment_received: {comment.comment_received[:50] if comment.comment_received else 'NULL'}{'...' if comment.comment_received and len(comment.comment_received) > 50 else ''}")
                print(f"   comment_type: {comment.comment_type or 'NULL'}")
                print(f"   Contenu affiché: {content[:100]}{'...' if len(str(content)) > 100 else ''}")
                print()
            
            # 4. Statistiques par type
            print("4. Statistiques par type:")
            print("-" * 30)
            
            type_stats_query = text("""
                SELECT comment_type, COUNT(*) as count
                FROM support_comments 
                GROUP BY comment_type
                ORDER BY count DESC
            """)
            
            type_stats = session.execute(type_stats_query).fetchall()
            
            for row in type_stats:
                type_name = row[0] or "NULL"
                count = row[1]
                type_icons = {
                    "internal": "💭",
                    "external": "🌐",
                    "NULL": "❓"
                }
                icon = type_icons.get(type_name, "❓")
                print(f"   {icon} {type_name}: {count} commentaires")
            
            # 5. Commentaires récents (dernières 24h)
            print("\n5. Commentaires récents (dernières 24h):")
            print("-" * 40)
            
            # Adapter la requête selon le type de base de données
            if db_type == 'postgresql':
                recent_query = text("""
                    SELECT comment_type, COUNT(*) as count
                    FROM support_comments 
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    GROUP BY comment_type
                    ORDER BY count DESC
                """)
            else:  # SQLite
                recent_query = text("""
                    SELECT comment_type, COUNT(*) as count
                    FROM support_comments 
                    WHERE created_at >= datetime('now', '-24 hours')
                    GROUP BY comment_type
                    ORDER BY count DESC
                """)
            
            recent_stats = session.execute(recent_query).fetchall()
            
            if recent_stats:
                for row in recent_stats:
                    type_name = row[0] or "NULL"
                    count = row[1]
                    type_icons = {
                        "internal": "💭",
                        "external": "🌐",
                        "NULL": "❓"
                    }
                    icon = type_icons.get(type_name, "❓")
                    print(f"   {icon} {type_name}: {count} commentaires")
            else:
                print("   ℹ️ Aucun commentaire récent")
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_support_comments()
