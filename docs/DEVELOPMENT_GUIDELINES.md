# KlandoDash Development Guidelines

Ce document rassemble les leçons apprises et les standards à suivre pour le développement du Dashboard Klando.

## 1. Gestion de la Performance (RAM)

Le serveur (Render) a des limites de RAM strictes. 
- **INTERDIT** : Récupérer toute une table pour faire un `.length` ou un `.reduce()` en JavaScript.
- **OBLIGATOIRE** : Utiliser des fonctions SQL (RPC) pour les agrégations complexes.
- **LIMITES** : Toujours ajouter une clause `.limit()` sur les requêtes de listes (ex: 50 ou 100 max).

## 2. Supabase & PostgREST Gotchas

### Cache du Schéma
Lorsqu'une fonction SQL ou une vue est modifiée, PostgREST ne voit pas toujours le changement immédiatement.
- **Solution** : Toujours ajouter `NOTIFY pgrst, 'reload schema';` à la fin de vos scripts de migration.

### Signatures de Fonctions
PostgreSQL supporte l'overloading (plusieurs fonctions avec le même nom mais des paramètres différents). Cela perturbe l'API Supabase.
- **Règle** : Si vous changez les paramètres d'une fonction, faites un `DROP FUNCTION` complet de l'ancienne version avant de créer la nouvelle.

### SECURITY DEFINER
Par défaut, les fonctions SQL s'exécutent avec les droits de l'utilisateur (`SECURITY INVOKER`). Le Row Level Security (RLS) peut filtrer les résultats et fausser les totaux.
- **Standard** : Pour les statistiques globales (counts, sums), utilisez `SECURITY DEFINER` pour que la fonction puisse voir toutes les données.

## 3. Disprépançes de Schéma (Transactions)

Attention à la table `transactions` :
- **Colonne réelle** : `code_service`
- **Ancienne doc / SQL Dump** : `service_code` (Erreur à éviter).

## 4. Types JSON Imbriqués

Le frontend (Next.js) attend souvent des objets JSON très profonds (ex: `stats.users.typicalProfile.gender`).
- Lors de la création d'une RPC, vérifiez toujours l'interface TypeScript correspondante (`frontend/src/lib/queries/stats/types.ts`) pour ne pas oublier de champ, ce qui provoquerait un crash de la page.

## 5. Dépannage RPC (Troubleshooting)

Si une fonction RPC retourne `0` ou une erreur :

1.  **Vérifier les droits** : Assurez-vous que `GRANT EXECUTE` est bien appliqué pour `anon` et `authenticated`.
2.  **Tester en SQL** : Exécutez `SELECT public.nom_de_la_fonction();` directement dans l'éditeur SQL de Supabase.
3.  **Vérifier le cache** : Si vous venez de modifier la fonction, exécutez `NOTIFY pgrst, 'reload schema';` pour forcer la mise à jour de l'API.
