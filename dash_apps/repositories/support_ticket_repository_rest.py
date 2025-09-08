"""
Repository pour les tickets de support utilisant l'API REST Supabase
"""
from dash_apps.repositories.supabase_repository import SupabaseRepository
from typing import List, Optional, Dict, Any, Tuple
import logging
from datetime import datetime

# Logger
logger = logging.getLogger(__name__)

class SupportTicketRepositoryRest(SupabaseRepository):
    """
    Repository pour les tickets de support utilisant l'API REST Supabase
    """
    
    def __init__(self):
        """
        Initialise le repository avec la table 'support_tickets'
        """
        super().__init__("support_tickets")
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """
        Récupère un ticket par son ID
        
        Args:
            ticket_id: Identifiant du ticket
            
        Returns:
            Dictionnaire contenant les informations du ticket ou None si non trouvé
        """
        return self.get_by_id("ticket_id", ticket_id)
    
    def list_tickets(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        Liste les tickets avec pagination
        
        Args:
            skip: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments à retourner
            
        Returns:
            Liste de tickets
        """
        return self.get_all(offset=skip, limit=limit)
    
    def create_ticket(self, ticket_data: dict) -> Optional[Dict]:
        """
        Crée un nouveau ticket (Not implemented)
        
        Args:
            ticket_data: Données du ticket
            
        Returns:
            Le ticket créé ou None
        """
        raise NotImplementedError("La création de tickets de support n'est pas autorisée via ce repository.")
    
    def update_ticket(self, ticket_id: str, updates: dict) -> Optional[Dict]:
        """
        Met à jour un ticket existant (seulement le status)
        
        Args:
            ticket_id: Identifiant du ticket
            updates: Dictionnaire avec les modifications (seul 'status' est autorisé)
            
        Returns:
            Le ticket mis à jour ou None en cas d'erreur
        """
        # N'autoriser la modification que du champ 'status'
        if 'status' in updates:
            status_update = {'status': updates['status']}
            if self.update("ticket_id", ticket_id, status_update):
                return self.get_by_id("ticket_id", ticket_id)
        return None
    
    def delete_ticket(self, ticket_id: str) -> bool:
        """
        Supprime un ticket (Not implemented)
        
        Args:
            ticket_id: Identifiant du ticket
            
        Returns:
            True si supprimé, False sinon
        """
        raise NotImplementedError("La suppression de tickets de support n'est pas autorisée via ce repository.")
    
    def count_tickets(self, status: Optional[str] = None, 
                      category: Optional[str] = None, subtype: Optional[str] = None) -> int:
        """
        Compte le nombre total de tickets, filtré par statut/catégorie/sous-type si spécifié
        
        Args:
            status: Filtre par statut
            category: Filtre par catégorie
            subtype: Filtre par sous-type
            
        Returns:
            Nombre de tickets correspondant aux critères
        """
        try:
            # Filtre initial pour le statut
            filters = {}
            if status:
                filters["status"] = status
            
            # Récupérer tous les tickets avec le filtre de statut
            tickets = self.get_all(filters=filters)
            
            # Appliquer les filtres de catégorie et sous-type en post-traitement
            if category or subtype:
                filtered_tickets = []
                
                for ticket in tickets:
                    match = True
                    
                    # Filtre par catégorie
                    if category and category.lower() == "signalement_trajet":
                        if not (ticket.get("subject", "").lower().find("[signalement trajet]") != -1):
                            match = False
                    
                    # Filtre par sous-type
                    if subtype and match:
                        tag_map = {
                            "conducteur_absent": "[conducteur absent]",
                            "conducteur_en_retard": "[conducteur en retard]",
                            "autre": "[autre]",
                        }
                        tag = tag_map.get(subtype.lower())
                        if tag and not (ticket.get("message", "").lower().find(tag) != -1):
                            match = False
                    
                    if match:
                        filtered_tickets.append(ticket)
                
                return len(filtered_tickets)
            
            # Si pas de filtre catégorie/sous-type, retourner simplement le nombre de tickets
            return len(tickets)
            
        except Exception as e:
            logger.error(f"Erreur lors du comptage des tickets: {str(e)}")
            return 0
    
    def update_ticket_status(self, ticket_id: str, new_status: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Met à jour le statut d'un ticket et retourne l'ancien et le nouveau statut
        
        Args:
            ticket_id: Identifiant du ticket à mettre à jour
            new_status: Nouveau statut à appliquer
            
        Returns:
            Tuple contenant (ancien_statut, nouveau_statut) ou (None, None) si le ticket n'est pas trouvé
        """
        # Récupérer le ticket existant pour obtenir l'ancien statut
        ticket = self.get_by_id("ticket_id", ticket_id)
        
        if not ticket:
            return None, None
        
        # Sauvegarder l'ancien statut
        old_status = ticket.get("status")
        
        # Mettre à jour le ticket
        updates = {
            "status": new_status,
            "updated_at": datetime.now().isoformat()
        }
        
        success = self.update("ticket_id", ticket_id, updates)
        
        if success:
            return old_status, new_status
        else:
            return old_status, old_status  # Pas de changement si échec
    
    def get_tickets_paginated_minimal(self, page_index: int, page_size: int, 
                                     filters: Dict[str, Any] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Version optimisée pour récupérer les tickets avec pagination minimale
        
        Args:
            page_index: Index de la page (1-based)
            page_size: Nombre d'éléments par page
            filters: Dictionnaire des filtres (category, subtype)
            status: Filtre par statut
            
        Returns:
            Dict contenant tickets, total_count et pagination
        """
        try:
            # Extraire les filtres
            category = filters.get('category') if filters else None
            subtype = filters.get('subtype') if filters else None
            
            # Utiliser la méthode optimisée
            result = self.get_tickets_by_page(
                page=page_index,
                page_size=page_size,
                status=status,
                category=category,
                subtype=subtype
            )
            
            return {
                "tickets": result["tickets"],
                "total_count": result["pagination"]["total_count"],
                "pagination": result["pagination"]
            }
                
        except Exception as e:
            logger.error(f"Erreur get_tickets_paginated_minimal: {str(e)}")
            return {
                "tickets": [],
                "total_count": 0,
                "pagination": {
                    "total_count": 0,
                    "page": page_index,
                    "page_size": page_size,
                    "total_pages": 1
                }
            }
    
    def get_tickets_with_pagination(self, page: int = 1, page_size: int = 10, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère une page de tickets avec pagination et métadonnées (méthode legacy)
        
        Args:
            page: Numéro de page (commence à 1)
            page_size: Nombre d'éléments par page
            status: Filtre optionnel par statut
            
        Returns:
            Un dictionnaire contenant la liste des tickets et les métadonnées de pagination
        """
        # Rediriger vers la méthode optimisée
        return self.get_tickets_paginated_minimal(
            page_index=page,
            page_size=page_size,
            filters={},
            status=status
        )
    
    def get_trip_signalements_count(self, trip_id: str) -> int:
        """
        Retourne le nombre de signalements liés à un trip donné.
        Le lien est détecté via le sujet contenant le tag '[Signalement trajet]'
        et l'ID du trajet.
        """
        if not trip_id:
            return 0
        
        trip_id_str = str(trip_id).strip()
        
        try:
            # Récupérer tous les tickets
            all_tickets = self.get_all()
            
            # Filtrer les signalements liés au trajet
            signalements = [
                t for t in all_tickets if (
                    "[signalement trajet]" in t.get("subject", "").lower() and
                    trip_id_str in t.get("subject", "").lower()
                )
            ]
            
            return len(signalements)
            
        except Exception as e:
            logger.error(f"Erreur lors du comptage des signalements: {str(e)}")
            return 0
    
    def has_signalement_for_trip(self, trip_id: str) -> bool:
        """
        Indique si un trip a au moins un signalement associé.
        """
        return self.get_trip_signalements_count(trip_id) > 0
    
    def list_signalements_for_trip(self, trip_id: str) -> List[Dict]:
        """
        Retourne la liste des tickets associés à un trajet via le sujet.
        Critères: subject contient '[Signalement trajet]' et l'ID du trajet.
        """
        if not trip_id:
            return []
        
        trip_id_str = str(trip_id).strip()
        
        try:
            # Récupérer tous les tickets
            all_tickets = self.get_all(order_by="created_at", order_direction="desc")
            
            # Filtrer les signalements liés au trajet
            signalements = [
                t for t in all_tickets if (
                    "[signalement trajet]" in t.get("subject", "").lower() and
                    trip_id_str in t.get("subject", "").lower()
                )
            ]
            
            return signalements
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des signalements: {str(e)}")
            return []
    
    def get_tickets_by_page(self, page: int = 1, page_size: int = 10, status: Optional[str] = None,
                          category: Optional[str] = None, subtype: Optional[str] = None) -> dict:
        """
        Récupère les tickets par page avec optimisations
        
        Args:
            page: Numéro de la page
            page_size: Nombre de tickets par page
            status: Filtre optionnel par statut
            category: Filtre optionnel par catégorie
            subtype: Filtre optionnel par sous-type
            
        Returns:
            Dict contenant les tickets et les informations de pagination
        """
        try:
            # Filtre de base pour le statut
            filters = {}
            if status:
                filters["status"] = status
            
            # Calculer le décalage (offset)
            skip = (page - 1) * page_size
            
            # Récupérer tous les tickets avec le filtre de statut
            all_tickets = self.get_all(
                order_by="created_at",
                order_direction="desc", 
                filters=filters
            )
            
            # Post-traitement pour les filtres de catégorie et sous-type
            filtered_tickets = all_tickets
            
            # Filtre par catégorie
            if category:
                c = (category or "").lower()
                if c == "signalement_trajet":
                    filtered_tickets = [
                        t for t in filtered_tickets if 
                        "[signalement trajet]" in t.get("subject", "").lower()
                    ]
            
            # Filtre par sous-type
            if subtype:
                s = (subtype or "").lower()
                tag_map = {
                    "conducteur_absent": "[conducteur absent]",
                    "conducteur_en_retard": "[conducteur en retard]",
                    "autre": "[autre]",
                }
                tag = tag_map.get(s)
                if tag:
                    filtered_tickets = [
                        t for t in filtered_tickets if
                        tag in t.get("message", "").lower()
                    ]
            
            # Calculer le nombre total après filtrage
            total_count = len(filtered_tickets)
            
            # Appliquer la pagination
            paginated_tickets = filtered_tickets[skip:skip+page_size]
            
            # Calculer le nombre total de pages
            total_pages = max(1, (total_count + page_size - 1) // page_size)
            
            # Retourner les tickets et les informations de pagination
            return {
                "tickets": paginated_tickets,
                "pagination": {
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur get_tickets_by_page: {str(e)}")
            return {
                "tickets": [],
                "pagination": {
                    "total_count": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 1
                }
            }
