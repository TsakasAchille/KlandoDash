#!/bin/bash
# Script pour démarrer KlandoDash en mode REST (sans connexion directe PostgreSQL)

# Afficher un message d'information
echo "🚀 Démarrage de KlandoDash en mode REST Supabase"
echo "==================================================="
echo "Ce script configure l'application pour utiliser l'API REST Supabase"
echo "au lieu de la connexion directe à PostgreSQL."
echo

# Variables d'environnement pour forcer l'utilisation de l'API REST
export CONNECTION_MODE="rest"
export FORCE_REST_API="true"

# Activer le mode debug pour voir les logs détaillés
export DASH_DEBUG="true"

# Vérifier si Supabase est configuré
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "⚠️  ATTENTION: Les variables SUPABASE_URL et SUPABASE_KEY ne sont pas définies."
    echo "   Si ces variables ne sont pas configurées dans le fichier .env,"
    echo "   l'application ne pourra pas se connecter à Supabase."
    echo
    echo "   Vous pouvez les définir dans le fichier .env ou en ligne de commande:"
    echo "   export SUPABASE_URL=https://votre-projet.supabase.co"
    echo "   export SUPABASE_KEY=votre-clé-anon"
    echo
fi

# Démarrer l'application
echo "📡 Démarrage de l'application en mode REST..."
echo "   Logs de debug activés (DASH_DEBUG=true)"
echo

# Vérifier si on doit utiliser python ou python3
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Démarrer l'application
# Selon le Procfile, le point d'entrée est dash_apps.app:server
$PYTHON_CMD -m dash_apps.app
