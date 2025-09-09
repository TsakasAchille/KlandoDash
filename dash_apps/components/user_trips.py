from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
from dash_apps.utils.data_schema_rest import get_trips_for_user
import datetime

# Initialisation de Jinja2 pour le template des trajets utilisateur
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir))
user_trips_template = env.get_template("user_trips_template.jinja2")

# Fonction pour formater les dates
def format_date(value):
    if isinstance(value, (datetime.datetime, pd.Timestamp)):
        return value.strftime("%d/%m/%Y %H:%M")
    return str(value)

# Styles communs pour une cohérence visuelle
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '28px',
    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
    'padding': '0px',
    'overflow': 'hidden',
    'marginBottom': '16px'
}

def render_user_trips(user_id=None, data=None, user=None):
    """
    Affiche les trajets effectués par l'utilisateur en utilisant un template Jinja2.
    
    Args:
        user_id: ID de l'utilisateur (pour le système générique)
        data: Données des trajets (DataFrame, pour le système générique)
        user: Données de l'utilisateur complètes (dict, pour l'ancien système)
    """
    print(f"[TRIPS_DEBUG] === DÉBUT RENDER_USER_TRIPS ===")
    print(f"[TRIPS_DEBUG] Paramètres reçus:")
    print(f"[TRIPS_DEBUG]   - user_id: {user_id}")
    print(f"[TRIPS_DEBUG]   - data type: {type(data)}")
    print(f"[TRIPS_DEBUG]   - user type: {type(user)}")
    
    # Gestion des différents modes d'appel
    if user_id and data is not None:
        # Mode générique: appelé par le système de panneaux avec user_id et data
        actual_user_id = user_id
        trips_df = data if isinstance(data, pd.DataFrame) else pd.DataFrame()
        print(f"[TRIPS_DEBUG] Mode générique activé")
        print(f"[TRIPS_DEBUG] DataFrame reçu: {len(trips_df)} lignes")
        if not trips_df.empty:
            print(f"[TRIPS_DEBUG] Colonnes DataFrame: {list(trips_df.columns)}")
        print(f"[TRIPS] Mode générique - {len(trips_df)} trajets fournis pour {actual_user_id[:8]}...")
    elif user is not None:
        # Mode legacy: appelé directement avec un dict user
        actual_user_id = user.get('uid')
        print(f"[TRIPS_DEBUG] Mode legacy activé pour user: {actual_user_id}")
        if 'trips' in user:
            trips_df = user['trips']
            print(f"[TRIPS_DEBUG] Trajets trouvés dans user dict: {len(trips_df)} trajets")
            print(f"[TRIPS] Trajets récupérés du cache pour {actual_user_id[:8]}...")
        else:
            # Fallback: charger depuis DB si pas en cache
            try:
                print(f"[TRIPS_DEBUG] Pas de trajets en cache, chargement depuis DB...")
                print(f"[TRIPS] Chargement trajets optimisés pour {actual_user_id[:8]}... depuis DB")
                from dash_apps.utils.data_schema_rest import get_user_trips_with_role
                
                trips_df = get_user_trips_with_role(str(actual_user_id), limit=50)
                print(f"[TRIPS_DEBUG] Résultat DB: {len(trips_df)} trajets")
                print(f"[TRIPS] {len(trips_df)} trajets récupérés (optimisé)")
            except Exception as e:
                print(f"[TRIPS_DEBUG] Erreur chargement DB: {e}")
                trips_df = pd.DataFrame()
    else:
        # Aucune donnée fournie
        print(f"[TRIPS_DEBUG] Aucune donnée fournie, retour None")
        return None
    
    db_error = False
    trips_data = []
        
    # Préparation des données pour l'affichage
    print(f"[TRIPS_DEBUG] === PRÉPARATION DONNÉES AFFICHAGE ===")
    print(f"[TRIPS_DEBUG] trips_df type: {type(trips_df)}")
    print(f"[TRIPS_DEBUG] trips_df empty: {trips_df.empty if isinstance(trips_df, pd.DataFrame) else 'N/A'}")
    
    try:
        if isinstance(trips_df, pd.DataFrame) and not trips_df.empty and 'trip_id' in trips_df.columns:
            print(f"[TRIPS_DEBUG] Conditions DataFrame remplies, traitement {len(trips_df)} trajets")
            for idx, trip in trips_df.iterrows():
                print(f"[TRIPS_DEBUG] Traitement trajet {idx}: {trip.get('trip_id', 'NO_ID')}")
                trip_dict = trip.to_dict()
                
                # Formater les dates
                if 'departure_schedule' in trip_dict:
                    original_date = trip_dict['departure_schedule']
                    trip_dict['departure_schedule'] = format_date(trip_dict['departure_schedule'])
                    print(f"[TRIPS_DEBUG] Date formatée: {original_date} -> {trip_dict['departure_schedule']}")
                if 'created_at' in trip_dict:
                    trip_dict['created_at'] = format_date(trip_dict['created_at'])  
                
                # Le rôle est déjà inclus dans la requête optimisée
                print(f"[TRIPS_DEBUG] Rôle trajet: {trip_dict.get('role', 'NO_ROLE')}")
                trips_data.append(trip_dict)
            
            print(f"[TRIPS_DEBUG] {len(trips_data)} trajets ajoutés à trips_data")
        else:
            print(f"[TRIPS_DEBUG] Conditions DataFrame non remplies:")
            print(f"[TRIPS_DEBUG]   - isinstance DataFrame: {isinstance(trips_df, pd.DataFrame)}")
            print(f"[TRIPS_DEBUG]   - not empty: {not trips_df.empty if isinstance(trips_df, pd.DataFrame) else 'N/A'}")
            print(f"[TRIPS_DEBUG]   - has trip_id: {'trip_id' in trips_df.columns if isinstance(trips_df, pd.DataFrame) else 'N/A'}")
            
    except Exception as e:
        import traceback
        print(f"[TRIPS_DEBUG] ERREUR lors du traitement des trajets: {str(e)}")
        print(f"[TRIPS_DEBUG] Traceback complet:")
        print(traceback.format_exc())
        print(f"Erreur lors de la récupération des trajets utilisateur: {str(e)}")
        print(traceback.format_exc())
        db_error = True
    
    # Trier par date de départ (du plus récent au plus ancien)
    print(f"[TRIPS_DEBUG] === TRI DES TRAJETS ===")
    print(f"[TRIPS_DEBUG] Nombre de trajets avant tri: {len(trips_data)}")
    try:
        trips_data = sorted(trips_data, key=lambda x: x.get('departure_schedule', ''), reverse=True)
        print(f"[TRIPS_DEBUG] Tri réussi, {len(trips_data)} trajets triés")
    except Exception as e:
        print(f"[TRIPS_DEBUG] Erreur lors du tri: {e}")
        # En cas d'erreur de tri, continuer avec l'ordre actuel
        pass
    
    # Rendu du template HTML avec Jinja2
    print(f"[TRIPS_DEBUG] === RENDU TEMPLATE ===")
    print(f"[TRIPS_DEBUG] Données pour template:")
    print(f"[TRIPS_DEBUG]   - trips: {len(trips_data)} trajets")
    print(f"[TRIPS_DEBUG]   - db_error: {db_error}")
    
    try:
        html_content = user_trips_template.render(
            trips=trips_data,
            db_error=db_error
        )
        print(f"[TRIPS_DEBUG] Template rendu avec succès, taille HTML: {len(html_content)} caractères")
    except Exception as e:
        print(f"[TRIPS_DEBUG] ERREUR rendu template: {e}")
        import traceback
        print(f"[TRIPS_DEBUG] Traceback template:")
        print(traceback.format_exc())
        # Fallback en cas d'erreur de template
        html_content = f"<div>Erreur de rendu: {e}</div>"
    
    # Afficher le template dans un iframe
    print(f"[TRIPS_DEBUG] === CRÉATION COMPOSANT DASH ===")
    print(f"[TRIPS_DEBUG] Création iframe avec HTML de {len(html_content)} caractères")
    
    result = html.Div(
        html.Iframe(
            srcDoc=html_content,
            style={
                'width': '100%',
                'height': '500px',  # Hauteur adaptative pour la liste des trajets
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            sandbox='allow-scripts allow-top-navigation',
        ),
        style=CARD_STYLE
    )
    
    print(f"[TRIPS_DEBUG] === FIN RENDER_USER_TRIPS ===")
    print(f"[TRIPS_DEBUG] Composant créé: {type(result)}")
    return result
