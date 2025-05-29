import streamlit as st
from src.streamlit_apps.pages.components.chats import ChatManager

class TripsChat:
    """Classe responsable de la gestion des fonctionnalités de chat pour les trajets"""
    
    def __init__(self):
        """Initialisation de la classe TripsChat"""
        pass
        
    def display_chat_popup(self, passenger_id, passenger_name, trip_id):
        """Affiche un dialogue de chat pour le passager sélectionné
        
        Args:
            passenger_id (str): ID du passager
            passenger_name (str): Nom du passager
            trip_id (str): ID du trajet
        """
        # Créer un grand dialogue modal pour le chat
        with st.container():
            # Ajouter un bouton pour fermer le dialogue
            st.markdown('''
            <style>
            .chat-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: #102844;
                color: white;
                padding: 10px 15px;
                border-radius: 5px 5px 0 0;
            }
            .chat-dialog {
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                background-color: white;
            }
            .chat-content {
                padding: 15px;
                max-height: 500px;
                overflow-y: auto;
            }
            </style>
            ''', unsafe_allow_html=True)

            st.markdown('<div class="chat-dialog">', unsafe_allow_html=True)
            
            # Entête du dialogue avec le nom du passager et le bouton de fermeture
            header_cols = st.columns([3, 1])
            with header_cols[0]:
                st.markdown(f'<div class="chat-header"><h3>Chat avec {passenger_name}</h3></div>', unsafe_allow_html=True)
            with header_cols[1]:
                if st.button("Fermer", key="close_chat_dialog"):
                    # Réinitialiser les variables de session pour fermer le dialogue
                    st.session_state["show_chat_dialog"] = False
                    st.session_state["chat_with_passenger_id"] = None
                    st.rerun()
            
            # Contenu du chat
            st.markdown('<div class="chat-content">', unsafe_allow_html=True)
            
            # Utiliser le ChatManager pour récupérer et afficher les conversations
            chat_manager = ChatManager()
            
            # Charger les conversations et les filtrer pour ce passager et ce trajet
            chats_df, messages_df, _ = chat_manager.load_chat_data()
            
            if not chats_df.empty:
                # Filtrer les conversations pour ce passager
                # On cherche les conversations où le passager est soit user_a soit user_b
                filtered_chats = chats_df[(chats_df['user_a'] == passenger_id) | (chats_df['user_b'] == passenger_id)]
                
                if not filtered_chats.empty:
                    # Sélectionner la première conversation trouvée
                    selected_chat = filtered_chats.iloc[0]
                    chat_id = selected_chat['chat_id']
                    
                    # Récupérer les messages de cette conversation
                    chat_messages = messages_df[messages_df['chat_id'] == chat_id].copy()
                    
                    if not chat_messages.empty:
                        # Déterminer l'autre utilisateur dans la conversation
                        user_a = selected_chat['user_a']
                        user_b = selected_chat['user_b']
                        
                        # Afficher les messages avec le style approprié
                        chat_manager.display_chat_from_dataframe(chat_messages, user_a, user_b)
                    else:
                        st.info("Aucun message dans cette conversation.")
                else:
                    st.info(f"Aucune conversation trouvée pour {passenger_name}.")
            else:
                st.info("Aucune donnée de chat disponible.")
                
            st.markdown('</div>', unsafe_allow_html=True)  # Fermer chat-content
            st.markdown('</div>', unsafe_allow_html=True)  # Fermer chat-dialog