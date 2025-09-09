#!/usr/bin/env python3
"""
Script pour appliquer la correction de la carte
"""

import os
import shutil
from pathlib import Path

def apply_fallback_solution():
    """Applique la solution de fallback en modifiant la configuration"""
    print("=== APPLICATION DE LA SOLUTION FALLBACK ===")
    
    # Chemins
    project_root = Path(__file__).parent
    env_file = project_root / '.env'
    fallback_style = project_root / 'fallback_map_style.json'
    
    if not fallback_style.exists():
        print("❌ Fichier fallback_map_style.json non trouvé")
        return False
    
    # Lire le fichier .env
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return False
    
    # Backup du .env original
    backup_file = project_root / '.env.backup'
    shutil.copy2(env_file, backup_file)
    print(f"✅ Backup créé: {backup_file}")
    
    # Lire le contenu actuel
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Modifier la ligne MAPLIBRE_STYLE_URL
    new_lines = []
    maplibre_updated = False
    
    for line in lines:
        if line.startswith('MAPLIBRE_STYLE_URL='):
            # Commenter l'ancienne ligne et ajouter la nouvelle
            new_lines.append(f"# {line}")
            new_lines.append(f"MAPLIBRE_STYLE_URL=https://demotiles.maplibre.org/globe.json\n")
            maplibre_updated = True
            print("✅ MAPLIBRE_STYLE_URL mise à jour vers le style de démonstration")
        else:
            new_lines.append(line)
    
    # Si la variable n'existait pas, l'ajouter
    if not maplibre_updated:
        new_lines.append("MAPLIBRE_STYLE_URL=https://demotiles.maplibre.org/globe.json\n")
        print("✅ MAPLIBRE_STYLE_URL ajoutée")
    
    # Écrire le nouveau fichier
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Configuration mise à jour")
    return True

def apply_local_style_solution():
    """Applique la solution avec le style local"""
    print("\n=== APPLICATION DE LA SOLUTION STYLE LOCAL ===")
    
    # Chemins
    project_root = Path(__file__).parent
    env_file = project_root / '.env'
    static_dir = project_root / 'dash_apps' / 'assets'
    fallback_style = project_root / 'fallback_map_style.json'
    
    # Créer le répertoire assets s'il n'existe pas
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Copier le style dans assets
    target_style = static_dir / 'map_style.json'
    shutil.copy2(fallback_style, target_style)
    print(f"✅ Style copié vers: {target_style}")
    
    # Modifier le .env pour pointer vers le fichier local
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return False
    
    # Lire le contenu actuel
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Modifier la ligne MAPLIBRE_STYLE_URL
    new_lines = []
    maplibre_updated = False
    
    for line in lines:
        if line.startswith('MAPLIBRE_STYLE_URL='):
            # Commenter l'ancienne ligne et ajouter la nouvelle
            new_lines.append(f"# {line}")
            new_lines.append(f"MAPLIBRE_STYLE_URL=/assets/map_style.json\n")
            maplibre_updated = True
            print("✅ MAPLIBRE_STYLE_URL mise à jour vers le style local")
        else:
            new_lines.append(line)
    
    # Si la variable n'existait pas, l'ajouter
    if not maplibre_updated:
        new_lines.append("MAPLIBRE_STYLE_URL=/assets/map_style.json\n")
        print("✅ MAPLIBRE_STYLE_URL ajoutée")
    
    # Écrire le nouveau fichier
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Configuration mise à jour avec style local")
    return True

def restore_original_config():
    """Restaure la configuration originale"""
    print("\n=== RESTAURATION DE LA CONFIGURATION ORIGINALE ===")
    
    project_root = Path(__file__).parent
    env_file = project_root / '.env'
    backup_file = project_root / '.env.backup'
    
    if backup_file.exists():
        shutil.copy2(backup_file, env_file)
        print("✅ Configuration originale restaurée")
        return True
    else:
        print("❌ Aucun backup trouvé")
        return False

def main():
    print("🗺️  CORRECTION DE LA CARTE MAPLIBRE")
    print("=" * 50)
    
    print("\nOptions disponibles:")
    print("1. Utiliser le style de démonstration MapLibre (recommandé)")
    print("2. Utiliser un style local personnalisé")
    print("3. Restaurer la configuration originale")
    print("4. Quitter")
    
    choice = input("\nChoisissez une option (1-4): ").strip()
    
    if choice == "1":
        if apply_fallback_solution():
            print("\n✅ Solution appliquée avec succès!")
            print("🔄 Redémarrez l'application pour voir les changements")
    elif choice == "2":
        if apply_local_style_solution():
            print("\n✅ Solution locale appliquée avec succès!")
            print("🔄 Redémarrez l'application pour voir les changements")
    elif choice == "3":
        if restore_original_config():
            print("\n✅ Configuration originale restaurée!")
            print("🔄 Redémarrez l'application")
    elif choice == "4":
        print("👋 Au revoir!")
    else:
        print("❌ Option invalide")

if __name__ == "__main__":
    main()
