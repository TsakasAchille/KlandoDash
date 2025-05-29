#!/bin/bash

# Script de nettoyage du repository KlandoDash
# Ce script:
# 1. Crée une sauvegarde du dossier src
# 2. Supprime les éléments obsolètes du repository

echo "Début du nettoyage du repository KlandoDash..."

# Vérifier si le dossier dash_apps existe
if [ ! -d "dash_apps" ]; then
    echo "ERREUR: Le dossier dash_apps n'existe pas. Opération annulée pour des raisons de sécurité."
    exit 1
fi

# Créer un dossier de sauvegarde avec date
BACKUP_DIR="src_backup_$(date +%Y%m%d_%H%M%S)"
echo "Création d'une sauvegarde du dossier src dans $BACKUP_DIR..."
mkdir -p $BACKUP_DIR
cp -r src/* $BACKUP_DIR/

# Vérifier que la sauvegarde a bien été créée
if [ ! -d "$BACKUP_DIR" ] || [ ! "$(ls -A $BACKUP_DIR)" ]; then
    echo "ERREUR: La sauvegarde n'a pas été correctement créée. Opération annulée."
    exit 1
fi

echo "Sauvegarde terminée avec succès."

# Liste des éléments obsolètes à supprimer
OBSOLETE_ITEMS=(
    "src"
    "python-flask-google-oauth-login-master"  # Exemple de dossier potentiellement obsolète
    "polyline_data.txt"  # Fichier de test
    "test_polyline.py"
    "test_polyline_from_file.py"
)

# Suppression des éléments obsolètes
for item in "${OBSOLETE_ITEMS[@]}"; do
    if [ -e "$item" ]; then
        echo "Suppression de $item..."
        rm -rf "$item"
    else
        echo "$item n'existe pas, ignoré."
    fi
done

echo "Nettoyage terminé avec succès!"
echo "Une sauvegarde du dossier src a été conservée dans $BACKUP_DIR"
echo "Si l'application fonctionne correctement, vous pourrez supprimer cette sauvegarde plus tard."
