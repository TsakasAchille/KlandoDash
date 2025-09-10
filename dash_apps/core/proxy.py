# Proxy supprimé - MapLibre utilise maintenant directement Firebase
# Plus besoin de proxy complexe

from flask import Blueprint

proxy_bp = Blueprint('proxy', __name__)

# Toutes les routes proxy ont été supprimées
# MapLibre accède directement au style Firebase avec clé API
