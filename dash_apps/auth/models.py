from flask_login import UserMixin

class User(UserMixin):
    """
    Modèle utilisateur simplifié pour l'authentification en mémoire
    """
    
    def __init__(self, id, email, name=None, profile_pic=None, tags=None, admin=False, active=True):
        self.id = id
        self.email = email
        self.name = name
        self.profile_pic = profile_pic
        self.tags = tags or ''
        self.admin = admin
        self.active = active
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def get_tags_list(self):
        """Retourne les tags sous forme de liste"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]
    
    def add_tag(self, tag):
        """Ajoute un tag à l'utilisateur"""
        tags = self.get_tags_list()
        if tag not in tags:
            tags.append(tag)
            self.tags = ','.join(tags)
            return True
        return False
    
    def remove_tag(self, tag):
        """Supprime un tag de l'utilisateur"""
        tags = self.get_tags_list()
        if tag in tags:
            tags.remove(tag)
            self.tags = ','.join(tags)
            return True
        return False
