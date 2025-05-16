# Klandodash - Architecture Dash Professionnelle

## Structure

- `app.py` : Point d'entrée principal Dash multipage
- `pages/` : Pages Dash (ex : trips_page)
- `components/` : Composants UI réutilisables
- `utils/` : Accès DB et helpers (à créer)
- `assets/` : Fichiers statiques (CSS, images, etc.)

## Lancer l'app

```bash
python app.py
```

## À faire
- Déplacer db_utils.py dans utils/
- Factoriser les callbacks dans callbacks/
- Ajouter d'autres pages si besoin
