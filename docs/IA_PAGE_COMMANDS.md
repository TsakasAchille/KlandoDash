# Guide d'Automatisation : Klando IA Data Hub

Ce document liste les commandes et sélecteurs JavaScript que vous (l'IA) devez utiliser pour interagir avec le tableau de bord Klando, en contournant les lenteurs potentielles de l'interface graphique (notamment sur des appareils lents comme un Raspberry Pi 4).

## 1. Recherche de Conducteurs (Auto-Search)

**La méthode recommandée** est de passer les paramètres directement dans l'URL. Cela évite d'avoir à remplir les champs manuellement.

*   **URL de base :** `https://[DOMAINE_KLANDO]/ia`
*   **Format avec paramètres :** `https://[DOMAINE_KLANDO]/ia?origin=[VILLE_DEPART]&dest=[VILLE_ARRIVEE]`
*   **Exemple :** `https://klandodash.onrender.com/ia?origin=Dakar&dest=Thies`

Dès que la page charge avec ces paramètres, la recherche est déclenchée automatiquement.

Si vous devez le faire **manuellement via JavaScript (evaluate)** :
```javascript
document.getElementById('ia-search-origin').value = 'Dakar';
document.getElementById('ia-search-dest').value = 'Thiès';
document.getElementById('ia-search-button').click();
```

## 2. Sélection d'un Conducteur

Une fois la recherche terminée, les conducteurs apparaissent dans une liste. Vous pouvez sélectionner un conducteur spécifique si vous connaissez son ID unique (`uid`).

*   **Commande JS :**
```javascript
document.getElementById('ia-select-driver-[UID_DU_CONDUCTEUR]').click();
```

## 3. Ajout d'une Preuve Visuelle (Capture d'écran Facebook)

Pour joindre un screenshot (ex: demande d'un client sur un groupe Facebook) au brouillon, vous devez utiliser le pont Base64 invisible spécialement conçu pour l'IA. 

**IMPORTANT : Ne déclenchez pas d'événements de frappe (typing), modifiez le DOM directement et cliquez sur le bouton d'upload caché.**

*   **Étape 1 :** Injecter le Base64 dans le textarea caché.
*   **Étape 2 :** Cliquer sur le bouton caché pour forcer l'upload vers Supabase.

*   **Commande JS :**
```javascript
// 1. Injecter l'image (doit commencer par "data:image/png;base64,...")
document.getElementById('ia-image-base64').value = 'data:image/png;base64,iVBORw0KGgoAAAAN...';

// 2. Déclencher l'upload
document.getElementById('ia-image-upload-button').click();
```
*Attendez quelques secondes après cette commande pour que l'image soit uploadée avant de sauvegarder le brouillon final.*

## 4. Création du Brouillon (Proposition)

Si vous avez sélectionné un conducteur via l'interface, le champ cible est déjà rempli. Sinon (mode manuel/global), vous pouvez remplir les champs directement.

Le système est "blindé" : même si React ne détecte pas le changement, le clic sur le bouton ira lire directement la valeur dans le HTML.

*   **IDs des champs :**
    *   `ia-contact-target` : L'ID de l'utilisateur, son email, ou le mot "GLOBAL".
    *   `ia-contact-subject` : L'objet stratégique de la proposition.
    *   `ia-contact-message` : Le contenu du message.
    *   `ia-create-draft-button` : Le bouton pour finaliser et envoyer au Centre Éditorial.

*   **Commande JS complète :**
```javascript
document.getElementById('ia-contact-target').value = 'GLOBAL'; // Ou un ID/Email
document.getElementById('ia-contact-subject').value = 'Forte demande sur l'axe Dakar-Thiès';
document.getElementById('ia-contact-message').value = 'Bonjour, au vu de la capture ci-jointe, il y a une forte demande aujourd'hui...';

// Soumettre le formulaire
document.getElementById('ia-create-draft-button').click();
```

## Résumé du Workflow IA Optimal

1. Ouvrir l'URL avec `?origin=...&dest=...`
2. Si une capture existe : Injecter le Base64 dans `ia-image-base64` et cliquer sur `ia-image-upload-button`.
3. Remplir le message dans `ia-contact-message` et l'objet dans `ia-contact-subject`.
4. Cliquer sur `ia-create-draft-button`.
5. Fin de l'opération (le message part en relecture dans le Centre Éditorial).
