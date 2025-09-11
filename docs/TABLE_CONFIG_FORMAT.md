# Format de Configuration des Tableaux

Ce document décrit le format JSON utilisé pour configurer les tableaux dynamiques dans KlandoDash.

## Structure Générale

```json
{
  "table_name": "nom_table_sql",
  "columns": {
    "nom_colonne": {
      // Configuration de la colonne
    }
  },
  "default_sort": {
    "column": "nom_colonne",
    "direction": "asc|desc"
  },
  "pagination": {
    "default_page_size": 5,
    "page_sizes": [5, 10, 20, 50]
  }
}
```

## Configuration des Colonnes

### Propriétés de Base

| Propriété | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `label` | string | ✅ | Nom affiché dans l'en-tête du tableau |
| `type` | string | ✅ | Type de données (voir types supportés) |
| `supabase_column` | string | ✅ | Nom de la colonne dans la base de données |
| `visible` | boolean | ✅ | Si la colonne doit être affichée |
| `sortable` | boolean | ❌ | Si la colonne peut être triée (défaut: false) |

### Types de Données Supportés

#### `string` - Texte simple
```json
{
  "label": "Nom",
  "type": "string",
  "supabase_column": "name",
  "visible": true,
  "truncate": 30  // Optionnel: tronquer à N caractères
}
```

#### `currency` - Valeur monétaire
```json
{
  "label": "Prix",
  "type": "currency",
  "supabase_column": "price",
  "unit": "FCFA",  // Unité monétaire
  "visible": true
}
```

#### `enum` - Valeur avec mapping et badge
```json
{
  "label": "Statut",
  "type": "enum",
  "supabase_column": "status",
  "values": {
    "PENDING": "En attente",
    "CONFIRMED": "Confirmé",
    "CANCELED": "Annulé"
  },
  "visible": true
}
```

#### `date` - Date uniquement
```json
{
  "label": "Date de départ",
  "type": "date",
  "supabase_column": "departure_date",
  "visible": true,
  "transform": {
    "type": "from_iso",
    "source": "departure_schedule",  // Colonne source
    "output": "date",
    "format": "%Y-%m-%d"  // Format strftime optionnel
  }
}
```

#### `time` - Heure uniquement
```json
{
  "label": "Heure de départ",
  "type": "time",
  "supabase_column": "departure_schedule",
  "visible": true,
  "transform": {
    "type": "from_iso",
    "source": "departure_schedule",
    "output": "time",
    "format": "%H:%M"
  }
}
```

#### `datetime` - Date et heure
```json
{
  "label": "Créé le",
  "type": "datetime",
  "supabase_column": "created_at",
  "visible": true,
  "transform": {
    "type": "from_iso",
    "source": "created_at",
    "output": "datetime",
    "format": "%Y-%m-%d %H:%M"
  }
}
```

#### `integer` / `number` - Valeurs numériques
```json
{
  "label": "Places disponibles",
  "type": "integer",
  "supabase_column": "seats_available",
  "visible": true
}
```

## Transformations Avancées

### `from_iso` - Parsing de timestamps ISO 8601

Transforme un timestamp ISO (ex: `2025-09-11T14:30:00+00:00`) en format lisible.

```json
{
  "transform": {
    "type": "from_iso",
    "source": "nom_colonne_source",  // Colonne contenant le timestamp
    "output": "date|time|datetime",  // Type de sortie souhaité
    "format": "%Y-%m-%d %H:%M"      // Format strftime (optionnel)
  }
}
```

### `currency` - Formatage monétaire

```json
{
  "transform": {
    "type": "currency",
    "unit": "FCFA"
  }
}
```

### `enum_badge` - Badge coloré pour énumérations

```json
{
  "transform": {
    "type": "enum_badge",
    "values": {
      "PENDING": "En attente",
      "CONFIRMED": "Confirmé"
    },
    "colors": {  // Optionnel: couleurs personnalisées
      "PENDING": "warning",
      "CONFIRMED": "success"
    }
  }
}
```

### `truncate` - Troncature de texte

```json
{
  "transform": {
    "type": "truncate",
    "max_length": 50
  }
}
```

## Validation Automatique

Le système valide automatiquement :

1. **Colonnes existantes** : Toutes les colonnes référencées doivent exister dans le schéma SQL de la table
2. **Transformations supportées** : Les types de transformation doivent être implémentés dans `DataTransformer`
3. **Cohérence des types** : Les transformations doivent être compatibles avec le type de colonne

## Exemple Complet

```json
{
  "table_name": "trips",
  "columns": {
    "trip_id": {
      "label": "ID Trajet",
      "type": "string",
      "supabase_column": "trip_id",
      "visible": true,
      "sortable": false
    },
    "departure_name": {
      "label": "Départ",
      "type": "string",
      "supabase_column": "departure_name",
      "visible": true,
      "truncate": 30
    },
    "departure_date": {
      "label": "Date de départ",
      "type": "date",
      "supabase_column": "departure_date",
      "visible": true,
      "transform": {
        "type": "from_iso",
        "source": "departure_schedule",
        "output": "date",
        "format": "%Y-%m-%d"
      }
    },
    "passenger_price": {
      "label": "Prix",
      "type": "currency",
      "supabase_column": "passenger_price",
      "unit": "FCFA",
      "visible": true
    },
    "status": {
      "label": "Statut",
      "type": "enum",
      "supabase_column": "status",
      "values": {
        "PENDING": "En attente",
        "CONFIRMED": "Confirmé",
        "CANCELED": "Annulé"
      },
      "visible": true
    }
  },
  "default_sort": {
    "column": "departure_date",
    "direction": "desc"
  },
  "pagination": {
    "default_page_size": 5,
    "page_sizes": [5, 10, 20, 50]
  }
}
```

## Ajout de Nouvelles Colonnes

1. Vérifier que la colonne existe dans le schéma SQL (`dash_apps/utils/data_definition/[table].json`)
2. Ajouter la configuration dans le JSON
3. Définir les transformations si nécessaire
4. Tester l'affichage

## Extension du Système

Pour ajouter de nouveaux types de transformation :

1. Implémenter la méthode dans `DataTransformer` (`dash_apps/utils/data_transformer.py`)
2. Enregistrer le type dans `_register_transformers()`
3. Documenter le nouveau type dans ce fichier
