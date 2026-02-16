# Diagnostic et Résolution : Statistiques Dashboard

Ce document récapitule la problématique des statistiques du dashboard Klando, les tentatives de résolution, et l'état actuel.

## 1. La Problématique Initiale
**Cause :** Le dashboard (Render) dépassait sa limite de mémoire (Memory Limit Exceeded) et redémarrait.
**Raison :** Les calculs de statistiques étaient faits en JavaScript côté serveur. Le code récupérait la **totalité** des tables `trips`, `users` et `transactions` (~1000+ lignes cumulées) pour faire des `.length` et des `.reduce()`. 
**Impact :** Consommation de RAM excessive proportionnelle au nombre d'utilisateurs.

---

## 2. Stratégie de Résolution
Passer d'un calcul "en mémoire" à un calcul "en base de données" via une fonction **RPC (Remote Procedure Call)**.
L'objectif est que Supabase renvoie juste un petit objet JSON avec les chiffres finaux (ex: `{ total_users: 672 }`) au lieu de la liste complète des membres.

---

## 3. Historique des Tentatives

### Tentative 1 : `get_dashboard_stats_optimized`
- **Action :** Création d'une fonction SQL agrégée.
- **Problème :** Affichait `0`.
- **Cause :** La sécurité RLS (Row Level Security) empêchait la fonction de voir toutes les lignes car elle s'exécutait avec les droits de l'utilisateur connecté (qui ne peut pas tout voir).

### Tentative 2 : Version `SECURITY DEFINER`
- **Action :** Ajout de `SECURITY DEFINER` pour que la fonction tourne avec les droits "admin" et ignore le RLS.
- **Problème :** Erreur SQL `column "service_code" does not exist`.
- **Confusion :** Le fichier `schema.sql` indique `service_code` mais la base de données réelle semble utiliser `code_service`.

### Tentative 3 : Versions `v2` et `v3`
- **Action :** Renommage pour éviter les conflits de cache PostgREST.
- **Problème :** Erreur `PGRST202` (Candidate function not found).
- **Cause :** PostgREST est très sensible aux signatures de fonctions (avec ou sans paramètres). Si une fonction est définie avec des paramètres optionnels, l'appel sans paramètres échoue parfois si le cache n'est pas rafraîchi.

---

## 4. État Actuel : `get_klando_stats_final`

Nous utilisons maintenant une fonction au nom unique et sans aucun paramètre pour éliminer toute ambiguïté.

### Pourquoi ça peut encore "échouer" :
1. **Cache PostgREST :** Supabase garde en mémoire l'ancienne structure de l'API. Il faut parfois forcer un rafraîchissement avec `NOTIFY pgrst, 'reload schema';`.
2. **Signature de Fonction :** Si le code appelle `rpc('ma_fonction', {})` et que la fonction est définie sans paramètres en SQL, PostgREST peut renvoyer une erreur 404/405.
3. **Permissions :** Si `GRANT EXECUTE` n'est pas appliqué à `anon` et `authenticated`, le frontend reçoit un objet vide.

---

## 5. Procédure de Rétablissement (Dernier Recours)

Si les statistiques affichent toujours `0` ou une erreur :

1. **Nettoyage SQL :**
   Exécuter `DROP FUNCTION IF EXISTS ...` pour TOUTES les versions citées plus haut dans l'éditeur SQL de Supabase.
2. **Application Unique :**
   Appliquer uniquement le script de la fonction `get_klando_stats_final`.
3. **Vérification API :**
   Tester la fonction directement dans l'éditeur SQL : `SELECT public.get_klando_stats_final();`.
   Si cela renvoie les bons chiffres en SQL mais `0` sur le site, c'est un problème de **Permissions (GRANT)**.

---

## 6. Modifications de sécurité effectuées
- Utilisation de `SECURITY DEFINER` pour garantir que les calculs de totaux sont exacts.
- Ajout de `coalesce(..., 0)` partout pour éviter que la présence d'une valeur `NULL` ne fasse planter tout l'objet JSON.
- Bridgage de la colonne `code_service` (nom réel constaté en base).
