# Architecture mise u00e0 jour

L'architecture de l'application a u00e9tu00e9 mise u00e0 jour pour utiliser PostgreSQL directement via SQLAlchemy.

## Fichiers du00e9pru00e9ciu00e9s

- `data_manager.py` - N'est plus utilisu00e9 car nous accu00e9dons directement u00e0 PostgreSQL
- `subscribers/` - Ces fichiers sont conservu00e9s u00e0 titre de ru00e9fu00e9rence historique

## Architecture actuelle

- `processors/` - Contient les processeurs qui accu00e8dent directement u00e0 PostgreSQL et mettent en cache les donnu00e9es avec Streamlit
- `core/database.py` - Contient les modu00e8les ORM SQLAlchemy et la connexion u00e0 la base de donnu00e9es

Les processeurs utilisent le cache Streamlit (`@st.cache_data`) pour u00e9viter les requu00eates ru00e9pu00e9titives u00e0 la base de donnu00e9es et amu00e9liorer les performances.
