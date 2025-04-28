import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from src.streamlit_apps.components import Table, Styles, setup_page
# Corriger l'importation des composants Streamlit
import streamlit.components.v1 as stcomp
from src.core.database import Chat, get_session

class ChatManager:
    """
    Classe pour gérer l'affichage et l'interaction avec les conversations.
    Encapsule toutes les fonctions liées aux chats.
    """
    
    def __init__(self):
        """Initialisation de la classe ChatManager"""
        pass
    
    @st.cache_data(ttl=300)  # Cache les données pendant 5 minutes
    def load_chat_data(_self):
        """
        Charge les données de chat directement depuis PostgreSQL et les structure en DataFrames
        
        Returns:
            tuple: (chats_df, messages_df, raw_data) - DataFrames des conversations et messages, et données brutes
        """
        try:
            print("Récupération des chats depuis PostgreSQL...")
            session = get_session()
            chats = session.query(Chat).all()
            chats_data = [chat.to_dict() for chat in chats]
            session.close()
            
            if not chats_data:
                print("Aucun chat trouvé dans la base de données.")
                return pd.DataFrame(), pd.DataFrame(), {}
                
            # Créer le DataFrame directement à partir des données
            chats_df = pd.DataFrame(chats_data)
            
            # Pour la compat à retravailler plus tard
            messages_df = pd.DataFrame()  # Tableau vide pour l'instant
            raw_data = {}  # Données brutes vides pour l'instant
            
            # Conversion des dates
            date_columns = ['timestamp', 'updated_at']
            for col in date_columns:
                if col in chats_df.columns:
                    chats_df[col] = pd.to_datetime(chats_df[col], errors='coerce')
            
            print(f"Chargement réussi de {len(chats_df)} chats")
            return chats_df, messages_df, raw_data
            
        except Exception as e:
            print(f"Erreur lors du chargement des chats: {e}")
            return pd.DataFrame(), pd.DataFrame(), {}
    
    def display_chat_interface(self):
        """
        Affiche l'interface principale des chats avec sélection de conversation
        et affichage des messages en utilisant les DataFrames
        """
        st.title("Messages")
        
        # Charger les données structurées en DataFrames
        chats_df, messages_df, raw_data = self.load_chat_data()
        
        if chats_df.empty:
            st.warning("Aucune conversation disponible.")
            return
            
        # Interface à deux colonnes
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Conversations")
            
            # Créer une liste lisible pour l'affichage dans le selectbox
            # Format: "Trip ID (X messages)"
            display_options = [f"{row['trip_ref']} ({row['message_count']} msgs)" for _, row in chats_df.iterrows()]
            
            # Afficher la liste des conversations
            if display_options:
                selected_index = st.selectbox(
                    "Sélectionner une conversation",
                    range(len(display_options)),
                    format_func=lambda i: display_options[i]
                )
                
                # Afficher des informations supplémentaires sur la conversation sélectionnée
                if selected_index is not None:
                    selected_row = chats_df.iloc[selected_index]
                    st.info(f"Participants: {selected_row['user_a']} et {selected_row['user_b']}")
                    
                    # Afficher la date du dernier message si disponible
                    if selected_row['last_message_time']:
                        try:
                            last_msg_time = pd.to_datetime(selected_row['last_message_time'].replace('Z', '+00:00'))
                            st.caption(f"Dernier message: {last_msg_time.strftime('%d/%m/%Y %H:%M')}")
                        except:
                            st.caption(f"Dernier message: {selected_row['last_message_time']}")
            
        # Afficher les messages de la conversation sélectionnée
        if 'selected_index' in locals() and selected_index is not None:
            selected_chat_id = chats_df.iloc[selected_index]['chat_id']
            selected_trip = chats_df.iloc[selected_index]['trip_ref']
            user_a = chats_df.iloc[selected_index]['user_a']
            user_b = chats_df.iloc[selected_index]['user_b']
            
            # Filtrer les messages pour cette conversation
            chat_messages = messages_df[messages_df['chat_id'] == selected_chat_id].copy()
            
            with col2:
                st.subheader(f"Conversation: {selected_trip}")
                
                if not chat_messages.empty:
                    # Utiliser la méthode d'affichage adaptée aux DataFrames
                    self.display_chat_from_dataframe(chat_messages, user_a, user_b)
                else:
                    st.info("Aucun message dans cette conversation.")
    
    def display_chat_modern_alternative(self, messages, user_a, user_b):
        """
        Affiche les messages avec un style moderne, optimisé pour les messages audio
        Utilise des colonnes Streamlit pour contrôler la largeur des lecteurs audio
        """
        # CSS pour les messages texte uniquement
        st.markdown("""
        <style>
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 10px;
        }
        .message {
            max-width: 80%;
            padding: 10px 15px;
            border-radius: 18px;
            position: relative;
            margin-bottom: 8px;
        }
        .message-a {
            align-self: flex-start;
            background-color: #34C759;
            color: black;
            border-bottom-left-radius: 5px;
        }
        .message-b {
            align-self: flex-end;
            background-color: #0084ff;
            color: white;
            border-bottom-right-radius: 5px;
        }
        .timestamp {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 4px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Container pour les messages
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for message in messages:
            msg_data = message['data']
            msg_user = msg_data['user'].split('/')[-1]
            is_user_a = msg_user == user_a
            timestamp = datetime.fromisoformat(msg_data['timestamp'].replace('Z', '+00:00'))
            
            # Message audio - version avec colonnes pour forcer la largeur
            if 'audio_url' in msg_data:
                # Utiliser plus de colonnes pour un contrôle plus fin
                # Largeur totale = 10 colonnes
                if is_user_a:
                    cols = st.columns([2, 2, 3])  # Audio à gauche
                    col_idx = 0  # Utiliser la première colonne
                else:
                    cols = st.columns([3, 2, 2])  # Audio à droite
                    col_idx = 2  # Utiliser la dernière colonne
                
                with cols[col_idx]:
                    st.audio(msg_data['audio_url'])
                    st.markdown(f"<div class='timestamp'>{timestamp.strftime('%H:%M')}</div>", unsafe_allow_html=True)
            
            # Message texte standard - inchangé
            else:
                message_class = "message message-a" if is_user_a else "message message-b"
                align = "left" if is_user_a else "right"
                
                html = f'<div style="display: flex; justify-content: {align}"><div class="{message_class}">'
                
                if 'message' in msg_data:
                    html += f"{msg_data['message']}"
                
                html += f'<div class="timestamp">{timestamp.strftime("%H:%M")}</div>'
                html += '</div></div>'
                
                st.markdown(html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_chat_modern(self, messages, user_a, user_b):
        """
        Affiche les messages avec un style moderne (version originale)
        Gère les messages audio avec des placeholders
        """
        # CSS amélioré pour les bulles de conversation avec support audio
        st.markdown("""
        <style>
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 10px;
        }
        .message {
            max-width: 80%;
            padding: 10px 15px;
            border-radius: 18px;
            position: relative;
            margin-bottom: 8px;
        }
        .message-a {
            align-self: flex-start;
            background-color: #e5e5ea;
            color: black;
            border-bottom-left-radius: 5px;
        }
        .message-b {
            align-self: flex-end;
            background-color: #0084ff;
            color: white;
            border-bottom-right-radius: 5px;
        }
        .timestamp {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 4px;
        }
        .audio-placeholder {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 5px;
            border-radius: 8px;
            background-color: rgba(0,0,0,0.05);
            margin: 5px 0;
        }
        .audio-icon {
            font-size: 18px;
        }
        .audio-info {
            font-size: 12px;
        }
        /* Classe pour le div vide comme espace réservé */
        .audio-element {
            height: 50px;
            margin: 5px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Itérer sur les messages pour identifier les messages audio
        audio_elements = []
        
        # Container pour les messages
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for i, message in enumerate(messages):
            msg_data = message['data']
            msg_user = msg_data['user'].split('/')[-1]
            is_user_a = msg_user == user_a
            timestamp = datetime.fromisoformat(msg_data['timestamp'].replace('Z', '+00:00'))
            
            # Créer la bulle de message
            message_class = "message message-a" if is_user_a else "message message-b"
            align = "left" if is_user_a else "right"
            
            html = f'<div style="display: flex; justify-content: {align}"><div class="{message_class}">'
            
            # Contenu du message
            if 'audio_url' in msg_data:
                # Créer un identifiant unique pour cet élément audio
                audio_id = f"audio-{i}"
                duration_seconds = msg_data['audio_duration'] / 1000
                
                # Ajouter un indicateur visuel pour l'audio
                html += f"""<div class="audio-placeholder">
                            <div class="audio-icon">🔊</div>
                            <div class="audio-info">Message vocal ({duration_seconds:.1f}s)</div>
                          </div>
                          <div id="{audio_id}" class="audio-element"></div>"""
                
                # Stocker l'URL audio pour insertion ultérieure
                audio_elements.append((audio_id, msg_data['audio_url']))
            elif 'message' in msg_data:
                html += f"{msg_data['message']}"
            
            # Ajouter timestamp
            html += f'<div class="timestamp">{timestamp.strftime("%H:%M")}</div>'
            html += '</div></div>'
            
            st.markdown(html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Maintenant insérer les éléments audio dans les emplacements réservés
        for audio_id, audio_url in audio_elements:
            # Version simplifiée sans le paramètre key
            with st.container():
                # Script pour tenter de déplacer l'élément audio au bon endroit
                stcomp.html(f"""
                <script>
                    // Fonction pour déplacer l'élément audio au bon endroit
                    function moveAudio() {{
                        const audioContainers = document.querySelectorAll('[data-testid="element-container"]');
                        const lastAudioContainer = audioContainers[audioContainers.length - 1];
                        const targetElement = document.getElementById('{audio_id}');
                        if (lastAudioContainer && targetElement) {{
                            targetElement.appendChild(lastAudioContainer);
                        }}
                    }}
                    
                    // Attendre que le DOM soit complètement chargé
                    setTimeout(moveAudio, 500);
                </script>
                """, height=0)
                
                st.audio(audio_url)
    
    def display_chat_professional(self, messages, user_a, user_b):
        """
        Affiche les messages avec un style professionnel
        """
        # CSS pour les bulles de style professionnel
        st.markdown("""
        <style>
        .chat-pro-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            padding: 10px;
        }
        .pro-message {
            max-width: 90%;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .pro-message-a {
            align-self: flex-start;
            border-left: 4px solid #36c5f0;
            background-color: #f8f8f8;
        }
        .pro-message-b {
            align-self: flex-end;
            border-left: 4px solid #2eb67d;
            background-color: #f8f8f8;
        }
        .pro-sender {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .pro-sender-a {
            color: #36c5f0;
        }
        .pro-sender-b {
            color: #2eb67d;
        }
        .pro-timestamp {
            font-size: 11px;
            color: #999;
            margin-top: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Container pour les messages
        st.markdown('<div class="chat-pro-container">', unsafe_allow_html=True)
        
        for message in messages:
            msg_data = message['data']
            msg_user = msg_data['user'].split('/')[-1]
            is_user_a = msg_user == user_a
            timestamp = datetime.fromisoformat(msg_data['timestamp'].replace('Z', '+00:00'))
            
            # Classes selon l'expéditeur
            message_class = "pro-message pro-message-a" if is_user_a else "pro-message pro-message-b"
            sender_class = "pro-sender pro-sender-a" if is_user_a else "pro-sender pro-sender-b"
            align = "left" if is_user_a else "right"
            
            html = f'<div style="display: flex; justify-content: {align}"><div class="{message_class}">'
            html += f'<div class="{sender_class}">{user_a if is_user_a else user_b}</div>'
            
            # Contenu du message
            if 'audio_url' in msg_data:
                # Pour les messages audio, on utilise un composant Streamlit séparé
                st.markdown(html+'</div></div>', unsafe_allow_html=True)
                st.audio(msg_data['audio_url'])
                continue  # On passe au message suivant
            elif 'message' in msg_data:
                html += f"<div>{msg_data['message']}</div>"
            
            # Ajouter timestamp
            html += f'<div class="pro-timestamp">{timestamp.strftime("%d/%m/%Y %H:%M")}</div>'
            html += '</div></div>'
            
            if html:  # Si le HTML n'a pas été vidé pour un audio
                st.markdown(html, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_chat_comic(self, messages, user_a, user_b):
        """
        Affiche les messages avec un style BD (comic)
        """
        # CSS pour les bulles avec queues
        st.markdown("""
        <style>
        .comic-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            padding: 15px;
        }
        .comic-message {
            max-width: 75%;
            padding: 12px;
            border-radius: 12px;
            position: relative;
        }
        .comic-message-a {
            align-self: flex-start;
            background-color: #f0f0f0;
            margin-left: 15px;
        }
        .comic-message-a:before {
            content: '';
            position: absolute;
            left: -10px;
            top: 15px;
            border-style: solid;
            border-width: 10px 10px 10px 0;
            border-color: transparent #f0f0f0 transparent transparent;
        }
        .comic-message-b {
            align-self: flex-end;
            background-color: #dcf8c6;
            margin-right: 15px;
        }
        .comic-message-b:after {
            content: '';
            position: absolute;
            right: -10px;
            top: 15px;
            border-style: solid;
            border-width: 10px 0 10px 10px;
            border-color: transparent transparent transparent #dcf8c6;
        }
        .comic-sender {
            font-size: 13px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .comic-timestamp {
            font-size: 10px;
            color: #888;
            text-align: right;
            margin-top: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Container pour les messages
        st.markdown('<div class="comic-container">', unsafe_allow_html=True)
        
        for message in messages:
            msg_data = message['data']
            msg_user = msg_data['user'].split('/')[-1]
            is_user_a = msg_user == user_a
            timestamp = datetime.fromisoformat(msg_data['timestamp'].replace('Z', '+00:00'))
            
            # Classes selon l'expéditeur
            message_class = "comic-message comic-message-a" if is_user_a else "comic-message comic-message-b"
            align = "left" if is_user_a else "right"
            
            html = f'<div style="display: flex; justify-content: {align}"><div class="{message_class}">'
            html += f'<div class="comic-sender">{user_a if is_user_a else user_b}</div>'
            
            # Contenu du message
            if 'audio_url' in msg_data:
                st.markdown(html+'</div></div>', unsafe_allow_html=True)
                st.audio(msg_data['audio_url'])
                continue  # On passe au message suivant
            elif 'message' in msg_data:
                html += f"<div>{msg_data['message']}</div>"
            
            # Ajouter timestamp
            html += f'<div class="comic-timestamp">{timestamp.strftime("%H:%M")}</div>'
            html += '</div></div>'
            
            st.markdown(html, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_chat_from_dataframe(self, messages_df, user_a, user_b):
        """
        Affiche les messages depuis un DataFrame structuré
        
        Args:
            messages_df (DataFrame): DataFrame contenant les messages
            user_a (str): Identifiant du premier utilisateur
            user_b (str): Identifiant du deuxième utilisateur
        """
        # CSS pour les messages texte
        st.markdown("""
        <style>
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 10px;
        }
        .message {
            max-width: 80%;
            padding: 10px 15px;
            border-radius: 18px;
            position: relative;
            margin-bottom: 8px;
        }
        .message-a {
            align-self: flex-start;
            background-color: #34C759;
            color: black;
            border-bottom-left-radius: 5px;
        }
        .message-b {
            align-self: flex-end;
            background-color: #0084ff;
            color: white;
            border-bottom-right-radius: 5px;
        }
        .timestamp {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 4px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Container pour les messages
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Statistiques de la conversation
        total_msgs = len(messages_df)
        audio_msgs = messages_df['has_audio'].sum()
        text_msgs = total_msgs - audio_msgs
        
        # Afficher les statistiques
        st.caption(f"Total: {total_msgs} messages ({audio_msgs} vocaux, {text_msgs} texte)")
        
        # Traiter chaque message du DataFrame
        for _, msg in messages_df.iterrows():
            sender = msg['sender']
            is_user_a = msg['is_user_a']
            timestamp = msg['timestamp']
            
            # Message audio
            if msg['has_audio']:
                # Utiliser des colonnes pour contrôler la largeur
                if is_user_a:
                    cols = st.columns([2, 2, 3])  # Audio à gauche
                    col_idx = 0  # Première colonne
                else:
                    cols = st.columns([3, 2, 2])  # Audio à droite
                    col_idx = 2  # Dernière colonne
                
                with cols[col_idx]:
                    st.audio(msg['audio_url'])
                    st.markdown(f"<div class='timestamp'>{timestamp.strftime('%H:%M')}</div>", unsafe_allow_html=True)
            
            # Message texte
            elif msg['message_text']:
                message_class = "message message-a" if is_user_a else "message message-b"
                align = "left" if is_user_a else "right"
                
                html = f'<div style="display: flex; justify-content: {align}"><div class="{message_class}">{msg["message_text"]}<div class="timestamp">{timestamp.strftime("%H:%M")}</div></div></div>'
                
                st.markdown(html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Afficher des options d'analyse si demandé
        with st.expander("Analyse de la conversation"):
            # Distribution des messages par utilisateur
            st.subheader("Distribution des messages")
            
            # Compter les messages par expéditeur
            msg_counts = messages_df['sender'].value_counts()
            
            # Convertir en DataFrame pour l'affichage
            counts_df = pd.DataFrame({
                'Utilisateur': msg_counts.index,
                'Messages': msg_counts.values
            })
            
            # Ajouter une colonne pour indiquer si c'est user_a
            counts_df['Est User A'] = counts_df['Utilisateur'] == user_a
            
            # Afficher le tableau des comptages
            st.dataframe(counts_df)
            
            # Histogramme des messages par heure du jour
            st.subheader("Messages par heure du jour")
            if 'timestamp' in messages_df.columns:
                # Extraire l'heure
                messages_df['hour'] = messages_df['timestamp'].dt.hour
                
                # Histogramme
                hour_counts = messages_df['hour'].value_counts().sort_index()
                
                # Générer des étiquettes horaires pour tous les points de 0 à 23
                hour_labels = {i: f"{i:02d}:00" for i in range(24)}
                
                # Afficher l'histogramme
                st.bar_chart(hour_counts)
    
    def display_audio(self, audio_url):
        """
        Affiche un élément audio avec une taille contrôlée
        """
        st.audio(audio_url)
