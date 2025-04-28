import streamlit as st

def modern_card(title, icon, items, bg_color="#23272c", accent_color="#EBC33F"):
    """
    Affiche une carte moderne et épurée pour Streamlit.
    Args:
        title (str): Titre de la carte
        icon (str): Emoji ou icône
        items (list): Liste de tuples (label, valeur)
        bg_color (str): Couleur de fond de la carte
        accent_color (str): Couleur du titre
    """
    st.markdown(f'''
    <div style="background:{bg_color}; border-radius:12px; padding:22px 18px; margin-bottom:18px; box-shadow:0 2px 12px rgba(0,0,0,0.12);">
        <div style="font-size:18px; font-weight:600; color:{accent_color}; margin-bottom:12px; letter-spacing:0.5px;">
            {icon} {title}
        </div>
        <div style="display:flex; gap:32px;">
            {''.join([f"<div><div style='font-size:13px; color:#bbb;'>{label}</div><div style='font-size:21px; color:#fff; font-weight:600; margin-top:2px;'>{value}</div></div>" for label, value in items])}
        </div>
    </div>
    ''', unsafe_allow_html=True)
