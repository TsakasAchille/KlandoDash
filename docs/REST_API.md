# Migration vers l'API REST Supabase

## Introduction

Ce document explique l'implémentation du mode REST pour KlandoDash, qui permet d'accéder à la base de données Supabase via son API REST au lieu d'une connexion PostgreSQL directe. Cette fonctionnalité est particulièrement utile lorsque :

- La connexion PostgreSQL directe est bloquée par un pare-feu
- L'application est déployée dans un environnement où l'accès direct à la base de données n'est pas possible
- On souhaite réduire la charge sur la base de données PostgreSQL

## Architecture

L'implémentation repose sur plusieurs composants clés :

1. **SupabaseRepository** : Une classe de base qui encapsule les opérations CRUD vers l'API REST Supabase
2. **Repositories REST** : Versions REST des repositories existants (UserRepositoryRest, TripRepositoryRest, etc.)
3. **RepositoryFactory** : Une factory qui fournit le repository approprié (SQL ou REST) selon la configuration
4. **Config** : La configuration détermine le mode de connexion à utiliser

## Configuration

Pour utiliser le mode REST, vous avez plusieurs options :

### 1. Utiliser le script de démarrage en mode REST

Le script `start_rest_mode.sh` configure automatiquement l'environnement pour utiliser l'API REST :

```bash
./start_rest_mode.sh
```

### 2. Configuration manuelle

Vous pouvez configurer l'application via les variables d'environnement :

```bash
export CONNECTION_MODE="rest"
export FORCE_REST_API="true"
export SUPABASE_URL="https://votre-projet.supabase.co"
export SUPABASE_KEY="votre-clé-anon"
python3 app.py
```

### 3. Fichier `.env`

Vous pouvez également configurer ces paramètres dans le fichier `.env` :

```
CONNECTION_MODE=rest
FORCE_REST_API=true
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre-clé-anon
```

## Utilisation dans le code

Pour utiliser les repositories REST dans votre code :

### Avec la Factory (recommandé)

```python
from dash_apps.repositories.repository_factory import RepositoryFactory

# La factory retourne automatiquement le bon repository selon la configuration
user_repo = RepositoryFactory.get_user_repository()
trips = user_repo.get_all_trips()
```

### Utilisation directe des repositories REST

```python
from dash_apps.repositories.user_repository_rest import UserRepositoryRest

user_repo = UserRepositoryRest()
users = user_repo.get_all_users()
```

## Mode automatique

Le mode `CONNECTION_MODE=auto` (par défaut) permet à l'application de basculer automatiquement :

1. Elle essaie d'abord d'utiliser la connexion PostgreSQL directe
2. Si celle-ci échoue et que les identifiants Supabase sont disponibles, elle bascule vers l'API REST
3. En dernier recours, elle utilise SQLite (pour les environnements de développement)

## Standardisation vers l'API REST

Afin d'améliorer la portabilité et la fiabilité de l'application, nous avons standardisé certains modules pour utiliser exclusivement l'API REST :

1. **Module Utilisateurs** : Entièrement migré pour utiliser l'API REST Supabase
   - `UsersCacheService` utilise directement `data_schema_rest`
   - Les panneaux de profil, statistiques et trajets utilisent l'API REST

2. **Module Tickets Support** : Utilise l'API REST via le repository factory

3. **Modules en cours de migration** :
   - Module Trajets
   - Module Validations conducteurs

## Limitations de l'API REST

- Certaines requêtes complexes avec jointures multiples sont plus difficiles à exprimer avec l'API REST
- Les filtres complexes sont appliqués en post-traitement côté client
- La performance peut être légèrement inférieure à celle d'une connexion PostgreSQL directe

## Tests

Pour tester spécifiquement les repositories REST :

```bash
python3 test_repositories_rest.py
```

Ce script vérifie que tous les repositories REST fonctionnent correctement avec l'API Supabase.
