import streamlit as st
import pandas as pd
from .users_profile import UsersProfileManager
from .users_stats import UsersStatsManager
from .users_trips import UsersTripsManager
from src.data_processing.processors.user_processor import UserProcessor
from src.streamlit_apps.components.modern_card import modern_card
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import io
import pandas as pd
from fpdf import FPDF

# Lazy loading des managers pour éviter les dépendances circulaires
_profile_manager = None
_stats_manager = None
_trips_manager = None

def _get_profile_manager():
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = UsersProfileManager()
    return _profile_manager

def _get_stats_manager():
    global _stats_manager
    if _stats_manager is None:
        _stats_manager = UsersStatsManager()
    return _stats_manager

def _get_trips_manager():
    global _trips_manager
    if _trips_manager is None:
        _trips_manager = UsersTripsManager()
    return _trips_manager

# Fonction pour initialiser/récupérer les données
def get_user_data():
    """Récupère les données des utilisateurs depuis la base de données"""
    return UserProcessor.get_all_users()

# === Fonctions de tableau ===
def display_users_table(users_df, pre_selected_user_id=None):
    """Affiche le tableau des utilisateurs et gère la sélection
    
    Args:
        users_df: DataFrame contenant les données des utilisateurs
        pre_selected_user_id: ID de l'utilisateur à présélectionner
        
    Returns:
        dict: Informations sur la sélection (selected_rows, etc.)
    """
    # Colonnes à afficher dans la table
    display_cols = [
        'id',
        'uid',  # Ajouter le champ uid qui est crucial pour les liens
        'display_name',
        'name',
        'email',
        'phone_number'
    ]
    
    # Filtrer les colonnes existantes
    valid_cols = [col for col in display_cols if col in users_df.columns]
        
    # Configuration de la grille avec case à cocher
    gb = GridOptionsBuilder.from_dataframe(users_df[valid_cols])
    gb.configure_selection('single', use_checkbox=True)
    gb.configure_grid_options(suppressRowClickSelection=True)
    
    # Sélectionner automatiquement l'utilisateur si demandé
    if pre_selected_user_id and 'uid' in users_df.columns:
        user_row_index = users_df[users_df['uid'] == pre_selected_user_id].index.tolist()
        if user_row_index:
            gb.configure_selection('single', use_checkbox=True, pre_selected_rows=[user_row_index[0]])
    
    # Afficher la grille
    grid_response = AgGrid(
        users_df[valid_cols],
        gridOptions=gb.build(),
        fit_columns_on_grid_load=False,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=700,
    )
    
    return grid_response

# === Fonctions d'affichage du profil ===
def display_profile_info(user_data):
    """Affiche les informations de profil de l'utilisateur
    
    Args:
        user_data: Données de l'utilisateur à afficher (dictionnaire)
    """
    return _get_profile_manager().display_profile_info(user_data)

# === Fonctions d'affichage des statistiques ===
def display_stats_info(user_data):
    """Affiche les statistiques de l'utilisateur
    
    Args:
        user_data: Données de l'utilisateur à afficher (dictionnaire)
    """
    return _get_stats_manager().display_stats_info(user_data)

# === Fonctions d'affichage des trajets ===
def display_trips_info(user_data):
    """Affiche les trajets associés à l'utilisateur
    
    Args:
        user_data: Données de l'utilisateur à afficher (dictionnaire)
    """
    return _get_trips_manager().display_trips_info(user_data)

# === Fonctions d'affichage des types de transaction ===
def display_user_transaction_types(user_data):
    """Affiche les types de transaction utilisés par l'utilisateur (via UID uniquement, affichage moderne)"""
    import streamlit as st
    from src.data_processing.processors.user_processor import UserProcessor
    from src.streamlit_apps.components.modern_card import modern_card
    uid = user_data.get('uid')
    if not uid:
        st.info("UID utilisateur non trouvé pour les transactions.")
        return
    types = UserProcessor.get_user_transaction_types(uid)
    if types and types != ["Aucune transaction"]:
        try:
            modern_card(
                title="Types de transaction utilisés",
                icon="💸",
                items=types,  
                accent_color="#f39c12"
            )
        except Exception:
            modern_card(
                title="Types de transaction utilisés",
                icon="💸",
                items=[("", t) for t in types],
                accent_color="#f39c12"
            )
    else:
        st.info("Aucune transaction trouvée pour cet utilisateur.")

# === Fonctions d'export ===
def clean_latin1(text):
    if not isinstance(text, str):
        text = str(text)
    try:
        text.encode('latin1')
        return text
    except UnicodeEncodeError:
        # Remplace les caractères non latin1 par '?'
        cleaned = text.encode('latin1', errors='replace').decode('latin1')
        import streamlit as st
        st.warning("Certains caractères spéciaux non supportés par le PDF ont été remplacés par '?'")
        return cleaned

def remove_timezone_from_df(df):
    """Supprime le timezone des colonnes datetime64 de DataFrame (Excel ne supporte pas tz-aware)."""
    for col in df.select_dtypes(include=["datetimetz", "datetime"]):
        # On ne retire le tz que si la colonne est tz-aware
        if hasattr(df[col].dtype, 'tz') and df[col].dtype.tz is not None:
            df[col] = df[col].dt.tz_localize(None)
    return df

def remove_timezone_from_dict(d):
    """Supprime le timezone des champs datetime dans un dictionnaire."""
    for k, v in d.items():
        if hasattr(v, 'tzinfo') and v.tzinfo is not None:
            d[k] = v.replace(tzinfo=None)
    return d

def export_user_to_excel(user_data, trips=None, stats=None, transaction_types=None):
    try:
        import xlsxwriter
    except ImportError:
        import streamlit as st
        st.error("Le module xlsxwriter n'est pas installé. Faites : pip install xlsxwriter")
        return None
    import copy
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        # Nettoyage timezone pour user_data et stats (dict)
        user_data_clean = remove_timezone_from_dict(copy.deepcopy(user_data))
        pd.DataFrame([user_data_clean]).to_excel(writer, sheet_name="Profil", index=False)
        if stats is not None:
            stats_clean = remove_timezone_from_dict(copy.deepcopy(stats))
            pd.DataFrame([stats_clean]).to_excel(writer, sheet_name="Statistiques", index=False)
        if trips is not None and not trips.empty:
            trips_clean = remove_timezone_from_df(trips.copy())
            trips_clean.to_excel(writer, sheet_name="Trajets", index=False)
        if transaction_types is not None:
            pd.DataFrame({"Types de transaction": transaction_types}).to_excel(writer, sheet_name="Transactions", index=False)
        writer.save()
    output.seek(0)
    return output

def export_user_to_pdf(user_data, trips=None, stats=None, transaction_types=None):
    pdf = FPDF()
    pdf.add_page()
    import os
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdf.add_font('DejaVu', '', font_path, uni=True)
        font_name = "DejaVu"
    else:
        font_name = "Arial"
    pdf.set_font(font_name, size=12)
    nomprenom = f"{user_data.get('first_name','')} {user_data.get('name','')}".strip()
    titre = clean_latin1(f"Fiche Utilisateur Klando : {nomprenom if nomprenom else user_data.get('display_name','')}")
    pdf.cell(0, 10, titre, ln=1, align="C")
    pdf.ln(5)
    pdf.set_font(font_name, size=10)
    pdf.cell(0, 8, clean_latin1("Profil"), ln=1)
    for k, v in user_data.items():
        val = '-' if v is None else v
        pdf.cell(0, 7, clean_latin1(f"{k}: {val}"), ln=1)
    if stats:
        pdf.ln(3)
        pdf.cell(0, 8, clean_latin1("Statistiques"), ln=1)
        for k, v in stats.items():
            val = '-' if v is None else v
            pdf.cell(0, 7, clean_latin1(f"{k}: {val}"), ln=1)
    if trips is not None and not trips.empty:
        pdf.ln(3)
        pdf.cell(0, 8, clean_latin1("Trajets"), ln=1)
        trip_fields = [
            ("ID du trajet", "trip_id"),
            ("Date de départ", "departure_date"),
            ("Date de création", "created_at"),
            ("Ville de départ", "departure_city"),
            ("Ville d'arrivée", "arrival_city"),
            ("Statut", "status")
        ]
        for idx, row in trips.iterrows():
            for label, key in trip_fields:
                val = row.get(key, '-')
                if pd.isnull(val) or val is None:
                    val = '-'
                # Format date si Timestamp
                if 'date' in key and val != '-' and hasattr(val, 'strftime'):
                    val = val.strftime("%Y-%m-%d %H:%M")
                pdf.cell(0, 7, clean_latin1(f"{label}: {val}"), ln=1)
            pdf.ln(2)
    if transaction_types:
        pdf.ln(3)
        pdf.cell(0, 8, clean_latin1("Types de transaction"), ln=1)
        for t in transaction_types:
            pdf.cell(0, 7, clean_latin1(t), ln=1)
    pdf_output = io.BytesIO(pdf.output(dest='S').encode('latin1'))
    return pdf_output

# === Fonction complète d'affichage des informations utilisateur ===
def display_user_info(user_data):
    """Affiche toutes les informations d'un utilisateur + export Excel/PDF"""
    import streamlit as st
    from src.data_processing.processors.user_processor import UserProcessor
    from src.data_processing.processors.trip_processor import TripProcessor
    # Profil
    display_profile_info(user_data)
    # Statistiques (pour affichage)
    display_stats_info(user_data)
    # Statistiques (pour export)
    total_trips_count, driver_trips_count, passenger_trips_count, total_distance, total_seats = _get_stats_manager()._calculate_user_stats(user_data.get('uid'))
    stats = {
        "Trajets effectués (total)": total_trips_count,
        "Trajets en tant que conducteur": driver_trips_count,
        "Trajets en tant que passager": passenger_trips_count,
        "Distance totale": f"{total_distance:.1f} km",
        "Places réservées": total_seats
    }
    # Trajets
    user_id = user_data.get('uid')
    trips_df = _get_trips_manager()._get_user_trips(user_id)
    display_trips_info(user_data)
    # Types de transaction
    transaction_types = UserProcessor.get_user_transaction_types(user_data.get('uid'))
    display_user_transaction_types(user_data)
    # Boutons d'export
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Exporter la fiche en Excel"):
            excel = export_user_to_excel(user_data, trips_df, stats, transaction_types)
            st.download_button(
                label="Télécharger Excel",
                data=excel,
                file_name=f"fiche_utilisateur_{user_data.get('uid','user')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    with col2:
        if st.button("Exporter la fiche en PDF"):
            pdf = export_user_to_pdf(user_data, trips_df, stats, transaction_types)
            st.download_button(
                label="Télécharger PDF",
                data=pdf,
                file_name=f"fiche_utilisateur_{user_data.get('uid','user')}.pdf",
                mime="application/pdf"
            )
